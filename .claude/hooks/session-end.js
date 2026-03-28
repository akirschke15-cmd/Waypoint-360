#!/usr/bin/env node
/**
 * Session End Hook
 *
 * Persists session state before closing.
 */

'use strict';

const fs = require('fs');
const path = require('path');

function log(msg) {
  process.stderr.write(`${msg}\n`);
}

function main() {
  const homeDir = process.env.HOME || process.env.USERPROFILE;
  if (!homeDir) {
    process.exit(0);
  }

  const logDir = path.join(homeDir, '.claude-code', 'sessions');
  const timestamp = new Date().toISOString();
  const sessionFile = path.join(logDir, `${timestamp}-session.tmp`);

  try {
    fs.mkdirSync(logDir, { recursive: true });

    const sessionData = {
      timestamp,
      event: 'SessionEnd'
    };

    fs.writeFileSync(sessionFile, JSON.stringify(sessionData, null, 2) + '\n');
    log(`[SessionEnd] Session state saved to ${sessionFile}`);
  } catch (err) {
    log(`[SessionEnd] Failed to save session: ${err.message}`);
  }

  process.exit(0);
}

main();
