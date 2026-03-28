#!/usr/bin/env node
/**
 * Agent Activation Hook
 *
 * Reads stdin JSON input, scores user prompt against agent rules,
 * outputs dispatch directive to stdout.
 *
 * Reads agent-rules.json to determine agent suggestions based on keywords.
 */

'use strict';

const fs = require('fs');
const path = require('path');

const MAX_STDIN = 1024 * 1024;
let rawInput = '';

const MAX_DISPATCHED = 3;

function log(msg) {
  process.stderr.write(`${msg}\n`);
}

function readAgentRules() {
  const rulesPath = path.join(process.cwd(), '.claude', 'agent-rules.json');
  try {
    if (fs.existsSync(rulesPath)) {
      return JSON.parse(fs.readFileSync(rulesPath, 'utf8'));
    }
  } catch (err) {
    log(`[AgentActivation] Failed to read agent-rules.json: ${err.message}`);
  }
  return { taskAgents: {}, keywords: {} };
}

function detectTaskNumbers(prompt) {
  const matches = prompt.match(/tasks?\s*(\d{1,3})(?:\s*[-–to]+\s*(\d{1,3}))?/gi) || [];
  const numbers = [];

  matches.forEach(m => {
    const parts = m.match(/\d+/g);
    if (parts) {
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : start;
      for (let i = start; i <= end; i++) {
        numbers.push(i.toString().padStart(3, '0'));
      }
    }
  });

  return numbers;
}

function scoreKeywords(prompt, rules) {
  const dispatchAgents = [];
  const promptLower = prompt.toLowerCase();

  if (!rules.keywords) {
    return dispatchAgents;
  }

  Object.keys(rules.keywords).forEach(agent => {
    const patterns = rules.keywords[agent];
    if (Array.isArray(patterns)) {
      const matched = patterns.some(pattern => {
        const regex = new RegExp(pattern, 'i');
        return regex.test(promptLower);
      });
      if (matched) {
        dispatchAgents.push(agent);
      }
    }
  });

  return dispatchAgents;
}

function dedup(arr) {
  return [...new Set(arr)].slice(0, MAX_DISPATCHED);
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
    let userPrompt = '';

    try {
      input = JSON.parse(rawInput);
      userPrompt = input.user_message || '';
    } catch {
      // Pass through on parse error
    }

    const rules = readAgentRules();
    let dispatchAgents = [];

    // Attempt task number detection first
    const taskNumbers = detectTaskNumbers(userPrompt);
    if (taskNumbers.length > 0 && rules.taskAgents) {
      taskNumbers.forEach(num => {
        if (rules.taskAgents[num]) {
          dispatchAgents.push(rules.taskAgents[num]);
        }
      });
    }

    // Fallback to keyword detection
    if (dispatchAgents.length === 0) {
      dispatchAgents = scoreKeywords(userPrompt, rules);
    }

    // Auto-append code-reviewer for implementation verbs
    if (/(?:complete|implement|build|create|write|add|ship|wire.up)\s+(task|feature|endpoint|component|page|route|module|service)/i.test(userPrompt)) {
      if (!dispatchAgents.includes('code-reviewer')) {
        dispatchAgents.push('code-reviewer');
      }
    }

    const uniqueAgents = dedup(dispatchAgents);

    if (uniqueAgents.length > 0) {
      process.stderr.write('\n');
      process.stderr.write(`DISPATCH AGENTS: ${uniqueAgents.join(', ')}\n`);
      process.stderr.write('Launch these agents via Task(subagent_type=...) for complex work.\n');
      process.stderr.write('See .claude/docs/00-AGENT-ROUTING.md for routing table.\n');
      process.stderr.write('\n');
    }

    process.stdout.write(rawInput);
    process.exit(0);
  });
}

main();
