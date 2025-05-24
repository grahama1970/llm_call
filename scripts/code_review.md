```bash
# Generate a comprehensive AI code review for all changes since the last commit,
# including staged, unstaged, and new untracked files, using Gemini via uvx.
(
  echo "=== CHANGES SINCE LAST COMMIT (STAGED + UNSTAGED) ===" &&
  git diff HEAD &&
  echo -e "\n\n=== CURRENT CONTENTS OF CHANGED FILES ===" &&
  git diff --name-only HEAD | uvx files-to-prompt &&
  echo -e "\n\n=== NEW UNTRACKED FILES ===" &&
  git ls-files --others --exclude-standard | uvx files-to-prompt
) | uvx --with llm-gemini llm -m gemini-2.5-pro-preview-05-06 -o google_search 1 -s 'You are a senior engineer and team lead. Review all changes since the last commit, including new files and modifications. Provide a comprehensive code review as if this were a GitHub comment.' > comprehensive-review-gemini.md && echo 'Comprehensive review saved to comprehensive-review-gemini.md'
```