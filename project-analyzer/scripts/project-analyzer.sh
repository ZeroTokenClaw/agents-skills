#!/usr/bin/env bash
# Project Analyzer - Main entry point
# Usage: ./project-analyzer.sh [--quick|--full] [--json]
# Output: Complete project health report

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

MODE="full"
OUTPUT_JSON=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --quick|-q)
      MODE="quick"
      shift
      ;;
    --full|-f)
      MODE="full"
      shift
      ;;
    --json|-j)
      OUTPUT_JSON=true
      shift
      ;;
    --help|-h)
      echo "Usage: $0 [--quick|--full] [--json]"
      echo ""
      echo "Options:"
      echo "  --quick, -q    Fast scan (5 key dimensions only)"
      echo "  --full, -f     Complete analysis (default)"
      echo "  --json, -j     Output in JSON format"
      echo "  --help, -h     Show this help"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "🔍 Project Analyzer"
echo "=================="
echo ""

if [ "$MODE" = "quick" ]; then
  echo "🚀 Quick Scan Mode"
  echo ""
  
  # Quick checks
  echo "=== Quick Health Check ==="
  echo ""
  
  # Check 1: Config files
  CONFIG_COUNT=$(ls -1 package.json pyproject.toml go.mod Cargo.toml 2>/dev/null | wc -l)
  echo "📋 Config Files: $CONFIG_COUNT"
  
  # Check 2: Source structure
  if [ -d "src" ]; then
    echo "✅ src/ directory present"
  elif [ -d "lib" ]; then
    echo "✅ lib/ directory present"
  elif [ -d "app" ]; then
    echo "✅ app/ directory present"
  else
    echo "⚠️  No standard source directory found"
  fi
  
  # Check 3: Test presence
  if [ -d "__tests__" ] || [ -d "test" ] || [ -d "tests" ] || [ -d "spec" ]; then
    echo "✅ Test directory present"
  else
    echo "⚠️  No test directory found"
  fi
  
  # Check 4: Type checking
  if [ -f "tsconfig.json" ] || [ -f "pyproject.toml" ] && grep -q 'mypy\|pyright' pyproject.toml 2>/dev/null; then
    echo "✅ Type checking configured"
  else
    echo "⚠️  No type checking configured"
  fi
  
  # Check 5: Git hooks
  if [ -d ".husky" ] || [ -f "package.json" ] && grep -q 'husky' package.json 2>/dev/null; then
    echo "✅ Git hooks configured"
  else
    echo "⚠️  No git hooks configured"
  fi
  
  echo ""
  echo "✅ Quick scan complete"
  
else
  echo "🚀 Full Analysis Mode"
  echo ""
  
  # Run all dimension checks
  echo "=== Dimension 1: Identity & Configuration ==="
  "$SCRIPT_DIR/scan-configs.sh"
  echo ""
  
  echo "=== Dimension 2: Architecture & Structure ==="
  "$SCRIPT_DIR/analyze-structure.sh"
  echo ""
  
  echo "=== Dimension 3: Syntax & Conventions ==="
  "$SCRIPT_DIR/detect-conventions.sh"
  echo ""
  
  echo "=== Dimension 4: Version & Compatibility ==="
  "$SCRIPT_DIR/check-versions.sh"
  echo ""
  
  echo "=== Dimension 5: Developer Experience ==="
  "$SCRIPT_DIR/measure-dx.sh"
  echo ""
  
  # Calculate overall health score
  echo "📊 Overall Health Score"
  echo "======================"
  echo ""
  
  SCORE=0
  
  # Dimension 1: Configuration (0-25)
  CONFIG_FILES=$(ls -1 package.json pyproject.toml go.mod Cargo.toml tsconfig.json .eslintrc* .prettierrc* 2>/dev/null | wc -l)
  if [ $CONFIG_FILES -gt 5 ]; then
    SCORE=$((SCORE + 25))
  elif [ $CONFIG_FILES -gt 3 ]; then
    SCORE=$((SCORE + 15))
  elif [ $CONFIG_FILES -gt 0 ]; then
    SCORE=$((SCORE + 10))
  fi
  
  # Dimension 2: Architecture (0-20)
  if [ -d "src" ] || [ -d "lib" ] || [ -d "app" ]; then
    SCORE=$((SCORE + 10))
  fi
  if [ -d "packages" ] || [ -f "turbo.json" ] || [ -f "nx.json" ]; then
    SCORE=$((SCORE + 10))
  else
    SCORE=$((SCORE + 5))
  fi
  
  # Dimension 3: Conventions (0-20)
  if [ -f ".eslintrc" ] || [ -f ".eslintrc.js" ]; then
    SCORE=$((SCORE + 10))
  fi
  if [ -f ".prettierrc" ] || [ -f ".prettierrc.js" ]; then
    SCORE=$((SCORE + 5))
  fi
  if [ -f "tsconfig.json" ]; then
    SCORE=$((SCORE + 5))
  fi
  
  # Dimension 4: Versioning (0-15)
  if [ -f "package-lock.json" ] || [ -f "pnpm-lock.yaml" ] || [ -f "yarn.lock" ]; then
    SCORE=$((SCORE + 10))
  fi
  if [ -f ".nvmrc" ] || [ -f ".python-version" ]; then
    SCORE=$((SCORE + 5))
  fi
  
  # Dimension 5: DX (0-20)
  if [ -f "package.json" ] && grep -q '"test"' package.json 2>/dev/null; then
    SCORE=$((SCORE + 10))
  fi
  if [ -d ".husky" ] || [ -f "package.json" ] && grep -q 'husky' package.json 2>/dev/null; then
    SCORE=$((SCORE + 5))
  fi
  if [ -f "README.md" ]; then
    SCORE=$((SCORE + 5))
  fi
  
  # Level determination
  if [ $SCORE -ge 85 ]; then
    LEVEL="Excellent"
  elif [ $SCORE -ge 65 ]; then
    LEVEL="Good"
  elif [ $SCORE -ge 45 ]; then
    LEVEL="Needs Work"
  else
    LEVEL="Critical"
  fi
  
  echo "   Health Score: $SCORE/100 ($LEVEL)"
  echo ""
  
  # Recommendations
  echo "💡 Recommendations:"
  echo "------------------"
  
  if [ $CONFIG_FILES -lt 5 ]; then
    echo "   • Add more configuration files (ESLint, Prettier, TypeScript)"
  fi
  
  if ! [ -f ".eslintrc" ]; then
    echo "   • Configure ESLint for code quality enforcement"
  fi
  
  if ! [ -f ".prettierrc" ]; then
    echo "   • Configure Prettier for consistent formatting"
  fi
  
  if ! [ -f "package.json" ] && ! [ -f "pyproject.toml" ] && ! [ -f "go.mod" ]; then
    echo "   • Add dependency management configuration"
  fi
  
  if ! [ -d "__tests__" ] && ! [ -d "tests" ]; then
    echo "   • Add test directory and configure test framework"
  fi
  
  if ! [ -f "README.md" ]; then
    echo "   • Add README.md with project documentation"
  fi
  
  if ! [ -d ".github/workflows" ]; then
    echo "   • Add CI/CD configuration (GitHub Actions)"
  fi
  
  echo ""
  echo "✅ Analysis complete"
  echo ""
  echo "💡 Next steps:"
  echo "   1. Address recommendations above"
  echo "   2. Run specific dimension scripts for details:"
  echo "      • $SCRIPT_DIR/scan-configs.sh"
  echo "      • $SCRIPT_DIR/analyze-structure.sh"
  echo "      • $SCRIPT_DIR/detect-conventions.sh"
  echo "      • $SCRIPT_DIR/check-versions.sh"
  echo "      • $SCRIPT_DIR/measure-dx.sh"
fi

exit 0
