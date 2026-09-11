# Contributing

`dev` is the integration branch; `main` contains only validated releases. Use `feature/PDE-XXX-description`, `fix/PDE-XXX-description`, or the corresponding `docs`, `test`, `refactor`, and `chore` prefixes. Commits use `[AREA][PDE-XXX] concise English description`.

Run migrations, `ruff check .`, `pytest`, `python -m app.evaluation.run`, `npm run lint`, and `npm run build` before integration. Do not commit secrets, runtime databases, or automated-authorship metadata.

