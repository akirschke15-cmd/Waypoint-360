#!/usr/bin/env node
/**
 * Session Start Hook
 *
 * Loads previous session context and project detection on new session start.
 */

'use strict';

const fs = require('fs');
const path = require('path');

function log(msg) {
  process.stderr.write(`${msg}\n`);
}

function output(msg) {
  process.stdout.write(`${msg}\n`);
}

function findFiles(dir, pattern, maxAge = 7) {
  if (!fs.existsSync(dir)) {
    return [];
  }

  const now = Date.now();
  const maxAgeMs = maxAge * 24 * 60 * 60 * 1000;
  const files = [];

  try {
    const entries = fs.readdirSync(dir);
    entries.forEach(entry => {
      if (new RegExp(pattern).test(entry)) {
        const fullPath = path.join(dir, entry);
        const stat = fs.statSync(fullPath);
        if (now - stat.mtimeMs < maxAgeMs) {
          files.push({
            path: fullPath,
            mtime: stat.mtimeMs
          });
        }
      }
    });
  } catch (err) {
    log(`[SessionStart] Error reading directory: ${err.message}`);
  }

  files.sort((a, b) => b.mtime - a.mtime);
  return files;
}

function detectProjectType() {
  const languages = [];
  const frameworks = [];

  if (fs.existsSync('package.json')) {
    languages.push('JavaScript');
    const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    const deps = Object.keys({ ...pkg.dependencies, ...pkg.devDependencies });
    if (deps.some(d => /react/.test(d))) frameworks.push('React');
    if (deps.some(d => /next/.test(d))) frameworks.push('Next.js');
    if (deps.some(d => /typescript/.test(d))) languages.push('TypeScript');
  }

  if (fs.existsSync('pyproject.toml') || fs.existsSync('requirements.txt')) {
    languages.push('Python');
    if (fs.existsSync('pyproject.toml')) {
      const content = fs.readFileSync('pyproject.toml', 'utf8');
      if (/django/.test(content)) frameworks.push('Django');
      if (/fastapi/.test(content)) frameworks.push('FastAPI');
      if (/flask/.test(content)) frameworks.push('Flask');
    }
  }

  if (fs.existsSync('tsconfig.json')) {
    languages.push('TypeScript');
  }

  if (fs.existsSync('go.mod')) {
    languages.push('Go');
  }

  if (fs.existsSync('Cargo.toml')) {
    languages.push('Rust');
  }

  if (fs.existsSync('main.tf') || fs.existsSync('variables.tf')) {
    languages.push('Terraform');
  }

  return {
    languages: [...new Set(languages)],
    frameworks: [...new Set(frameworks)]
  };
}

function main() {
  const homeDir = process.env.HOME || process.env.USERPROFILE || os.homedir();
  const sessionsDir = path.join(homeDir, '.claude-code', 'sessions');
  const learnedDir = path.join(homeDir, '.claude-code', 'skills');

  // Ensure directories exist
  [sessionsDir, learnedDir].forEach(dir => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  });

  // Check for recent sessions
  const recentSessions = findFiles(sessionsDir, '.*-session\\.tmp$', 7);

  if (recentSessions.length > 0) {
    const latest = recentSessions[0];
    log(`[SessionStart] Found ${recentSessions.length} recent session(s)`);
    log(`[SessionStart] Latest: ${latest.path}`);

    try {
      const content = fs.readFileSync(latest.path, 'utf8');
      if (!content.includes('[Session context goes here]')) {
        output(`Previous session summary:\n${content}`);
      }
    } catch (err) {
      log(`[SessionStart] Failed to read session: ${err.message}`);
    }
  }

  // Check for learned skills
  const learnedSkills = findFiles(learnedDir, '.*\\.md$');
  if (learnedSkills.length > 0) {
    log(`[SessionStart] ${learnedSkills.length} learned skill(s) available`);
  }

  // Detect project type
  const projectInfo = detectProjectType();
  if (projectInfo.languages.length > 0 || projectInfo.frameworks.length > 0) {
    const parts = [];
    if (projectInfo.languages.length > 0) {
      parts.push(`languages: ${projectInfo.languages.join(', ')}`);
    }
    if (projectInfo.frameworks.length > 0) {
      parts.push(`frameworks: ${projectInfo.frameworks.join(', ')}`);
    }
    log(`[SessionStart] Project detected -- ${parts.join('; ')}`);
    output(`Project type: ${JSON.stringify(projectInfo)}`);
  } else {
    log('[SessionStart] No specific project type detected');
  }

  process.exit(0);
}

main();
