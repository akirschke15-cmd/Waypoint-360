# Boiler 4.0 Project Initialization Script (PowerShell)
# Usage: .\scripts\init-project.ps1 -ProjectName <name> -ProjectDescription <desc> -TargetUsers <users> [-Mode <strict|lean>]

param(
    [Parameter(Mandatory=$true, HelpMessage="Name of the project")]
    [string]$ProjectName,

    [Parameter(Mandatory=$true, HelpMessage="Brief description of the project")]
    [string]$ProjectDescription,

    [Parameter(Mandatory=$true, HelpMessage="Target users for this project")]
    [string]$TargetUsers,

    [Parameter(Mandatory=$false, HelpMessage="Boiler mode: strict or lean")]
    [ValidateSet("strict", "lean")]
    [string]$Mode = "strict"
)

# Set strict error handling
$ErrorActionPreference = "Stop"

# Color codes for output
$colors = @{
    "info"    = "Cyan"
    "success" = "Green"
    "error"   = "Red"
    "warn"    = "Yellow"
}

# Function to print colored output
function Write-Info {
    param([string]$message)
    Write-Host "[INFO] $message" -ForegroundColor $colors["info"]
}

function Write-Success {
    param([string]$message)
    Write-Host "[SUCCESS] $message" -ForegroundColor $colors["success"]
}

function Write-Error-Custom {
    param([string]$message)
    Write-Host "[ERROR] $message" -ForegroundColor $colors["error"]
}

function Write-Warn {
    param([string]$message)
    Write-Host "[WARN] $message" -ForegroundColor $colors["warn"]
}

# Function to validate input
function Test-InputValid {
    param(
        [string]$input,
        [string]$name
    )

    if ([string]::IsNullOrWhiteSpace($input)) {
        Write-Error-Custom "$name cannot be empty"
        exit 1
    }
}

# Function to check if directory is a git repo
function Test-GitRepo {
    if (Test-Path ".\.git") {
        return $true
    }
    return $false
}

# Validate inputs
Test-InputValid $ProjectName "ProjectName"
Test-InputValid $ProjectDescription "ProjectDescription"
Test-InputValid $TargetUsers "TargetUsers"

Write-Info "Initializing Boiler 4.0 project"
Write-Info "Project Name: $ProjectName"
Write-Info "Description: $ProjectDescription"
Write-Info "Target Users: $TargetUsers"
Write-Info "Mode: $Mode"
Write-Host ""

# Check if we're in a git repo
$isGitRepo = Test-GitRepo
if (-not $isGitRepo) {
    Write-Warn "Not a git repository. Initializing git..."
    git init
}

# Check if .claude directory already exists
if (Test-Path ".\.claude") {
    Write-Error-Custom ".claude directory already exists. Remove it or run this script in a new directory."
    exit 1
}

# Create .claude directory structure
Write-Info "Creating .claude directory structure..."
New-Item -ItemType Directory -Path ".\.claude\skills" -Force | Out-Null
New-Item -ItemType Directory -Path ".\.claude\rules\common" -Force | Out-Null
New-Item -ItemType Directory -Path ".\.claude\logs" -Force | Out-Null
New-Item -ItemType Directory -Path ".\.claude\instincts" -Force | Out-Null

# Copy skills from template
Write-Info "Copying skills from template..."
if (Test-Path ".\Boiler-4.0-Template\.claude\skills") {
    Copy-Item -Path ".\Boiler-4.0-Template\.claude\skills\*" -Destination ".\.claude\skills\" -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Warn "Template skills directory not found. Skipping skills copy."
}

# Copy rules from template
Write-Info "Copying rules from template..."
if (Test-Path ".\Boiler-4.0-Template\.claude\rules\common") {
    Copy-Item -Path ".\Boiler-4.0-Template\.claude\rules\common\*" -Destination ".\.claude\rules\common\" -Recurse -Force -ErrorAction SilentlyContinue
} else {
    Write-Warn "Template rules directory not found. Skipping rules copy."
}

# Copy CLAUDE.md if it exists in template
Write-Info "Setting up CLAUDE.md..."
if (Test-Path ".\Boiler-4.0-Template\CLAUDE.md") {
    Copy-Item -Path ".\Boiler-4.0-Template\CLAUDE.md" -Destination ".\.claude\CLAUDE.md" -Force
} else {
    # Create a minimal CLAUDE.md
    $claudeMdContent = @"
# PROJECT INSTRUCTIONS

## Project Identity

This is {{PROJECT_NAME}}.

**Description:** {{PROJECT_DESCRIPTION}}

**Target Users:** {{TARGET_USERS}}

## Quality Standards

- Code is production-ready on first draft
- No placeholder comments or TODO blocks
- Tests are comprehensive and maintainable
- Documentation is clear and current
- Security is considered in every design decision

## Development Practices

- Use appropriate skills from `.claude/skills/` for different tasks
- Follow conventional commits for all changes
- Run verification loop before pushing
- Maintain >80% test coverage
- Keep context compact with strategic-compact skill

## Mode Configuration

BOILER_MODE={{BOILER_MODE}}

- strict: All quality gates enforced, comprehensive checks
- lean: Essential checks only, faster iteration

"@
    Set-Content -Path ".\.claude\CLAUDE.md" -Value $claudeMdContent
}

# Create WORKSPACE.md if it doesn't exist
if (-not (Test-Path ".\.claude\WORKSPACE.md")) {
    Write-Info "Creating WORKSPACE.md..."
    $workspaceMdContent = @"
# Workspace State

## Current Phase
Phase 0: Initialization

## Recent Progress
- Project initialized
- Skills and rules loaded

## Next Steps
1. Configure project dependencies
2. Set up initial architecture
3. Begin Phase 1 execution

## Context Notes
(Add notes about project assumptions, key decisions, blockers)

"@
    Set-Content -Path ".\.claude\WORKSPACE.md" -Value $workspaceMdContent
}

# Create instincts.md template
Write-Info "Creating instincts template..."
$instinctsMdContent = @"
# Project Instincts (Learned Patterns)

This file captures learned patterns specific to {{PROJECT_NAME}}.

## Code Patterns
(Add patterns you want Claude to learn and apply automatically)

## API Conventions
(Add API design conventions used in this project)

## Testing Patterns
(Add testing patterns that should be followed)

## Deployment Strategies
(Add deployment patterns learned from experience)

## Known Gotchas
(Add surprising edge cases or gotchas discovered)

"@
Set-Content -Path ".\.claude\instincts.md" -Value $instinctsMdContent

# Create a basic .env template if it doesn't exist
if (-not (Test-Path ".\.env.example")) {
    Write-Info "Creating .env.example template..."
    $envContent = @"
# Environment Configuration
# Copy this file to .env and fill in actual values

# Project Settings
PROJECT_NAME={{PROJECT_NAME}}
NODE_ENV=development

# Database (if applicable)
DATABASE_URL=postgresql://user:password@localhost:5432/{{PROJECT_NAME}}

# API Keys (if applicable)
# API_KEY=your_api_key_here

# Feature Flags
BOILER_MODE={{BOILER_MODE}}

"@
    Set-Content -Path ".\.env.example" -Value $envContent
}

# Create .gitignore entries if .gitignore doesn't exist
if (-not (Test-Path ".\.gitignore")) {
    Write-Info "Creating .gitignore..."
    $gitignoreContent = @"
# Dependencies
node_modules/
venv/
__pycache__/
*.pyc
.Python
env/
ENV/

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Build
dist/
build/
.next/
out/
coverage/

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Claude Code
.claude/logs/
.claude/.cache/

# Temporary
*.tmp
.cache/
temp/

"@
    Set-Content -Path ".\.gitignore" -Value $gitignoreContent
}

# Create a basic README if it doesn't exist
if (-not (Test-Path ".\README.md")) {
    Write-Info "Creating README.md..."
    $readmeContent = @"
# {{PROJECT_NAME}}

{{PROJECT_DESCRIPTION}}

**Target Users:** {{TARGET_USERS}}

## Quick Start

1. Install dependencies
2. Configure environment (`.env`)
3. Run development server
4. See CONTRIBUTING.md for development practices

## Documentation

- `.claude/skills/README.md` - Available development skills
- `.claude/CLAUDE.md` - Project instructions
- `.claude/WORKSPACE.md` - Current workspace state

## Architecture

(Describe project architecture, main components, key decisions)

## Contributing

Follow the guidelines in `.claude/CLAUDE.md` and use the skills from `.claude/skills/`.

"@
    Set-Content -Path ".\README.md" -Value $readmeContent
}

# Function to replace template variables
function Replace-TemplateVariables {
    param([string]$filePath)

    if (Test-Path $filePath) {
        $content = Get-Content -Path $filePath -Raw
        $content = $content -replace "{{PROJECT_NAME}}", $ProjectName
        $content = $content -replace "{{PROJECT_DESCRIPTION}}", $ProjectDescription
        $content = $content -replace "{{TARGET_USERS}}", $TargetUsers
        $content = $content -replace "{{BOILER_MODE}}", $Mode
        Set-Content -Path $filePath -Value $content
    }
}

# Replace template variables in files
Write-Info "Replacing template variables..."
Replace-TemplateVariables ".\.claude\CLAUDE.md"
Replace-TemplateVariables ".\.claude\WORKSPACE.md"
Replace-TemplateVariables ".\.claude\instincts.md"
Replace-TemplateVariables ".\.env.example"
Replace-TemplateVariables ".\README.md"

# Create initial git commit if in a repo
if ($isGitRepo -or (Test-Path ".\.git")) {
    Write-Info "Creating initial commit..."
    & git add . | Out-Null
    & git commit -m "chore: initialize Boiler 4.0 project - $ProjectName" -ErrorAction SilentlyContinue | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Could not create initial commit"
    }
}

# Success output
Write-Host ""
Write-Success "Project initialized successfully!"
Write-Host ""
Write-Host "Project: $ProjectName"
Write-Host "Mode: $Mode"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Review .claude\CLAUDE.md - Project instructions"
Write-Host "2. Explore .claude\skills\README.md - Available skills"
Write-Host "3. Configure .env from .env.example"
Write-Host "4. Update README.md with architecture details"
Write-Host "5. Start building with available skills"
Write-Host ""
Write-Host "Key directories:"
Write-Host "  .claude\           - Claude Code configuration and skills"
Write-Host "  .claude\skills\    - 24 reusable development skills"
Write-Host "  .claude\rules\     - Coding standards and guidelines"
Write-Host "  .claude\logs\      - Execution logs and artifacts"
Write-Host ""
Write-Info "Happy coding!"
