#!/usr/bin/env bash
# Version compatibility checker - Dimension 4
# Usage: ./check-versions.sh [--json]
# Output: Runtime, framework, and dependency version analysis

set -e

OUTPUT_JSON=false
if [ "$1" = "--json" ]; then
  OUTPUT_JSON=true
fi

echo "📦 Version Compatibility Checker"
echo "================================"
echo ""

# Node.js version
if command -v node &> /dev/null; then
  NODE_VERSION=$(node --version)
  NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | tr -d 'v')
  
  echo "🟢 Node.js: $NODE_VERSION"
  
  # Check if LTS
  if [ "$NODE_MAJOR" -ge 18 ] && [ "$NODE_MAJOR" -le 20 ]; then
    echo "   ✅ Current LTS version"
  elif [ "$NODE_MAJOR" -lt 18 ]; then
    echo "   ⚠️  Outdated (LTS: 18-20)"
  else
    echo "   ℹ️  Latest version (check for stability)"
  fi
else
  echo "🔴 Node.js: Not installed"
fi

echo ""

# Python version
if command -v python3 &> /dev/null; then
  PY_VERSION=$(python3 --version 2>&1)
  echo "🐍 Python: $PY_VERSION"
elif command -v python &> /dev/null; then
  PY_VERSION=$(python --version 2>&1)
  echo "🐍 Python: $PY_VERSION"
else
  echo "🐍 Python: Not installed"
fi

echo ""

# Go version
if command -v go &> /dev/null; then
  GO_VERSION=$(go version | awk '{print $3}')
  echo "🐹 Go: $GO_VERSION"
else
  echo "🐹 Go: Not installed"
fi

echo ""

# Rust version
if command -v rustc &> /dev/null; then
  RUST_VERSION=$(rustc --version | awk '{print $2}')
  echo "🦀 Rust: $RUST_VERSION"
else
  echo "🦀 Rust: Not installed"
fi

echo ""

# Package.json analysis (if exists)
if [ -f "package.json" ]; then
  echo "📦 Package.json Dependencies:"
  echo "----------------------------"
  
  # Extract key dependencies
  echo "   Core dependencies:"
  jq -r '.dependencies // {} | keys[]' package.json 2>/dev/null | head -10 | while read dep; do
    version=$(jq -r ".dependencies[\"$dep\"]" package.json 2>/dev/null || echo "?")
    echo "   • $dep@$version"
  done
  
  if [ -f "package-lock.json" ] || [ -f "pnpm-lock.yaml" ] || [ -f "yarn.lock" ]; then
    echo ""
    echo "   ✅ Lock file present (reproducible builds)"
  else
    echo ""
    echo "   ⚠️  No lock file (installs may vary)"
  fi
  
  # Check for outdated dependencies
  if command -v npm &> /dev/null; then
    echo ""
    echo "   Outdated packages (if any):"
    npm outdated --depth=0 2>/dev/null | tail -n +2 | head -5 | while read line; do
      echo "   $line" | awk '{print "   • " $1 "@" $2 " → " $3}'
    done || echo "   • All packages up to date"
  fi
fi

echo ""

# Go.mod analysis (if exists)
if [ -f "go.mod" ]; then
  echo "📦 Go Module:"
  echo "------------"
  
  MODULE=$(head -1 go.mod | awk '{print $2}')
  GO_VERSION=$(grep '^go ' go.mod | awk '{print $2}')
  
  echo "   Module: $MODULE"
  echo "   Go version required: $GO_VERSION"
  
  # Check dependencies
  DEP_COUNT=$(grep -c "^require (" go.mod 2>/dev/null || echo "0")
  if [ "$DEP_COUNT" -gt 0 ]; then
    echo "   Dependencies: $DEP_COUNT direct require blocks"
  fi
fi

echo ""

# Cargo.toml analysis (if exists)
if [ -f "Cargo.toml" ]; then
  echo "📦 Rust Crate:"
  echo "--------------"
  
  CRATE_NAME=$(grep '^name' Cargo.toml | head -1 | awk '{print $3}' | tr -d '"')
  CRATE_VERSION=$(grep '^version' Cargo.toml | head -1 | awk '{print $3}' | tr -d '"')
  EDITION=$(grep '^edition' Cargo.toml | head -1 | awk '{print $3}' | tr -d '"')
  
  echo "   Name: $CRATE_NAME"
  echo "   Version: $CRATE_VERSION"
  echo "   Edition: $EDITION"
fi

echo ""

# pyproject.toml analysis (if exists)
if [ -f "pyproject.toml" ]; then
  echo "📦 Python Project:"
  echo "-----------------"
  
  PROJ_NAME=$(grep '^name' pyproject.toml | head -1 | awk '{print $3}' | tr -d '"')
  PROJ_VERSION=$(grep '^version' pyproject.toml | head -1 | awk '{print $3}' | tr -d '"')
  
  echo "   Name: $PROJ_NAME"
  echo "   Version: $PROJ_VERSION"
  
  # Check for common tools
  if grep -q '\[tool.poetry\]' pyproject.toml 2>/dev/null; then
    echo "   Build system: Poetry"
  elif grep -q '\[build-system\]' pyproject.toml 2>/dev/null; then
    echo "   Build system: PEP 517/518"
  fi
fi

echo ""

# Module system detection
echo "🔀 Module System:"
echo "-----------------"

if [ -f "package.json" ]; then
  if grep -q '"type".*"module"' package.json 2>/dev/null; then
    echo "   ✅ ES Modules (ESM)"
  elif grep -q '"type".*"commonjs"' package.json 2>/dev/null; then
    echo "   ⚠️  CommonJS (consider migrating to ESM)"
  else
    echo "   ℹ️  No type specified (defaults to CommonJS)"
  fi
fi

if [ -f "go.mod" ]; then
  echo "   ✅ Go Modules"
fi

if [ -f "Cargo.toml" ]; then
  echo "   ✅ Cargo/Rust Modules"
fi

echo ""

# Browser support detection
echo "🌐 Browser Support:"
echo "-------------------"

if [ -f ".browserslistrc" ]; then
  echo "   .browserslistrc present:"
  head -5 .browserslistrc | while read line; do
    echo "   $line"
  done
elif [ -f "package.json" ] && grep -q '"browserslist"' package.json 2>/dev/null; then
  echo "   package.json browserslist:"
  jq -r '.browserslist | join(", ")' package.json 2>/dev/null | head -c 100
  echo ""
else
  echo "   ℹ️  No browserlist configured (using defaults)"
fi

echo ""

# Key framework detection
echo "🛠 Key Framework Detection:"
echo "---------------------------"

# Detect frameworks from dependencies or files
if [ -f "package.json" ]; then
  if jq -e '.dependencies.next' package.json &>/dev/null; then
    NEXT_VER=$(jq -r '.dependencies.next' package.json)
    echo "   • Next.js@$NEXT_VER"
  fi
  
  if jq -e '.dependencies.react' package.json &>/dev/null; then
    REACT_VER=$(jq -r '.dependencies.react' package.json)
    echo "   • React@$REACT_VER"
  fi
  
  if jq -e '.dependencies.vue' package.json &>/dev/null; then
    VUE_VER=$(jq -r '.dependencies.vue' package.json)
    echo "   • Vue@$VUE_VER"
  fi
  
  if jq -e '.dependencies.express' package.json &>/dev/null; then
    EXP_VER=$(jq -r '.dependencies.express' package.json)
    echo "   • Express@$EXP_VER"
  fi
fi

if [ -f "go.mod" ]; then
  if grep -q 'gin-gonic/gin' go.mod 2>/dev/null; then
    echo "   • Gin (Go web framework)"
  fi
  
  if grep -q 'gorm' go.mod 2>/dev/null; then
    echo "   • GORM (Go ORM)"
  fi
fi

if [ -f "Cargo.toml" ]; then
  if grep -q 'actix-web' Cargo.toml 2>/dev/null; then
    echo "   • Actix-web (Rust web framework)"
  fi
  
  if grep -q 'tokio' Cargo.toml 2>/dev/null; then
    echo "   • Tokio (Rust async runtime)"
  fi
fi

if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  if grep -q 'django' pyproject.toml requirements.txt 2>/dev/null; then
    echo "   • Django (Python web framework)"
  fi
  
  if grep -q 'fastapi' pyproject.toml requirements.txt 2>/dev/null; then
    echo "   • FastAPI (Python web framework)"
  fi
fi

echo ""
echo "✅ Version check complete"

exit 0
