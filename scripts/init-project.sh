#!/bin/bash
set -euo pipefail

# Boiler 4.0 Project Initialization Script (Bash)
# Usage: ./scripts/init-project.sh <ProjectName> <ProjectDescription> <TargetUsers> [--mode=strict|lean]

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to validate input
validate_input() {
    local input="$1"
    local name="$2"

    if [ -z "$input" ]; then
        log_error "$name cannot be empty"
        exit 1
    fi
}

# Function to check if directory is a git repo
is_git_repo() {
    if [ -d ".git" ]; then
        return 0
    else
        return 1
    fi
}

# Validate arguments
if [ $# -lt 3 ]; then
    log_error "Usage: ./scripts/init-project.sh <ProjectName> <ProjectDescription> <TargetUsers> [--mode=strict|lean]"
    echo ""
    echo "Arguments:"
    echo "  ProjectName           - Name of the project (e.g., 'MyApp', 'UserService')"
    echo "  ProjectDescription    - Brief description of the project"
    echo "  TargetUsers           - Target users (e.g., 'Enterprise customers', 'iOS developers')"
    echo "  --mode=<mode>         - Optional: strict (default) or lean"
    echo ""
    echo "Example:"
    echo "  ./scripts/init-project.sh MyApp 'Payment processing service' 'SaaS customers' --mode=strict"
    exit 1
fi

PROJECT_NAME="$1"
PROJECT_DESCRIPTION="$2"
TARGET_USERS="$3"
BOILER_MODE="strict"

# Parse optional mode flag
if [ $# -ge 4 ]; then
    case "$4" in
        --mode=strict|--mode=lean)
            BOILER_MODE="${4#--mode=}"
            ;;
        *)
            log_error "Unknown option: $4"
            exit 1
            ;;
    esac
fi

# Validate inputs
validate_input "$PROJECT_NAME" "ProjectName"
validate_input "$PROJECT_DESCRIPTION" "ProjectDescription"
validate_input "$TARGET_USERS" "TargetUsers"

log_info "Initializing Boiler 4.0 project"
log_info "Project Name: $PROJECT_NAME"
log_info "Description: $PROJECT_DESCRIPTION"
log_info "Target Users: $TARGET_USERS"
log_info "Mode: $BOILER_MODE"
echo ""

# Check if we're in a git repo
if ! is_git_repo; then
    log_warn "Not a git repository. Initializing git..."
    git init
fi

# Check if .claude directory already exists
if [ -d ".claude" ]; then
    log_error ".claude directory already exists. Remove it or run this script in a new directory."
    exit 1
fi

# Create .claude directory structure
log_info "Creating .claude directory structure..."
mkdir -p ".claude/skills"
mkdir -p ".claude/rules/common"
mkdir -p ".claude/logs"
mkdir -p ".claude/instincts"

# Copy skills from template
log_info "Copying skills from template..."
if [ -d "Boiler-4.0-Template/.claude/skills" ]; then
    cp -r "Boiler-4.0-Template/.claude/skills/"* ".claude/skills/" 2>/dev/null || true
else
    log_warn "Template skills directory not found. Skipping skills copy."
fi

# Copy rules from template
log_info "Copying rules from template..."
if [ -d "Boiler-4.0-Template/.claude/rules/common" ]; then
    cp -r "Boiler-4.0-Template/.claude/rules/common/"* ".claude/rules/common/" 2>/dev/null || true
else
    log_warn "Template rules directory not found. Skipping rules copy."
fi

# Copy CLAUDE.md if it exists in template
log_info "Setting up CLAUDE.md..."
if [ -f "Boiler-4.0-Template/CLAUDE.md" ]; then
    cp "Boiler-4.0-Template/CLAUDE.md" ".claude/CLAUDE.md"
else
    # Create a minimal CLAUDE.md
    cat > ".claude/CLAUDE.md" << 'EOF'
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

EOF
fi

# Create WORKSPACE.md if it doesn't exist
if [ ! -f ".claude/WORKSPACE.md" ]; then
    log_info "Creating WORKSPACE.md..."
    cat > ".claude/WORKSPACE.md" << 'EOF'
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
EOF
fi

# Create instincts.md template
log_info "Creating instincts template..."
cat > ".claude/instincts.md" << 'EOF'
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

EOF

# Create a basic .env template if it doesn't exist
if [ ! -f ".env.example" ]; then
    log_info "Creating .env.example template..."
    cat > ".env.example" << 'EOF'
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
EOF
fi

# Create .gitignore entries if .gitignore doesn't exist
if [ ! -f ".gitignore" ]; then
    log_info "Creating .gitignore..."
    cat > ".gitignore" << 'EOF'
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
EOF
fi

# Create a basic README if it doesn't exist
if [ ! -f "README.md" ]; then
    log_info "Creating README.md..."
    cat > "README.md" << 'EOF'
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

EOF
fi

# Replace template variables in files
log_info "Replacing template variables..."
replace_template_vars() {
    local file="$1"
    if [ -f "$file" ]; then
        if [ "$(uname)" = "Darwin" ]; then
            # macOS requires an empty string after -i
            sed -i '' "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$file"
            sed -i '' "s|{{PROJECT_DESCRIPTION}}|$PROJECT_DESCRIPTION|g" "$file"
            sed -i '' "s|{{TARGET_USERS}}|$TARGET_USERS|g" "$file"
            sed -i '' "s|{{BOILER_MODE}}|$BOILER_MODE|g" "$file"
        else
            # Linux/other Unix
            sed -i "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" "$file"
            sed -i "s|{{PROJECT_DESCRIPTION}}|$PROJECT_DESCRIPTION|g" "$file"
            sed -i "s|{{TARGET_USERS}}|$TARGET_USERS|g" "$file"
            sed -i "s|{{BOILER_MODE}}|$BOILER_MODE|g" "$file"
        fi
    fi
}

replace_template_vars ".claude/CLAUDE.md"
replace_template_vars ".claude/WORKSPACE.md"
replace_template_vars ".claude/instincts.md"
replace_template_vars ".env.example"
replace_template_vars "README.md"

# Create initial git commit if in a repo
if is_git_repo; then
    log_info "Creating initial commit..."
    git add .
    git commit -m "chore: initialize Boiler 4.0 project - $PROJECT_NAME" || log_warn "Could not create initial commit"
fi

# Success output
echo ""
log_success "Project initialized successfully!"
echo ""
echo "Project: $PROJECT_NAME"
echo "Mode: $BOILER_MODE"
echo ""
echo "Next steps:"
echo "1. Review .claude/CLAUDE.md - Project instructions"
echo "2. Explore .claude/skills/README.md - Available skills"
echo "3. Configure .env from .env.example"
echo "4. Update README.md with architecture details"
echo "5. Start building with available skills"
echo ""
echo "Key directories:"
echo "  .claude/           - Claude Code configuration and skills"
echo "  .claude/skills/    - 24 reusable development skills"
echo "  .claude/rules/     - Coding standards and guidelines"
echo "  .claude/logs/      - Execution logs and artifacts"
echo ""
log_info "Happy coding!"
