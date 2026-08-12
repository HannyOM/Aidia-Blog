# AIDIA - Flask Production Blog App

AIDIA is a production-ready blog application. It is built with Flask. It provides a rich text editor, role-based access control, user authentication, and a responsive UI.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Blog Publishing** — Create blog posts with a WYSIWYG rich text editor. Edit, delete, and view posts.
- **Draft/Publish Workflow** — New posts have draft status. Publish a post when it is ready.
- **User Authentication** — Users can register, log in, and confirm their email. Flask-Security handles authentication. After registration, the app tells the user to check their inbox (and spam folder) for the confirmation link.
- **Email Verification** — The app rejects invalid email addresses at registration. It verifies the address with the Mailboxlayer API before it creates the account.
- **Role-Based Access Control** — Each new user receives the "editor" role automatically. Editors and admins can manage content.
- **Author Ownership** — Only the author can edit or delete a post.
- **User Profiles** — Each user has a public profile page. The page shows the user's published posts. Drafts are visible only to the profile owner.
- **Contact Authors** — Visitors can send a message to a user from their profile page. The app emails the message to you.
- **Keyword Search** — Users can search published post titles and content by keyword.
- **Rich Text Editor** — The TipTap editor provides bold, italic, underline, headings, lists, blockquotes, links, code, and other formats.
- **Responsive UI** — The design works on mobile devices. It uses Tailwind CSS.
- **Health Check** — The `/health` endpoint reports database connectivity.

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| Flask 3.1+ | Web framework |
| Flask-Security 5.7 | Authentication and authorization |
| Flask-SQLAlchemy 3.1 | ORM database layer |
| Flask-Migrate 4.1 | Database migrations (Alembic) |
| Flask-WTF 1.2 | Form handling with CSRF protection |
| PostgreSQL 16 | Relational database |
| SQLAlchemy 2.0 | ORM with modern Mapped syntax |
| Argon2 | Password hashing |
| Resend | Email service integration |
| Mailboxlayer | Email verification at registration |
| Gunicorn | Production WSGI server |

### Frontend

| Technology | Purpose |
|------------|---------|
| Tailwind CSS 3.4 | Utility-first CSS framework |
| TipTap 2.27 | Rich text editor framework |
| Vite 5.4 | JavaScript bundler |
| PostCSS + Autoprefixer | CSS processing |

## Project Structure

```
flask-production-blog-app/
├── bloggr/                          # Main application package
│   ├── __init__.py                  # App factory & configuration
│   ├── models.py                    # SQLAlchemy ORM models
│   ├── blog.py                      # Blueprint with route handlers
│   ├── roles.py                     # Role assignment signal handlers
│   ├── email_service.py             # Resend.com email integration
│   ├── templates/                   # Jinja2 HTML templates
│   │   ├── base.html                # Base layout template
│   │   ├── blog/                    # Blog page templates
│   │   ├── security/                # Auth page templates
│   │   └── components/              # Reusable UI components
│   └── static/                      # Static assets (CSS, JS)
├── tests/                           # Test suite
│   ├── conftest.py                  # Pytest fixtures & helpers
│   ├── test_blog.py                 # Route & feature tests
│   ├── test_models.py               # Model relationship tests
│   └── test_factory.py              # App factory tests
├── migrations/                      # Alembic database migrations
├── scripts/
│   └── backup.sh                    # PostgreSQL backup script
├── .github/workflows/ci-cd.yml      # GitHub Actions pipeline
├── Dockerfile                       # Production Docker image
├── pyproject.toml                   # Python dependencies
├── package.json                     # Node.js dependencies
├── vite.config.js                   # Vite bundler config
├── tailwind.config.js               # Tailwind CSS config
├── railway.json                     # Railway deployment config
├── Procfile                         # Heroku-style process definition
├── wsgi.py                          # WSGI entry point
└── start.sh                         # Container entrypoint
```

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Node.js 20+ and npm
- Docker (for testing)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd flask-production-blog-app
   ```

2. **Install Python dependencies**

   ```bash
   pip install -e ".[dev]"
   ```

3. **Install Node.js dependencies**

   ```bash
   npm install
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:

   ```env
   FLASK_ENV=development
   SECRET_KEY=<your-secret-key>
   DATABASE_URL=postgresql://user:password@localhost:5432/aidia_blog
   SECURITY_PASSWORD_SALT=<your-password-salt>
   RESEND_API_KEY=<your-resend-api-key>
   RESEND_FROM_EMAIL=<your-verified-sender-email>
   MAILBOXLAYER_ACCESS_KEY=<your-mailboxlayer-api-key>
   ```

5. **Build frontend assets**

   ```bash
   npm run build-css
   npm run build-js
   ```

6. **Run database migrations**

   ```bash
   flask db upgrade
   ```

7. **Start the development server**

   ```bash
   flask run
   ```

   The application is available at `http://localhost:5000`.

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | No | Selects the configuration class. Use `development` or `production`. Default: `development` |
| `SECRET_KEY` | Yes | Flask session secret key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECURITY_PASSWORD_SALT` | Yes | Argon2 password hashing salt |
| `SECURITY_EMAIL_SUBJECT_REGISTER` | No | Subject line for the registration email |
| `RESEND_API_KEY` | No | Resend API key. Required only for email features |
| `RESEND_FROM_EMAIL` | No | Verified sender email address. Required only for email features |
| `MAILBOXLAYER_ACCESS_KEY` | No | Mailboxlayer API key. Required only for email verification |
| `MAILBOXLAYER_API_URL` | No | Mailboxlayer API endpoint. Default: `https://apilayer.net/api/check` |
| `PORT` | No | Port for the production server (default: 8080) |

### Configuration Classes

The app selects its configuration class from the environment:

- **DevelopmentConfig** — Debug mode is enabled. Cookie security is relaxed.
- **ProductionConfig** — Debug mode is disabled. Cookies use secure settings. Same-site policy is lax.

## Usage

### User Roles

- **Anonymous users** — Can browse published articles, search, view public profiles, and send messages to users.
- **Registered users** — Receive the "editor" role when they register.
- **Editors** — Can create, edit, and delete their own posts.
- **Admins** — Can create and publish posts. The author-only rule for editing and deleting applies to them too.

### Creating Posts

1. Log in to your account.
2. Navigate to `/new`. Or click "New Post" in the navigation.
3. Use the TipTap rich text editor to compose the post.
4. Check "Publish immediately" to make the post public. This step is optional.
5. Click "Add Post" to save the post.

Unpublished posts are visible only to their author.

### User Profiles

- Public profiles are at `/profile/<username>`.
- The profile shows user information and published posts. It shows drafts only to the profile owner.
- Edit the profile at `/profile/edit`.
- Visitors can send a message to the user from the profile page. The app emails the message to the user.

## Testing

The tests use PostgreSQL from Docker. The testcontainers library provides the database. Each test run is isolated from other runs.

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run a specific test file

```bash
pytest tests/test_blog.py
```

### Run a specific test function

```bash
pytest tests/test_blog.py::test_index
```

### Run tests matching a pattern

```bash
pytest -k "test_login"
```

### Test Fixtures

| Fixture | Description |
|---------|-------------|
| `client` | Flask test client for HTTP requests |
| `app` | Flask application instance |
| `db` | SQLAlchemy database instance |
| `create_user` | Creates and returns a test user with the "editor" role |
| `auth` | Helper with `.login()` and `.logout()` methods |

## Database Migrations

### Create a new migration

```bash
flask db migrate -m "description of changes"
```

### Apply migrations

```bash
flask db upgrade
```

### Roll back the last migration

```bash
flask db downgrade
```

## Deployment

### Docker

Build and run the Docker image:

```bash
docker build -t aidia-blog .
docker run -p 8080:8080 --env-file .env aidia-blog
```

The Docker image includes:

- Uses the Python 3.12-slim base image.
- Uses Node.js 20.x to build frontend assets.
- Runs database migrations when the app starts.
- Runs Gunicorn with 4 workers and a 120-second timeout.

### Railway

Use the included `railway.json` file. It deploys the app with one click.

### Heroku / Render

The included `Procfile` supports Heroku-style deployments:

```
release: alembic upgrade head
web: gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### CI/CD Pipeline

The GitHub Actions workflow is at `.github/workflows/ci-cd.yml`. It provides:

1. **Test** — Runs pytest against a PostgreSQL 16 service container.
2. **Build** — Builds a Docker image. Trivy scans the image for HIGH and CRITICAL vulnerabilities.
3. **Deploy** — Deploys to Railway with the Railway CLI. Verifies the deployment with a health check.
4. **Backup** — Backs up PostgreSQL with `pg_dump` and gzip. Keeps backups for 7 days.

## API Reference

### Health Check

```
GET /health
```

Returns the database connectivity status:

```json
{ "status": "healthy", "database": "connected" }
```

The endpoint returns HTTP 503 with `{"status": "unhealthy"}` when the database is not reachable.

### User Info API

```
GET /api/user/<user_id>
```

Returns public user information:

```json
{
  "username": "example_user",
  "joined": "June 04, 2026",
  "roles": ["editor"],
  "post_count": 5
}
```

## Routes

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | No | Homepage with a featured post and latest articles |
| GET | `/post/<post_id>` | No | View a single post |
| GET | `/articles` | No | All published articles |
| GET | `/search?q=<query>` | No | Search published posts |
| GET | `/new` | Yes | New post form |
| POST | `/add` | Yes | Create a new post (GET shows the form) |
| GET | `/edit/<post_id>` | Yes | Edit a post (author only; POST saves via `/save`) |
| POST | `/save/<post_id>` | Yes | Save an edited post |
| GET | `/delete/<post_id>` | Yes | Delete a post (author only) |
| GET | `/profile/<username>` | No | User profile page |
| GET/POST | `/profile/edit` | Yes | Edit a user profile |
| POST | `/message/<username>` | No | Send a message to a user |
| GET | `/check-email` | No | Confirmation reminder after registration |
| GET | `/api/user/<user_id>` | No | User info JSON API |
| GET | `/health` | No | Health check endpoint |

Flask-Security also provides `/login`, `/logout`, `/register`, and `/confirm` routes.

## Database Models

### User

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `username` | String(20) | Unique username |
| `email` | String(100) | Unique email address |
| `password` | String(255) | Hashed password (Argon2) |
| `active` | Boolean | Account active status |
| `fs_uniquifier` | String(255) | Flask-Security unique identifier |
| `confirmed_at` | DateTime | Email confirmation timestamp |

### Role

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | String(80) | Unique role name |
| `description` | String(255) | Role description |

### Post

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `title` | String(50) | Post title |
| `content` | Text | Post content (HTML) |
| `author_id` | Integer | Foreign key to User |
| `date` | Date | Publication date |
| `is_published` | Boolean | Published status (default: False) |

### Relationships

- **User ↔ Role**: Many-to-many via the `roles_users` junction table (CASCADE delete).
- **User → Post**: One-to-many (`Post.author` backref).

## Backup

The script `scripts/backup.sh` creates automated database backups:

- Uses `pg_dump` to create SQL backups.
- Compresses the backups with gzip.
- Deletes backups that are older than 7 days.

Manual backup:

```bash
bash scripts/backup.sh
```

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Run the tests to make sure they pass (`pytest`).
4. Commit your changes (`git commit -m 'Add amazing feature'`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request.

## License

This project is licensed under the MIT License.
