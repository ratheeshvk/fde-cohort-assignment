# Employee Performance Review Management System

FastAPI backend, PostgreSQL database, and React (Vite) frontend.

```
backend/    FastAPI app (API -> Service -> Repository -> DB, Pydantic models)
frontend/   React + TypeScript app (frontEndReact/)
sql/        Schema and seed scripts
```

## Branch naming

Branch off `main` and use one of these three prefixes only:

| Prefix | Use for | Example |
|---|---|---|
| `feature/` | New functionality or enhancements | `feature/review-pagination` |
| `bug/` | Fixing something that doesn't work as intended | `bug/review-periods-seed` |
| `hotfix/` | Urgent fix for a broken `main` (build fails, app won't start) | `hotfix/header-import` |

Rules:

- Format: `<prefix>/<short-description>`
- Lowercase letters, numbers, and hyphens only. No spaces, underscores, or names.
- Keep it short and descriptive (2-5 words).
- Don't commit directly to `main`; open a pull request from your branch.

Valid names match: `^(feature|bug|hotfix)/[a-z0-9]+(-[a-z0-9]+)*$`

```bash
git checkout main
git pull
git checkout -b feature/review-pagination
```

## Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 14+

## 1. Database

Create a database and load the schema and seed data:

```bash
createdb fde

psql fde -f sql/projectschema.sql
psql fde -f sql/seed_employees.sql
psql fde -f sql/seed_review_periods.sql
psql fde -f sql/seed_reviews.sql
```

> Note: `projectschema.sql` drops and recreates the tables, so re-running it wipes existing data.

## 2. Backend

Create a `.env` file at the **repository root** (not inside `backend/`):

```bash
cp backend/.env.example .env
```

Edit `DATABASE_URL` to match your database:

```
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/fde
```

Also set the auth values in the same file:

| Variable | Purpose |
|---|---|
| `JWT_SECRET` | Secret used to sign login tokens. Use a long random string. |
| `JWT_EXPIRE_MINUTES` | How long a login lasts (default `480`). |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | The first admin account, created by `init_db.py`. |
| `CORS_ORIGINS` | Comma-separated frontend origins allowed to send the login cookie (default `http://localhost:5173`). |
| `COOKIE_SECURE` | Set to `true` once the site runs on HTTPS. |

Install dependencies, create the first admin, and start the API:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python init_db.py                # creates the admin from ADMIN_USERNAME / ADMIN_PASSWORD
uvicorn main:app --reload
```

There is no sign-up endpoint. `init_db.py` is safe to re-run: an existing admin is left unchanged, so it never resets a password.

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

Run the tests:

```bash
pytest
```

## 3. Frontend

In a second terminal:

```bash
cd frontend/frontEndReact
npm install
npm run dev
```

Open http://localhost:5173. The app calls the API at `http://localhost:8000` by default; set `VITE_API_URL` to point it elsewhere.

Production build: `npm run build` (output in `dist/`).

## APIs

### Admin auth

Login sets an httponly `access_token` cookie (a signed JWT). Every other endpoint requires that cookie and returns `401 NOT_AUTHENTICATED` without it.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Log in with `{"username", "password"}`. Returns the admin (`id`, `username`) and sets the cookie. `401 INVALID_CREDENTIALS` on a wrong username or password. |
| POST | `/api/auth/logout` | Clear the cookie. Returns `204`; works even if the token has expired. |
| GET | `/api/auth/me` | Return the logged-in admin, or `401` if not logged in. |

```bash
# log in and save the cookie
curl -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "change-me"}'

# send the cookie on later requests
curl -b cookies.txt http://localhost:8000/api/auth/me
```

### Protected endpoints (admin login required)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/employees` | List all employees |
| GET | `/employees/{employee_id}` | Get one employee by code, e.g. `EMP101` (case-insensitive) |
| GET | `/review-periods` | List all review periods |
| GET | `/reviews` | List reviews. Optional query params: `employee_id`, `period_id` |
| GET | `/reviews/{review_id}` | Get one review |
| POST | `/api/reviews` | Submit a new review |

### Example: submit a review

```bash
curl -b cookies.txt -X POST http://localhost:8000/api/reviews \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": 1,
    "period_id": 9,
    "quality_rating": 4,
    "delivery_rating": 5,
    "teamwork_rating": 4,
    "comments": "Strong performer with great teamwork."
  }'
```

Ratings must be between 1 and 5. The API returns `201` with the saved review, `409` if the employee already has a review for that period, and `404` if the employee or period doesn't exist.
