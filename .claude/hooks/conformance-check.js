#!/usr/bin/env node
/**
 * Conformance Check Hook
 *
 * Reminds to verify requirement conformance after file writes.
 * Behavior changes based on BOILER_MODE (strict = mandatory, lean = advisory).
 */

'use strict';

const fs = require('fs');
const path = require('path');

const MAX_STDIN = 1024 * 1024;
let rawInput = '';

function log(msg) {
  process.stderr.write(`${msg}\n`);
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

    const toolName = input.tool_name || '';
    const boilerMode = process.env.BOILER_MODE || 'lean';

    // Check if framework file exists
    const frameworkPath = path.join(process.cwd(), '.claude', 'REQUIREMENT-CONFORMANCE-FRAMEWORK.md');
    const hasFramework = fs.existsSync(frameworkPath);

    if ((toolName === 'Write' || toolName === 'Edit') && hasFramework) {
      if (boilerMode === 'strict') {
        log('CONFORMANCE: Verify requirement conformance before marking complete.');
      } else {
        log('REMINDER: Consider checking requirement conformance.');
      }
    }

    process.stdout.write(rawInput);
    process.exit(0);
  });
}

main();
