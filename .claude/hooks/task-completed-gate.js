#!/usr/bin/env node
/**
 * Task Completed Gate Hook
 *
 * Runs test, syntax, and secret scan gates before task completion.
 * Exit code 2 = reject, 0 = accept.
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

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function runGate(name, command, args) {
  try {
    execSync(`${command} ${args.join(' ')}`, {
      stdio: 'pipe',
      timeout: 60000
    });
    return null;
  } catch (err) {
    return `${name}: ${(err.stdout || '').split('\n').slice(0, 3).join(' | ')}`;
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
    let input = {};

    try {
      input = JSON.parse(rawInput);
    } catch {
      // Pass through on error
    }

    const timestamp = new Date().toISOString();
    const logDir = path.join(process.cwd(), '.claude', 'logs', 'teams');
    ensureDir(logDir);

    const taskDesc = input.task_description || 'unknown';
    const teammateName = input.teammate_name || 'unknown';
    const failures = [];

    // Gate 1: Python tests
    if (fs.existsSync('pyproject.toml')) {
      const err = runGate('Python tests', 'python', ['-m', 'pytest', '--tb=short', '--quiet']);
      if (err) failures.push(err);
    }

    // Gate 2: JS/TS tests
    if (fs.existsSync('package.json')) {
      try {
        const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
        if (pkg.scripts && pkg.scripts.test) {
          const err = runGate('JS/TS tests', 'npm', ['test']);
          if (err) failures.push(err);
        }
      } catch {
        // Ignore
      }
    }

    // Gate 3: Syntax check for modified files
    try {
      const modifiedFiles = execSync('git diff --name-only HEAD 2>/dev/null', {
        encoding: 'utf8'
      }).split('\n').filter(Boolean);

      modifiedFiles.forEach(file => {
        if (file.endsWith('.py')) {
          const err = runGate(`Syntax ${file}`, 'python', ['-m', 'py_compile', file]);
          if (err) failures.push(err);
        }
      });
    } catch {
      // Ignore git errors
    }

    // Gate 4: Secret scan
    const secretPatterns = [
      'AKIA[A-Z0-9]{16}',
      'sk-[a-zA-Z0-9]{20,}',
      '-----BEGIN (RSA |EC )?PRIVATE KEY-----'
    ];

    try {
      const diff = execSync('git diff HEAD -- . 2>/dev/null', {
        encoding: 'utf8'
      });

      secretPatterns.forEach(pattern => {
        const regex = new RegExp(pattern);
        if (regex.test(diff)) {
          failures.push(`Secret scan: Potential secret detected matching ${pattern}`);
        }
      });
    } catch {
      // Ignore
    }

    const logEntry = {
      timestamp,
      event: 'TaskCompleted',
      teammate_name: teammateName,
      task: taskDesc,
      passed: failures.length === 0,
      failures
    };

    fs.appendFileSync(
      path.join(logDir, 'team-activity.jsonl'),
      JSON.stringify(logEntry) + '\n'
    );

    if (failures.length > 0) {
      log('Task completion blocked. Fix before marking done:');
      failures.forEach(f => log(`  - ${f}`));
      process.exit(2);
    }

    log(`Task '${taskDesc}' completed by '${teammateName}' - all gates passed.`);
    process.exit(0);
  });
}

main();
