#!/usr/bin/env bash
# Code convention detector - Dimension 3
# Usage: ./detect-conventions.sh [--json]
# Output: Detected naming conventions and coding patterns

set -e

OUTPUT_JSON=false
if [ "$1" = "--json" ]; then
  OUTPUT_JSON=false  # Keep false for now, simplify
fi

echo "🎨 Code Convention Detector"
echo "============================"
echo ""

# Sample files for analysis
SAMPLE_DIRS="src lib app packages"
if [ ! -d "src" ] && [ ! -d "lib" ] && [ ! -d "app" ]; then
  SAMPLE_DIRS="."
fi

# Detect file naming conventions
echo "📝 File Naming Conventions:"
echo "---------------------------"

FILE_PATTERNS=$(find $SAMPLE_DIRS -type f -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" 2>/dev/null | head -20 | xargs basename -a 2>/dev/null | sort -u)

if [ -n "$FILE_PATTERNS" ]; then
  # Check kebab-case
  KEBAB_COUNT=$(echo "$FILE_PATTERNS" | grep -E '^[a-z]+(-[a-z0-9]+)*\.(ts|tsx|js|jsx|py|go)$' | wc -l)
  
  # Check PascalCase
  PASCAL_COUNT=$(echo "$FILE_PATTERNS" | grep -E '^[A-Z][a-zA-Z0-9]*\.(ts|tsx|js|jsx|py|go)$' | wc -l)
  
  # Check snake_case (Python)
  SNAKE_COUNT=$(echo "$FILE_PATTERNS" | grep -E '^[a-z]+(_[a-z0-9]+)*\.py$' | wc -l)
  
  # Check CamelCase
  CAMEL_COUNT=$(echo "$FILE_PATTERNS" | grep -E '^[a-z]+[A-Z][a-zA-Z0-9]*\.(ts|tsx|js|jsx)$' | wc -l)
  
  TOTAL=$(echo "$FILE_PATTERNS" | wc -l)
  
  echo "   Kebab-case: $KEBAB_COUNT files"
  echo "   PascalCase: $PASCAL_COUNT files"
  echo "   snake_case: $SNAKE_COUNT files"
  echo "   camelCase: $CAMEL_COUNT files"
  echo ""
  
  # Determine dominant convention
  if [ $KEBAB_COUNT -gt $PASCAL_COUNT ] && [ $KEBAB_COUNT -gt $SNAKE_COUNT ]; then
    FILE_CONVENTION="kebab-case"
  elif [ $PASCAL_COUNT -gt $KEBAB_COUNT ] && [ $PASCAL_COUNT -gt $SNAKE_COUNT ]; then
    FILE_CONVENTION="PascalCase"
  elif [ $SNAKE_COUNT -gt $KEBAB_COUNT ] && [ $SNAKE_COUNT -gt $PASCAL_COUNT ]; then
    FILE_CONVENTION="snake_case"
  else
    FILE_CONVENTION="mixed"
  fi
  
  echo "📌 Dominant File Convention: $FILE_CONVENTION"
fi

echo ""

# Detect import style
echo "🔗 Import/Export Patterns:"
echo "--------------------------"

SAMPLE_FILE=$(find $SAMPLE_DIRS -name "*.ts" -o -name "*.tsx" -o -name "*.js" 2>/dev/null | head -1)

if [ -n "$SAMPLE_FILE" ] && [ -f "$SAMPLE_FILE" ]; then
  # Check for named exports
  NAMED_EXPORTS=$(grep -c "^export {" "$SAMPLE_FILE" 2>/dev/null || echo "0")
  
  # Check for default exports
  DEFAULT_EXPORTS=$(grep -c "export default" "$SAMPLE_FILE" 2>/dev/null || echo "0")
  
  # Check for as-imports (TypeScript)
  TYPE_IMPORTS=$(grep -c "import type" "$SAMPLE_FILE" 2>/dev/null || echo "0")
  
  echo "   Named exports found: $NAMED_EXPORTS"
  echo "   Default exports found: $DEFAULT_EXPORTS"
  echo "   Type-only imports: $TYPE_IMPORTS"
fi

echo ""

# Detect state management
echo "📊 State Management Detection:"
echo "------------------------------"

if grep -r "createStore\|useStore" . --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | head -1 > /dev/null; then
  echo "   • Zustand detected"
fi

if grep -r "redux\|createSlice\|configureStore" . --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" 2>/dev/null | head -1 > /dev/null; then
  echo "   • Redux detected"
fi

if grep -r "useContext\|createContext" . --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | head -1 > /dev/null; then
  echo "   • React Context detected"
fi

if grep -r "useQuery\|useMutation\|tanstack-query" . --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | head -1 > /dev/null; then
  echo "   • TanStack Query detected"
fi

if grep -r "swr\|useSWR" . --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | head -1 > /dev/null; then
  echo "   • SWR detected"
fi

if grep -r "Atom\|atom\|useAtom" . --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | head -1 > /dev/null; then
  echo "   • Jotai detected"
fi

if grep -r "signal\|useSignal" . --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | head -1 > /dev/null; then
  echo "   • Signals detected"
fi

echo ""

# Detect error handling patterns
echo "⚠️  Error Handling Patterns:"
echo "----------------------------"

if grep -r "Result<\|Result<T" . --include="*.ts" --include="*.tsx" 2>/dev/null | head -1 > /dev/null; then
  echo "   • Result<T, E> type pattern detected"
fi

if grep -r "throw new Error" . --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" 2>/dev/null | head -1 > /dev/null; then
  echo "   • Exception throwing detected"
fi

if grep -r "try.*{" . --include="*.ts" --include="*.tsx" --include="*.js" --include="*.py" 2>/dev/null | head -1 > /dev/null; then
  echo "   • try-catch blocks detected"
fi

if grep -r "errorBoundary\|ErrorBoundary" . --include="*.ts" --include="*.tsx" --include="*.js" 2>/dev/null | head -1 > /dev/null; then
  echo "   • React Error Boundaries detected"
fi

echo ""

# Detect component patterns (for frontend)
echo "🧩 Component Patterns:"
echo "----------------------"

if find . -name "*.tsx" -o -name "*.jsx" 2>/dev/null | head -1 > /dev/null; then
  # Function components
  FC_COUNT=$(grep -r "function [A-Z][a-zA-Z]*" . --include="*.tsx" --include="*.jsx" 2>/dev/null | wc -l)
  
  # Arrow function components
  AFC_COUNT=$(grep -r "const [A-Z][a-zA-Z]*.*=" . --include="*.tsx" --include="*.jsx" 2>/dev/null | grep "=>" | wc -l)
  
  # Class components
  CC_COUNT=$(grep -r "class.*extends.*Component" . --include="*.tsx" --include="*.jsx" 2>/dev/null | wc -l)
  
  # Hooks usage
  HOOKS_COUNT=$(grep -r "use[A-Z]" . --include="*.tsx" --include="*.jsx" 2>/dev/null | wc -l)
  
  echo "   Function components: $FC_COUNT"
  echo "   Arrow function components: $AFC_COUNT"
  echo "   Class components: $CC_COUNT"
  echo "   Custom hooks usage: $HOOKS_COUNT"
  
  if [ $HOOKS_COUNT -gt 0 ]; then
    echo "   → Hooks-based pattern detected"
  fi
fi

echo ""

# Detect naming conventions for variables
echo "🔤 Variable Naming Conventions:"
echo "--------------------------------"

SAMPLE_FILE=$(find $SAMPLE_DIRS -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.py" 2>/dev/null | head -1)

if [ -n "$SAMPLE_FILE" ] && [ -f "$SAMPLE_FILE" ]; then
  # Check const UPPER_SNAKE
  UPPER_SNAKE=$(grep -E "^[A-Z][A-Z_]+\s*=" "$SAMPLE_FILE" 2>/dev/null | head -3 || echo "")
  
  # Check camelCase
  CAMEL_CASE=$(grep -E "const [a-z][a-zA-Z0-9]*\s*=" "$SAMPLE_FILE" 2>/dev/null | head -3 || echo "")
  
  if [ -n "$UPPER_SNAKE" ]; then
    echo "   UPPER_SNAKE_CASE: used for constants"
  fi
  
  if [ -n "$CAMEL_CASE" ]; then
    echo "   camelCase: used for variables"
  fi
fi

echo ""

# Summary
echo "📋 Convention Summary:"
echo "----------------------"

if [ -n "$FILE_CONVENTION" ]; then
  echo "   File naming: $FILE_CONVENTION"
fi

exit 0
