#!/usr/bin/env node
/**
 * Post-Edit Quality Gate Hook
 *
 * Runs lightweight quality checks after file edits.
 * Uses prettier, biome, or ruff depending on availability.
 */

'use strict';

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const MAX_STDIN = 1024 * 1024;
let rawInput = '';

function log(msg) {
  process.stderr.write(`${msg}\n`);
}

function run(command, args, cwd = process.cwd()) {
  return spawnSync(command, args, {
    cwd,
    encoding: 'utf8',
    env: process.env
  });
}

function maybeRunQualityGate(filePath) {
  if (!filePath || !fs.existsSync(filePath)) {
    return;
  }

  const ext = path.extname(filePath).toLowerCase();
  const fix = String(process.env.QUALITY_GATE_FIX || '').toLowerCase() === 'true';
  const strict = String(process.env.QUALITY_GATE_STRICT || '').toLowerCase() === 'true';

  if (['.ts', '.tsx', '.js', '.jsx', '.json', '.md'].includes(ext)) {
    // Prefer biome if present
    if (fs.existsSync(path.join(process.cwd(), 'biome.json')) ||
        fs.existsSync(path.join(process.cwd(), 'biome.jsonc'))) {
      const args = ['biome', 'check', filePath];
      if (fix) args.push('--write');
      const result = run('npx', args);
      if (result.status !== 0 && strict) {
        log(`[QualityGate] Biome check failed for ${filePath}`);
      }
      return;
    }

    // Fallback to prettier
    const prettierArgs = ['prettier', '--check', filePath];
    if (fix) {
      prettierArgs[1] = '--write';
    }
    const prettier = run('npx', prettierArgs);
    if (prettier.status !== 0 && strict) {
      log(`[QualityGate] Prettier check failed for ${filePath}`);
    }
    return;
  }

  if (ext === '.go' && fix) {
    run('gofmt', ['-w', filePath]);
    return;
  }

  if (ext === '.py') {
    const args = ['format'];
    if (!fix) args.push('--check');
    args.push(filePath);
    const r = run('ruff', args);
    if (r.status !== 0 && strict) {
      log(`[QualityGate] Ruff check failed for ${filePath}`);
    }
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
      const filePath = String(input.tool_input?.file_path || '');
      maybeRunQualityGate(filePath);
    } catch {
      // Ignore parse errors
    }

    process.stdout.write(rawInput);
    process.exit(0);
  });
}

main();
