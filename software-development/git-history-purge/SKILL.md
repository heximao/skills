---
name: git-history-purge
description: Purge all previous Git commit history while preserving the current file state using the orphan branch method.
tags: [git, history, cleanup, performance]
---

# Clean Git History (Keep Current State)

This skill provides a procedure for purging all previous Git commit history while preserving the current file state. This is useful for reducing repository size, removing sensitive data from history, or speeding up slow Git UIs.

## Trigger
- User wants to "reset" a Git repository's history.
- Git UI (VS Code, SourceTree) is slow due to long history.
- Repository contains old large files that need to be purged completely.

## Procedure

1. **Check out an orphan branch**
   This creates a new branch with no parent commits.
   ```bash
   git checkout --orphan latest_branch
   ```

2. **Stage all files**
   ```bash
   git add -A
   ```

3. **Commit the changes**
   This becomes the new initial commit.
   ```bash
   git commit -am "Initial commit (history purged)"
   ```

4. **Delete the old main branch**
   Ensure you know the name of the old branch (usually `main` or `master`).
   ```bash
   git branch -D main
   ```

5. **Rename the orphan branch to main**
   ```bash
   git branch -m main
   ```

6. **Force push to remote (Caution!)**
   Only do this if you are the sole owner or have coordinated with the team.
   ```bash
   git push -f origin main
   ```

## Pitfalls
- **UI Cache**: Editors like VS Code or Obsidian may still show old history until restarted or the window is reloaded.
- **Parent Repositories**: If the `.git` folder is in a parent directory, running these commands inside a subdirectory might not target the correct repository. Always verify the `.git` location with `ls -la`.
- **Data Loss**: This is a destructive operation for history. Ensure a backup of the `.git` folder exists if there's any chance you need old commits back.

## Verification
- Run `git log` to ensure only one commit exists.
- Check disk space of the `.git` folder (should be significantly smaller if large files were removed).
