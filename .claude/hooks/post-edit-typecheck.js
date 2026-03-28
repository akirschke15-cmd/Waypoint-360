#!/usr/bin/env node
/**
 * Post-Edit TypeCheck Hook
 *
 * Runs type checking and syntax validation after file edits.
 * Supports TypeScript, Python, and Terraform.
 */

'use strict';

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const MAX_STDIN = 1024 * 1024;
let rawInput = '';

function log(msg) {
  process.stderr.write(`${msg}\n`);
}

function findTsConfig(dir) {
  const root = path.parse(dir).root;
  let current = dir;
  let depth = 0;

  while (current !== root && depth < 20) {
    if (fs.existsSync(path.join(current, 'tsconfig.json'))) {
      return current;
    }
    current = path.dirname(current);
    depth++;
  }

  return null;
}

function runTypeCheck(filePath) {
  if (!filePath || !fs.existsSync(filePath)) {
    return;
  }

  const ext = path.extname(filePath).toLowerCase();

  if (['.ts', '.tsx'].includes(ext)) {
    const dir = findTsConfig(path.dirname(filePath));
    if (dir) {
      try {
        const npxBin = process.platform === 'win32' ? 'npx.cmd' : 'npx';
        execSync(`${npxBin} tsc --noEmit --pretty false`, {
          cwd: dir,
          stdio: 'pipe',
          timeout: 30000
        });
      } catch (err) {
        const output = (err.stdout || '') + (err.stderr || '');
        const lines = output.split('\n').filter(line => {
          return line.includes(filePath) ||
                 line.includes(path.basename(filePath)) ||
                 line.includes(path.relative(dir, filePath));
        }).slice(0, 10);

        if (lines.length > 0) {
          log(`[TypeCheck] Errors in ${path.basename(filePath)}:`);
          lines.forEach(line => log(line));
        }
      }
    }
    return;
  }

  if (ext === '.py') {
    try {
      execSync(`python -m py_compile "${filePath}"`, {
        stdio: 'pipe',
        timeout: 10000
      });
    } catch (err) {
      log(`[TypeCheck] Syntax error in ${path.basename(filePath)}`);
    }
    return;
  }

  if (ext === '.tf') {
    try {
      execSync('terraform validate', {
        cwd: path.dirname(filePath),
        stdio: 'pipe',
        timeout: 15000
      });
    } catch (err) {
      log(`[TypeCheck] Terraform validation failed for ${path.basename(filePath)}`);
    }
    return;
  }
}

function main() {
  process.stdin.setEncoding('utf8');

  process.stdin.on('data', chunk => {
    if (rawInput.length < MAX_STDIN) {
      const remaining = MAX_STDIN - rawInput.length;
      rawInput += chunk.substring(0, remaining);
    }
  });

  process.stdin.on('end', () => {
    try {
      const input = JSON.parse(rawInput);
      const filePath = input.tool_input?.file_path;
      runTypeCheck(filePath);
    } catch {
      // Pass through on error
    }

    process.stdout.write(rawInput);
    process.exit(0);
  });
}

main();
