#!/usr/bin/env bash
# Architecture pattern detector - Dimension 2
# Usage: ./analyze-structure.sh [--json]
# Output: Detected architecture pattern and directory structure analysis

set -e

OUTPUT_JSON=false
if [ "$1" = "--json" ]; then
  OUTPUT_JSON=true
fi

echo "🏗 Architecture Pattern Detector"
echo "================================="
echo ""

# Detect project type
if [ -d "packages" ] || [ -d "apps" ]; then
  PROJECT_TYPE="monorepo"
elif [ -f "package.json" ] && grep -q '"workspaces"' package.json; then
  PROJECT_TYPE="monorepo"
else
  PROJECT_TYPE="single-package"
fi

# Detect architecture patterns
PATTERNS=()

# Check for MVC
if [ -d "app/controllers" ] || [ -d "controllers" ]; then
  PATTERNS+=("MVC")
fi

if [ -d "app/models" ] || [ -d "models" ]; then
  if [[ ! " ${PATTERNS[*]} " =~ "MVC" ]]; then
    PATTERNS+=("MVC")
  fi
fi

if [ -d "app/views" ] || [ -d "views" ]; then
  if [[ ! " ${PATTERNS[*]} " =~ "MVC" ]]; then
    PATTERNS+=("MVC")
  fi
fi

# Check for DDD
if [ -d "domain" ] || [ -d "Domain" ]; then
  PATTERNS+=("DDD")
fi

if [ -d "application" ] || [ -d "Application" ]; then
  if [[ ! " ${PATTERNS[*]} " =~ "DDD" ]]; then
    PATTERNS+=("DDD")
  fi
fi

if [ -d "infrastructure" ] || [ -d "Infrastructure" ]; then
  if [[ ! " ${PATTERNS[*]} " =~ "DDD" ]]; then
    PATTERNS+=("DDD")
  fi
fi

# Check for Clean Architecture
if [ -d "core" ] || [ -d "Core" ]; then
  PATTERNS+=("Clean Architecture")
fi

if [ -d "use-cases" ] || [ -d "usecase" ]; then
  if [[ ! " ${PATTERNS[*]} " =~ "Clean" ]]; then
    PATTERNS+=("Clean Architecture")
  fi
fi

# Check for Feature-Sliced
if [ -d "features" ] || [ -d "Features" ]; then
  PATTERNS+=("Feature-Sliced")
fi

if [ -d "entities" ] || [ -d "Entities" ]; then
  if [[ ! " ${PATTERNS[*]} " =~ "Feature" ]]; then
    PATTERNS+=("Feature-Sliced")
  fi
fi

# Check for Hexagonal/Ports & Adapters
if [ -d "ports" ] || [ -d "Ports" ]; then
  PATTERNS+=("Hexagonal")
fi

if [ -d "adapters" ] || [ -d "Adapters" ]; then
  if [[ ! " ${PATTERNS[*]} " =~ "Hexagonal" ]]; then
    PATTERNS+=("Hexagonal")
  fi
fi

# Check for Next.js App Router
if [ -d "app" ] && [ -f "next.config.js" ] || [ -f "next.config.mjs" ]; then
  PATTERNS+=("Next.js App Router")
fi

# Check for frontend
if [ -d "src/components" ] || [ -d "components" ]; then
  PATTERNS+=("Component-Based")
fi

if [ -d "src/pages" ] || [ -d "pages" ]; then
  PATTERNS+=("Page-Based")
fi

# Default to "Flat/Traditional" if no patterns detected
if [ ${#PATTERNS[@]} -eq 0 ]; then
  PATTERNS+=("Flat/Traditional")
fi

if $OUTPUT_JSON; then
  echo "{"
  echo "  \"projectType\": \"$PROJECT_TYPE\","
  echo "  \"patterns\": ["
  for i in "${!PATTERNS[@]}"; do
    if [ $i -gt 0 ]; then
      echo ","
    fi
    echo -n "    \"${PATTERNS[$i]}\""
  done
  echo ""
  echo "  ],"
else
  echo "📁 Project Type: $PROJECT_TYPE"
  echo ""
  echo "🏛 Detected Architecture Patterns:"
  for pattern in "${PATTERNS[@]}"; do
    echo "   • $pattern"
  done
  echo ""
fi

# Directory structure analysis
echo "📂 Directory Structure (top 3 levels):"
echo "--------------------------------------"
find . -maxdepth 3 -type d ! -path '*/node_modules/*' ! -path '*/.git/*' ! -path '*/\.*' 2>/dev/null | head -30 | while read dir; do
  depth=$(echo "$dir" | awk -F'/' '{print NF-1}')
  indent=""
  for ((i=1; i<depth; i++)); do
    indent="$indent  "
  done
  echo "${indent}📁 $(basename "$dir")/"
done

echo ""

# Detect source root
if [ -d "src" ]; then
  SOURCE_ROOT="src"
elif [ -d "lib" ]; then
  SOURCE_ROOT="lib"
elif [ -d "app" ]; then
  SOURCE_ROOT="app"
elif [ -d "packages" ]; then
  SOURCE_ROOT="packages/*/src"
fi

if [ -n "$SOURCE_ROOT" ]; then
  echo "📍 Detected Source Root: $SOURCE_ROOT"
  
  # Count files
  FILE_COUNT=$(find $SOURCE_ROOT -type f 2>/dev/null | wc -l)
  echo "   Total source files: $FILE_COUNT"
fi

echo ""

# Detect test organization
if [ -d "__tests__" ]; then
  TEST_PATTERN="__tests__ (co-located)"
elif [ -d "tests" ]; then
  TEST_PATTERN="tests (root)"
elif [ -d "test" ]; then
  TEST_PATTERN="test (root)"
elif [ -d "spec" ]; then
  TEST_PATTERN="spec (root)"
else
  TEST_PATTERN="Mixed or none detected"
fi

echo "🧪 Test Organization: $TEST_PATTERN"

if $OUTPUT_JSON; then
  echo ","
  echo "  \"sourceRoot\": \"$SOURCE_ROOT\","
  echo "  \"testPattern\": \"$TEST_PATTERN\","
  echo "  \"directories\": ["
  find . -maxdepth 3 -type d ! -path '*/node_modules/*' ! -path '*/.git/*' ! -path '*/\.*' 2>/dev/null | head -20 | while read dir; do
    echo "    \"$dir\","
  done
  echo "    null"
  echo "  ]"
  echo "}"
fi

exit 0
