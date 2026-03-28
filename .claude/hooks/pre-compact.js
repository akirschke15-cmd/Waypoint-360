#!/usr/bin/env node
/**
 * Pre-Compact Hook
 *
 * Saves context state before session compaction.
 */

'use strict';

const fs = require('fs');
const path = require('path');

function log(msg) {
  process.stderr.write(`${msg}\n`);
}

function main() {
  const stateDir = path.join(process.cwd(), '.claude', 'state');

  try {
    fs.mkdirSync(stateDir, { recursive: true });

    const timestamp = new Date().toISOString();
    const compactFile = path.join(stateDir, `compact-${timestamp}.json`);

    const state = {
      timestamp,
      event: 'PreCompact',
      cwd: process.cwd()
    };

    fs.writeFileSync(compactFile, JSON.stringify(state, null, 2) + '\n');
    log(`[PreCompact] State saved to ${compactFile}`);
  } catch (err) {
    log(`[PreCompact] Failed to save state: ${err.message}`);
  }

  process.exit(0);
}

main();
