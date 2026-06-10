---
name: portable-path-remediation
description: Systematic approach to replacing hardcoded absolute paths (e.g., /home/user/project) with portable relative paths across shell scripts, TypeScript, JSON, and Python files
source: auto-skill
extracted_at: '2026-06-10T05:56:37.736Z'
---

# Portable Path Remediation Workflow

## When to Use
When a project was developed on a different machine and contains hardcoded absolute paths (e.g., `/home/z/my-project`, `C:\Users\someone\project`) that break when cloned or moved to a new environment.

## Procedure

### 1. Find All Hardcoded Paths
Use `grep_search` with the pattern matching the old path prefix:

```
grep_search pattern="/home/z/"         # Linux/Mac origins
grep_search pattern="C:\\\\Users\\\\"    # Windows origins
```

This will surface paths in code AND documentation. Note which files are code (`.sh`, `.ts`, `.py`, `.json`) vs documentation (`.md`).

### 2. Categorize Files by Type
Each file type needs a different portability strategy:

| File Type | Strategy |
|-----------|----------|
| Shell scripts (`.sh`) | Use `cd "$(dirname "$0")"` or `cd "$(dirname "$0")/../.."` |
| TypeScript/Node (`.ts`, `.js`) | Use `path.resolve(__dirname, '../../backend')` or `path.resolve(process.cwd(), 'backend')` |
| Python (`.py`) | Use `Path(__file__).parent` or `os.getcwd()` |
| JSON (`package.json`) | Remove `cd /path` from scripts; run commands directly (npm scripts run in the package.json directory by default) |
| Documentation (`.md`) | Can leave as-is (historical record) OR update if they contain active instructions |

### 3. Apply Fixes by File Type

#### Shell Scripts (`.sh`)
**Before:**
```bash
cd /home/z/my-project/backend
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**After:**
```bash
cd "$(dirname "$0")"
exec python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
```

For scripts in subdirectories that need to reach the project root:
```bash
cd "$(dirname "$0")/../../backend"
```

#### TypeScript/Node.js (`.ts`, `.js`)
**Before:**
```typescript
const backendDir = '/home/z/my-project/backend';
const pythonPath = '/home/z/my-project/backend/.venv/bin/python3';
```

**After (child process cwd):**
```typescript
const backendDir = path.resolve(__dirname, '../../backend');
const pythonPath = process.env.CONTAEC_PYTHON_PATH || 'python3';
```

**After (Next.js API route - process.cwd):**
```typescript
const backendDir = path.resolve(process.cwd(), 'backend');
```

Key considerations for TypeScript:
- `__dirname` = directory of the current file (works in Node/bun runtime)
- `process.cwd()` = current working directory (works in Next.js API routes)
- Make configurable paths overridable via env vars: `process.env.CONTAEC_PYTHON_PATH || 'python3'`
- Use `path.resolve()` not string concatenation

#### Python (`.py`)
**Before:**
```python
BASE_DIR = "/home/z/my-project/backend"
DATA_DIR = "/home/z/my-project/backend/data"
```

**After:**
```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
```

#### package.json
**Before:**
```json
{
  "scripts": {
    "dev": "cd /home/z/my-project/backend && python3 -m uvicorn main:app --reload"
  }
}
```

**After:**
```json
{
  "scripts": {
    "dev": "python3 -m uvicorn main:app --reload"
  }
}
```

Note: npm/bun scripts always execute in the directory containing `package.json`, so the `cd` is unnecessary.

### 4. Verify No Remaining Hardcoded Paths in Code
Run `grep_search` again scoped to code files only:

```
grep_search pattern="/home/z/" glob="*.{sh,ts,tsx,js,json,py}"
```

Documentation files (`.md`) can retain old paths as historical records.

### 5. Test Key Entry Points
After fixing paths, verify:
- Shell scripts can find their target directories
- TypeScript child processes spawn in the correct working directory
- Python resolves its data directories correctly
- npm/bun scripts run without path errors

## Common Pitfalls

1. **Confusing `__dirname` with `process.cwd()`**: In Next.js API routes, `__dirname` may not be reliable. Use `process.cwd()` for project-root-relative paths.

2. **String concatenation instead of path resolution**: Always use `path.resolve()` (JS) or `Path / "subdir"` (Python), never string concatenation like `__dirname + '/../backend'`.

3. **Forgetting to update import references**: When a script's working directory changes, relative imports within that script may also need adjustment.

4. **Over-fixing documentation**: Historical `.md` files (worklogs, agent context) contain paths as records of past work. These don't need updating unless they contain active setup instructions.

5. **Hardcoded Python paths**: Instead of `/home/z/.venv/bin/python3`, use `python3` or `process.env.CONTAEC_PYTHON_PATH || 'python3'` to allow environment override.
