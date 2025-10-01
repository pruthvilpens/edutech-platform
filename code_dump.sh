#!/bin/bash
# code_dump.sh
# Generate a tree + code dump of the project for LLM context

OUTPUT="code_dump.txt"

# 1. Print full tree structure (exclude heavy/unnecessary dirs)
echo "### Project Tree" > "$OUTPUT"
tree -I "node_modules|.git|.next|dist|build|.turbo|venv|__pycache__" >> "$OUTPUT"

# 2. Print file contents (ignoring irrelevant files)
echo -e "\n\n### File Contents\n" >> "$OUTPUT"

find . \
  -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/.next/*" \
  ! -path "*/dist/*" \
  ! -path "*/build/*" \
  ! -path "*/.turbo/*" \
  ! -path "*/venv/*" \
  ! -path "*/__pycache__/*" \
  ! -name "*.log" \
  ! -name "*.md" \
  ! -iname "README*" \
  ! -name ".gitignore" \
  ! -name "package-lock.json" \
  ! -name "yarn.lock" \
  ! -name "pnpm-lock.yaml" \
  ! -name "*.sql" \
  ! -name "*.sh" \
  ! -name "*.txt" \
  ! -name "*.ico" \
  ! -name "*.svg" \
  ! -name "*.png" \
  ! -name "*.jpg" \
  ! -name "*.jpeg" \
  ! -name "*.gif" \
  ! -name "*.pdf" \
  ! -name "*.ttf" \
  ! -name "*.otf" \
  ! -name "*.woff" \
  ! -name "*.woff2" \
  ! -name "*.eot" \
  | sort | while read -r file; do
    echo -e "\n\n--- FILE: $file ---\n" >> "$OUTPUT"
    cat "$file" >> "$OUTPUT"
done

echo "✅ Code dump written to $OUTPUT"
