# AGENT Guidelines

- Before committing, run Python syntax check:
  `python -m py_compile $(git ls-files '*.py')`
- Ensure frontend builds successfully:
  `cd frontend && npm install && npm run build`
- Update README when environment variables or commands change.

## Дополнительные требования
- Install dependencies before running tests:
  `pip install -r api/requirements.txt`
- Run tests for backend and frontend:
  `pytest` and `npm test`
- Project layout:
  `api/` contains FastAPI application, `frontend/` holds React UI; start both via `run.py`
- For offline environments store wheels/npm packages locally or use a mirror of PyPI/NPM.
