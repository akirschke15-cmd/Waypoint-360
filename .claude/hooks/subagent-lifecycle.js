#!/usr/bin/env node
/**
 * Subagent Lifecycle Hook
 *
 * Logs agent spawn and completion events.
 */

'use strict';

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

    const logDir = path.join(process.cwd(), '.claude', 'logs', 'agents');
    ensureDir(logDir);

    const timestamp = new Date().toISOString();
    const event = input.event || 'unknown';
    const agentType = input.subagent_type || 'unknown';
    const taskId = input.task_id || 'unknown';

    const logEntry = {
      timestamp,
      event,
      agent_type: agentType,
      task_id: taskId
    };

    const logFile = path.join(logDir, 'agent-activity.jsonl');
    fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n');

    if (event === 'SubagentStart') {
      log(`[SubagentLifecycle] Started ${agentType} for task ${taskId}`);
    } else if (event === 'SubagentEnd') {
      log(`[SubagentLifecycle] Completed ${agentType} for task ${taskId}`);
    }

    process.stdout.write(rawInput);
    process.exit(0);
  });
}

main();
