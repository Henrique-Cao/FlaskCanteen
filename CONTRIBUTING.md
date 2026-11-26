# Contributing

Thank you for helping improve Canteen Order Rail. The Flask application and test suite are in [`canteenClaude/`](canteenClaude/); project guides are in [`docs/`](docs/).

## Set up the project

Follow [Getting started](docs/getting-started.md) to create a virtual environment and install application and test dependencies. From `canteenClaude/`, run the suite with:

```bash
python -m pytest
```

Add focused tests under `canteenClaude/tests/unit/` for isolated logic or `canteenClaude/tests/integration/` for routes, database behavior, and application flows. Reuse the fixtures in `tests/conftest.py`; tests must not use real customer data, the normal database, or the real upload directory.

## Before opening a change

- Keep changes focused and follow existing project patterns.
- Preserve the customer and staff workflows, and keep interactive controls clear and usable on touch screens.
- Update the relevant documentation when changing routes, request/response fields, models, configuration, or setup instructions.
- Run the relevant tests and include the results in your pull request.
- Do not commit credentials, private customer data, local databases, or uploaded customer content.

## Pull requests

Describe the user-visible change, note any configuration or data-model impact, and include test commands and results. For UI changes, include a screenshot when practical.

The project is licensed under the [MIT License](LICENSE).
