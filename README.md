# Adbrew TODO App

A TODO app with a React frontend, a Django REST API and MongoDB persistence, running in the
provided three-container Docker setup.

- **React** (hooks only) lists TODOs from the API and adds new ones; after every successful
  add, the list is re-fetched from the backend.
- **Django + DRF** exposes `GET /todos` and `POST /todos`, storing data in MongoDB through
  pymongo. No Django models, serializers or SQLite are used.

## Running it

**1. Point compose at the source folder** (the path to this repo's `src` directory):

```bash
# macOS / Linux
export ADBREW_CODEBASE_PATH="/path/to/this/repo/src"
```
```powershell
# Windows PowerShell (quotes needed if the path contains spaces)
$env:ADBREW_CODEBASE_PATH = "C:\path\to\this\repo\src"
```

**2. Build and start:**

```bash
docker-compose build      # first build takes a while
docker-compose up -d
docker ps                 # api, app and mongo should be Up
```

**3. Open** http://localhost:3000 (the app) or http://localhost:8000/todos (the API).

The `app` container runs `yarn install` on every start, so the first start can take a few
minutes. Follow progress with `docker logs -f app` until it prints `Compiled successfully!`.

## API

All responses use one envelope: `{"data": ...}` on success, `{"error": {...}}` on failure.

### `GET /todos`

```json
200 {"data": [{"id": "6719c0f2a1b2c3d4e5f60718", "description": "Learn Docker",
               "created_at": "2026-10-02T08:15:30.123000+00:00"}]}
```

TODOs are returned oldest first.

### `POST /todos`

```bash
curl -X POST http://localhost:8000/todos \
     -H "Content-Type: application/json" \
     -d '{"description": "Learn Docker"}'
```

```json
201 {"data": {"id": "...", "description": "Learn Docker", "created_at": "..."}}
```

`description` is required, must be a string, is trimmed, and must be 1–500 characters long.
Both `/todos` and `/todos/` are accepted.

### Errors

```json
{"error": {"code": "validation_error", "message": "Invalid request body.",
           "details": {"description": "This field may not be blank."}}}
```

| Status | `code` | When |
|---|---|---|
| 400 | `validation_error` | Missing, blank, non-string or too-long `description`, or a body that isn't a JSON object |
| 400 | `parse_error` | Malformed JSON |
| 405 | `method_not_allowed` | Any method other than GET/POST |
| 415 | `unsupported_media_type` | Body not sent as `application/json` |
| 503 | `database_unavailable` | MongoDB unreachable (fails after ~3s rather than hanging) |
| 500 | `database_error` / `internal_error` | Other database errors / unexpected errors (details are logged, never returned) |

## Architecture

### Backend (`src/rest/rest/`)

| Module | Responsibility |
|---|---|
| `views.py` | Thin HTTP layer: parse JSON, validate, call the repository, return a response. No `try/except`. |
| `validators.py` | Validates and cleans the request payload; raises `RequestValidationError` |
| `todo_repository.py` | The only code that knows the MongoDB collection and document shape. Maps documents to plain dicts and wraps pymongo errors in application exceptions. |
| `db.py` | One lazily created, shared `MongoClient` configured from `MONGO_HOST` / `MONGO_PORT` |
| `exceptions.py` | Application exceptions, free of Django, DRF and pymongo |
| `exception_handlers.py` | DRF exception handler that maps every exception to a status code and error envelope, and logs server-side failures |
| `responses.py` | Builders for the success and error envelopes |

```
POST /todos → TodoListView.post → validate_create_todo → TodoRepository.create_todo → MongoDB
                          any exception ↘ api_exception_handler → {"error": ...} + status
```

MongoDB document in `test_db.todos`:

```js
{ _id: ObjectId, description: String, created_at: ISODate /* UTC, set by the server */ }
```

### Frontend (`src/app/src/`)

| Module | Responsibility |
|---|---|
| `api/todosApi.js` | The only code that knows URLs and the envelope. Turns HTTP errors, network failures and malformed responses into one `ApiError` type. |
| `hooks/useTodos.js` | Server state (`todos`, `isLoading`, `error`), loading on mount, `refresh()`, and `addTodo()` (POST then re-fetch). Ignores out-of-order responses and responses arriving after unmount. |
| `components/TodoList.js` | Presentational: loading, empty, list, and error with Retry |
| `components/TodoForm.js` | Controlled input with client-side checks, submitting state, and inline server errors. Keeps the text when a submit fails. |
| `App.js` | Wires the hook to the two components |

The API base URL defaults to `http://localhost:8000`. It can be overridden with
`REACT_APP_API_URL`.

## Changes to the provided setup

- **Dockerfile.** The build no longer worked as provided. `FROM python:3.8` now resolves to
  Debian 12 (bookworm), but the MongoDB 4.4 packages the Dockerfile installs are built for
  Debian 10 (buster) and depend on `libssl1.1`, which bookworm doesn't ship. Changes:
  - The base image is pinned to `python:3.8-buster`.
  - apt points at `archive.debian.org`, because buster is end-of-life and its packages have
    moved there.
  - `easy_install pip` is removed: `easy_install` no longer exists, and pip is already in the
    image.

  The rest of the setup is unchanged: the same three containers, the same compose file, and
  the same MongoDB/pymongo versions.
- **`settings.py`.** Registered the exception handler. Removed a debug `print` and two unused
  imports.
- **`urls.py`.** The trailing slash is optional. The original `todos/` route made
  `POST /todos` fail with a 500, because Django's `APPEND_SLASH` can't redirect a POST.
