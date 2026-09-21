#!/usr/bin/env bash
# Quick project config scanner - Dimension 1
# Usage: ./scan-configs.sh [--json]
# Output: List of config files with their purpose

set -e

OUTPUT_JSON=false
if [ "$1" = "--json" ]; then
  OUTPUT_JSON=true
fi

CONFIG_FILES=(
  "package.json:Node.js package metadata"
  "package-lock.json:Yarn lock file"
  "pnpm-lock.yaml:pnpm lock file"
  "yarn.lock:Yarn lock file"
  "go.mod:Go module definition"
  "Cargo.toml:Rust package manifest"
  "pyproject.toml:Python project metadata"
  "pom.xml:Maven project object model"
  "build.gradle:Gradle build script"
  "Makefile:Make build automation"
  "tsconfig.json:TypeScript configuration"
  ".tsconfig.json:TypeScript configuration"
  "jsconfig.json:JavaScript configuration"
  ".eslintrc.js:ESLint configuration"
  ".eslintrc.json:ESLint configuration"
  ".eslintrc:ESLint configuration"
  "eslint.config.js:ESLint configuration"
  ".prettierrc:.prettierrc configuration"
  ".prettierrc.json:.prettierrc configuration"
  "prettier.config.js:Prettier configuration"
  ".browserslistrc:Browserslist configuration"
  "tsconfig.node.json:TypeScript Node config"
  "vite.config.ts:Vite configuration"
  "vite.config.js:Vite configuration"
  "next.config.js:Next.js configuration"
  "next.config.mjs:Next.js configuration"
  "turbo.json:Turborepo configuration"
  "nx.json:Nx configuration"
  ".nvmrc:Node version specification"
  ".node-version:Node version specification"
  ".python-version:Python version specification"
  ".tool-versions:asdf version specification"
  ".env:.env template"
  ".env.example:Environment template"
  ".env.development:Development environment"
  ".env.production:Production environment"
  ".github/workflows/:GitHub Actions workflows"
  ".gitlab-ci.yml:GitLab CI configuration"
  ".circleci/config.yml:CircleCI configuration"
  "Dockerfile:Docker image definition"
  "docker-compose.yml:Docker Compose configuration"
  "Makefile:Build automation"
  "Taskfile:Task automation"
  "justfile:Just recipe automation"
  "pyrightconfig.json:Pyright configuration"
  "mypy.ini:Mypy configuration"
  "ruff.toml:Ruff linter configuration"
  "pylintrc:Pylint configuration"
  ".golangci.yml:GolangCI linting configuration"
  "rustfmt.toml:Rust formatter configuration"
  "clippy.toml:Clippy linter configuration"
  ".commitlintrc.js:Commitlint configuration"
  "commitlint.config.js:Commitlint configuration"
  "huskyrc:Husky git hooks configuration"
  ".huskyrc:Husky git hooks configuration"
  "lint-staged.config.js:Lint-staged configuration"
)

echo "📋 Project Configuration Scanner"
echo "================================"

if $OUTPUT_JSON; then
  echo "["
fi

FOUND_COUNT=0
for item in "${CONFIG_FILES[@]}"; do
  IFS=':' read -r file description <<< "$item"
  
  if [ -f "$file" ]; then
    FOUND_COUNT=$((FOUND_COUNT + 1))
    if $OUTPUT_JSON; then
      if [ $FOUND_COUNT -gt 1 ]; then
        echo ","
      fi
      echo -n "  {\"file\": \"$file\", \"description\": \"$description\"}"
    else
      echo "✅ $file - $description"
    fi
  elif [ -d "$file" ]; then
    FOUND_COUNT=$((FOUND_COUNT + 1))
    if $OUTPUT_JSON; then
      if [ $FOUND_COUNT -gt 1 ]; then
        echo ","
      fi
      echo -n "  {\"file\": \"$file/\", \"description\": \"$description\"}"
    else
      echo "✅ $file/ - $description"
    fi
  fi
done

if $OUTPUT_JSON; then
  echo ""
  echo "]"
fi

echo ""
echo "Found $FOUND_COUNT configuration files"
echo ""

# Extract key project info
if [ -f "package.json" ]; then
  echo "📦 Package Manager: $(jq -r '.packageManager // "npm/yarn/pnpm"' package.json 2>/dev/null || echo "npm")"
  echo "🛠  Scripts: $(jq -r '.scripts | keys | join(", ")' package.json 2>/dev/null | cut -c1-60)..."
fi

if [ -f "go.mod" ]; then
  echo "📦 Go Module: $(head -1 go.mod | awk '{print $2}')"
  echo "🛠  Go Version: $(grep '^go ' go.mod | awk '{print $2}')"
fi

if [ -f "Cargo.toml" ]; then
  echo "📦 Rust Crate: $(grep '^name' Cargo.toml | awk '{print $3}' | tr -d '"')"
  echo "🛠  Edition: $(grep '^edition' Cargo.toml | awk '{print $3}' | tr -d '"')"
fi

if [ -f "pyproject.toml" ]; then
  echo "📦 Python Project: $(grep '^name' pyproject.toml | awk '{print $3}' | tr -d '"')"
  echo "🛠  Build System: $(grep 'build-system' -A2 pyproject.toml | grep requires -A2 | head -1 | tr -d '[]\" ')"
fi

exit 0
