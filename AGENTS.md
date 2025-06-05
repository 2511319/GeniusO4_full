# AGENT Guidelines

- Before committing, run Python syntax check:
  `python -m py_compile $(git ls-files '*.py')`
- Ensure frontend builds successfully:
  `cd frontend && npm install && npm run build`
- Update README when environment variables or commands change.
