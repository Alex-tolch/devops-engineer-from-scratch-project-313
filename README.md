### CI status

[![CI](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml/badge.svg)](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions/workflows/ci.yml)

## Running the application

Requirements: [uv](https://docs.astral.sh/uv/) (Python project manager).

1. Install dependencies (uv will create a virtual environment and install dependencies):

   ```bash
   uv sync
   ```

2. Run the application:
   ```bash
   make run
   ```

The application will be available at http://localhost:8080. The `GET /ping` route returns the string `pong`.

To verify (with the app running): `curl http://localhost:8080/ping` — expected response: `pong`.

## Docker

Build the image:

```bash
docker build -t devops-app .
```

Run the container:

```bash
docker run -p 8080:8080 devops-app
```

The app will be available at http://localhost:8080.

## Development

Run tests: `make test`

Run linter (Ruff): `make lint`

---

### Hexlet tests and linter status:

[![Actions Status](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Alex-tolch/devops-engineer-from-scratch-project-313/actions)
