#!/usr/bin/env bash
# Developer experience measurer - Dimension 5
# Usage: ./measure-dx.sh [--json]
# Output: Development tooling, scripts, and DX metrics

set -e

OUTPUT_JSON=false
if [ "$1" = "--json" ]; then
  OUTPUT_JSON=false  # Keep simple for now
fi

echo "🛠️  Developer Experience Measurer"
echo "=================================="
echo ""

# Script availability check
echo "📜 Available Scripts:"
echo "---------------------"

if [ -f "package.json" ]; then
  echo "   npm scripts:"
  jq -r '.scripts | to_entries[] | "   • " + .key + ": " + .value' package.json 2>/dev/null | head -15
fi

if [ -f "Makefile" ]; then
  echo ""
  echo "   make targets:"
  grep -E "^[a-zA-Z_-]+:" Makefile | head -15 | sed 's/:$//' | while read target; do
    echo "   • $target"
  done
fi

if [ -f "Taskfile" ] || [ -f "Taskfile.yml" ] || [ -f "Taskfile.yaml" ]; then
  echo ""
  echo "   task targets:"
  grep -E "^  [a-zA-Z_-]+:" Taskfile* 2>/dev/null | head -15 | sed 's/:$//' | while read target; do
    echo "   • $target"
  done
fi

if [ -f "justfile" ]; then
  echo ""
  echo "   just recipes:"
  grep -E "^[a-zA-Z_-]+" justfile | head -15 | while read recipe; do
    echo "   • $recipe"
  done
fi

echo ""

# Git hooks detection
echo "🪝 Git Hooks:"
echo "-------------"

if [ -d ".git/hooks" ]; then
  HOOKS=$(ls -1 .git/hooks/ 2>/dev/null | grep -v '\.sample$' || echo "none")
  if [ "$HOOKS" != "none" ] && [ -n "$HOOKS" ]; then
    echo "$HOOKS" | while read hook; do
      echo "   • $hook"
    done
  else
    echo "   ℹ️  No custom hooks configured"
  fi
fi

# Detect husky
if [ -d ".husky" ]; then
  echo "   ✅ Husky detected"
  HUSKY_HOOKS=$(ls -1 .husky/ 2>/dev/null | grep -E '^(prepare-commit-msg|pre-commit|commit-msg)' | head -5 || echo "")
  if [ -n "$HUSKY_HOOKS" ]; then
    echo "$HUSKY_HOOKS" | while read hook; do
      echo "   • husky: $hook"
    done
  fi
fi

# Detect lint-staged
if [ -f "package.json" ] && grep -q '"lint-staged"' package.json 2>/dev/null; then
  echo "   ✅ lint-staged detected"
fi

# Detect commitlint
if [ -f "package.json" ] && grep -q '"commitlint"' package.json 2>/dev/null; then
  echo "   ✅ commitlint detected"
fi

echo ""

# Type checking availability
echo "🔍 Type Checking:"
echo "-----------------"

if [ -f "package.json" ] && grep -q '"typecheck"' package.json 2>/dev/null; then
  TYPE_SCRIPT=$(jq -r '.scripts.typecheck // empty' package.json 2>/dev/null)
  if [ -n "$TYPE_SCRIPT" ]; then
    echo "   ✅ TypeScript type checking configured"
    echo "   Command: $TYPE_SCRIPT"
  fi
fi

if [ -f "pyproject.toml" ] && grep -q '\[tool.mypy\]' pyproject.toml 2>/dev/null; then
  echo "   ✅ mypy configured for Python"
fi

if [ -f "pyrightconfig.json" ] || [ -f "pyproject.toml" ] && grep -q '\[tool.pyright\]' pyproject.toml 2>/dev/null; then
  echo "   ✅ pyright configured for Python"
fi

if [ -f ".golangci.yml" ] || [ -f ".golangci.yaml" ]; then
  echo "   ✅ golangci-lint configured for Go"
fi

if [ -f "Cargo.toml" ] && grep -q '\[lint\]' Cargo.toml 2>/dev/null; then
  echo "   ✅ Clippy configured for Rust"
fi

echo ""

# Build speed indicators
echo "⚡ Build Speed Indicators:"
echo "--------------------------"

if [ -f "package.json" ] && grep -q '"build"' package.json 2>/dev/null; then
  BUILD_SCRIPT=$(jq -r '.scripts.build // empty' package.json 2>/dev/null)
  if [ -n "$BUILD_SCRIPT" ]; then
    echo "   Build command: $BUILD_SCRIPT"
  fi
fi

# Detect Turborepo
if [ -f "turbo.json" ]; then
  echo "   ✅ Turborepo detected (cached builds)"
  if [ -f "package.json" ] && grep -q '"turbo"' package.json 2>/dev/null; then
    TURBO_TASKS=$(jq -r '.pipeline | keys[]' package.json 2>/dev/null | grep -v '"build"' | head -5 || echo "")
    if [ -n "$TURBO_TASKS" ]; then
      echo "   Turbo tasks: $(echo $TURBO_TASKS | tr '\n' ' ')"
    fi
  fi
fi

# Detect Nx
if [ -f "nx.json" ]; then
  echo "   ✅ Nx detected (cached builds)"
fi

# Vite detection
if [ -f "vite.config.ts" ] || [ -f "vite.config.js" ]; then
  echo "   ✅ Vite detected (fast HMR)"
fi

# SWC detection
if grep -q '"swc"' package.json 2>/dev/null || grep -q '@swc' package.json 2>/dev/null; then
  echo "   ✅ SWC detected (fast TypeScript compilation)"
fi

echo ""

# Test infrastructure
echo "🧪 Test Infrastructure:"
echo "-----------------------"

if [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
  TEST_SCRIPT=$(jq -r '.scripts.test // empty' package.json 2>/dev/null)
  if [ -n "$TEST_SCRIPT" ]; then
    echo "   Test command: $TEST_SCRIPT"
  fi
fi

# Detect Jest
if grep -q '"jest"' package.json 2>/dev/null; then
  echo "   • Jest detected"
fi

# Detect Vitest
if grep -q '"vitest"' package.json 2>/dev/null; then
  echo "   • Vitest detected"
fi

# Detect Cypress
if grep -q '"cypress"' package.json 2>/dev/null; then
  echo "   • Cypress detected (E2E)"
fi

# Detect Playwright
if grep -q '"playwright"' package.json 2>/dev/null; then
  echo "   • Playwright detected (E2E)"
fi

# Detect pytest
if [ -f "pytest.ini" ] || [ -f "pyproject.toml" ] && grep -q '\[tool.pytest' pyproject.toml 2>/dev/null; then
  echo "   • pytest detected"
fi

echo ""

# IDE support indicators
echo "💻 IDE Support:"
echo "---------------"

if [ -d ".vscode" ]; then
  echo "   ✅ VS Code configuration present"
  VSCODE_FILES=$(ls -1 .vscode/ 2>/dev/null | head -5 | tr '\n' ',')
  echo "   Files: $VSCODE_FILES"
fi

if [ -f ".editorconfig" ]; then
  echo "   ✅ .editorconfig present"
fi

if [ -f ".env.example" ] || [ -f ".env.template" ]; then
  echo "   ✅ Environment template present"
fi

if [ -f "tsconfig.json" ] && [ -f ".vscode/settings.json" ]; then
  echo "   ✅ TypeScript + VS Code integration"
fi

echo ""

# Documentation indicators
echo "📚 Documentation:"
echo "-----------------"

if [ -f "README.md" ]; then
  README_SIZE=$(wc -l < README.md)
  echo "   ✅ README.md ($README_SIZE lines)"
fi

if [ -f "CONTRIBUTING.md" ]; then
  echo "   ✅ CONTRIBUTING.md present"
fi

if [ -f "docs" ]; then
  DOC_FILES=$(find docs -type f -name "*.md" 2>/dev/null | wc -l)
  echo "   ✅ docs/ directory ($DOC_FILES files)"
fi

if [ -f "ARCHITECTURE.md" ] || [ -f "ARCHITECTURE.md" ]; then
  echo "   ✅ Architecture documentation present"
fi

if [ -f "DEPLOYMENT.md" ] || [ -f "DEPLOY.md" ]; then
  echo "   ✅ Deployment documentation present"
fi

echo ""

# Code generation tools
echo "🔧 Code Generation:"
echo "-------------------"

if grep -q '"generate"\|"gen"\|"scaffold"' package.json 2>/dev/null; then
  echo "   Code generation script detected"
fi

if [ -d ".plop" ] || [ -f "plopfile.js" ]; then
  echo "   ✅ Plop detected"
fi

if [ -d "hygen" ] || [ -f "hygen.yaml" ]; then
  echo "   ✅ Hygen detected"
fi

if [ -f ".copier.yml" ] || [ -f "copier.yaml" ]; then
  echo "   ✅ Copier detected"
fi

echo ""

# CI/CD presence
echo "🔄 CI/CD Configuration:"
echo "-----------------------"

if [ -d ".github/workflows" ]; then
  WORKFLOW_COUNT=$(ls -1 .github/workflows/ 2>/dev/null | wc -l)
  echo "   ✅ GitHub Actions ($WORKFLOW_COUNT workflows)"
fi

if [ -f ".circleci/config.yml" ]; then
  echo "   ✅ CircleCI configured"
fi

if [ -f ".gitlab-ci.yml" ]; then
  echo "   ✅ GitLab CI configured"
fi

if [ -f "Dockerfile" ]; then
  echo "   ✅ Dockerfile present"
fi

if [ -f "docker-compose.yml" ]; then
  echo "   ✅ docker-compose.yml present"
fi

echo ""

# DX Score calculation (simple heuristic)
echo "📊 DX Score Calculation:"
echo "------------------------"

DX_SCORE=0

# Check scripts
if [ -f "package.json" ]; then
  SCRIPT_COUNT=$(jq -r '.scripts | keys | length' package.json 2>/dev/null || echo "0")
  DX_SCORE=$((DX_SCORE + SCRIPT_COUNT * 2))
fi

# Check type checking
if [ -f "tsconfig.json" ] || [ -f "pyproject.toml" ] && grep -q 'mypy\|pyright' pyproject.toml 2>/dev/null; then
  DX_SCORE=$((DX_SCORE + 10))
fi

# Check linting
if [ -f ".eslintrc" ] || [ -f ".eslintrc.js" ] || [ -f "pyproject.toml" ] && grep -q 'ruff\|pylint' pyproject.toml 2>/dev/null; then
  DX_SCORE=$((DX_SCORE + 10))
fi

# Check formatting
if [ -f ".prettierrc" ] || [ -f ".prettierrc.js" ]; then
  DX_SCORE=$((DX_SCORE + 5))
fi

# Check tests
if [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
  DX_SCORE=$((DX_SCORE + 10))
fi

# Check documentation
if [ -f "README.md" ]; then
  DX_SCORE=$((DX_SCORE + 5))
fi

# Check CI/CD
if [ -d ".github/workflows" ] || [ -f ".circleci/config.yml" ]; then
  DX_SCORE=$((DX_SCORE + 10))
fi

# Check git hooks
if [ -d ".husky" ] || [ -f "package.json" ] && grep -q 'husky' package.json 2>/dev/null; then
  DX_SCORE=$((DX_SCORE + 5))
fi

# Cap at 100
if [ $DX_SCORE -gt 100 ]; then
  DX_SCORE=100
fi

echo "   DX Score: $DX_SCORE/100"

if [ $DX_SCORE -ge 80 ]; then
  echo "   🏆 Excellent DX (profiling, linting, tests, docs all present)"
elif [ $DX_SCORE -ge 60 ]; then
  echo "   ✅ Good DX (core tooling present)"
elif [ $DX_SCORE -ge 40 ]; then
  echo "   ⚠️  Basic DX (room for improvement)"
else
  echo "   ❌ Poor DX (significant tooling gaps)"
fi

echo ""

exit 0
