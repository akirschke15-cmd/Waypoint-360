#!/usr/bin/env node
/**
 * Skill Activation Hook
 *
 * Auto-loads skills based on file context and user prompt.
 * Reads file patterns and keywords to suggest relevant skills.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const { globSync } = require('glob');

const MAX_STDIN = 1024 * 1024;
let rawInput = '';

function log(msg) {
  process.stderr.write(`${msg}\n`);
}

function getFileContext() {
  try {
    const files = globSync('**/*', {
      cwd: process.cwd(),
      ignore: ['node_modules/**', '.git/**', 'dist/**', 'build/**'],
      maxDepth: 2
    });
    return files.slice(0, 20);
  } catch {
    return [];
  }
}

function checkSkill(userPrompt, fileContext, patterns) {
  const promptLower = userPrompt.toLowerCase();

  for (const pattern of patterns) {
    const regex = new RegExp(pattern, 'i');
    if (regex.test(promptLower)) {
      return true;
    }
  }

  for (const file of fileContext) {
    const fileName = file.toLowerCase();
    for (const pattern of patterns) {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(fileName)) {
        return true;
      }
    }
  }

  return false;
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

    const fileContext = getFileContext();
    const matchedSkills = [];

    // Python development
    if (checkSkill(userPrompt, fileContext, [
      'python',
      'pytest',
      'django',
      'flask',
      'fastapi',
      'pip',
      '\\.py$',
      'requirements\\.txt',
      'pyproject\\.toml'
    ])) {
      matchedSkills.push('python-development');
    }

    // TypeScript development
    if (checkSkill(userPrompt, fileContext, [
      'typescript',
      'javascript',
      'react',
      'vue',
      'angular',
      'node',
      'npm',
      '\\.tsx?$',
      '\\.jsx?$',
      'package\\.json',
      'tsconfig\\.json'
    ])) {
      matchedSkills.push('typescript-development');
    }

    // Terraform
    if (checkSkill(userPrompt, fileContext, [
      'terraform',
      'infrastructure',
      'aws',
      'azure',
      'gcp',
      '\\.tf$',
      '\\.tfvars$'
    ])) {
      matchedSkills.push('terraform-infrastructure');
    }

    // Testing
    if (checkSkill(userPrompt, fileContext, [
      'test',
      'testing',
      'jest',
      'vitest',
      'pytest',
      'coverage',
      'spec',
      'test.*\\.(py|ts|js)',
      'spec\\.(ts|js)'
    ])) {
      matchedSkills.push('testing-best-practices');
    }

    const uniqueSkills = [...new Set(matchedSkills)];

    if (uniqueSkills.length > 0 && uniqueSkills.length <= 3) {
      process.stderr.write('\n');
      process.stderr.write(`AUTO-LOADED SKILLS: ${uniqueSkills.join(', ')}\n`);
      process.stderr.write('\n');
    }

    process.stdout.write(rawInput);
    process.exit(0);
  });
}

main();
