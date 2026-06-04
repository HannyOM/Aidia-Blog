# AIDIA - Flask Production Blog App

A production-ready blog application built with Flask, featuring a rich text editor, role-based access control, user authentication, and a responsive UI.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Blog Publishing** — Create, edit, delete, and view blog posts with a WYSIWYG rich text editor
- **Draft/Publish Workflow** — Posts default to draft status; publish when ready
- **User Authentication** — Registration, login, and email confirmation via Flask-Security
- **Role-Based Access Control** — Automatic "editor" role assignment; admin/editor permissions for content management
- **Author Ownership** — Only post authors can edit or delete their own posts
- **User Profiles** — Public profile pages with post history and draft visibility (owner-only)
- **Full-Text Search** — Search across published post titles and content
- **Rich Text Editor** — TipTap-powered editor with bold, italic, underline, headings, lists, blockquotes, links, code, and more
- **Responsive UI** — Mobile-friendly design built with Tailwind CSS and Flowbite
- **Health Check** — Built-in `/health` endpoint for monitoring database connectivity

## Tech Stack

### Backend

| Technology | Purpose |
|------------|---------|
| Flask 3.1+ | Web framework |
| Flask-Security 5.7 | Authentication & authorization |
| Flask-SQLAlchemy 3.1 | ORM database layer |
| Flask-Migrate 4.1 | Database migrations (Alembic) |
| Flask-WTF 1.2 | Form handling with CSRF protection |
| PostgreSQL 16 | Relational database |
| SQLAlchemy 2.0 | ORM with modern Mapped syntax |
| Argon2 | Password hashing |
| Resend | Email service integration |
| Gunicorn | Production WSGI server |
| Bleach | HTML sanitization |

### Frontend

| Technology | Purpose |
|------------|---------|
| Tailwind CSS 3.4 | Utility-first CSS framework |
| Flowbite 2.5 | Tailwind component library |
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

   The application will be available at `http://localhost:5000`.

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | Yes | `development` or `production` |
| `SECRET_KEY` | Yes | Flask session secret key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECURITY_PASSWORD_SALT` | Yes | Argon2 password hashing salt |
| `RESEND_API_KEY` | Yes | Resend.com API key for emails |
| `RESEND_FROM_EMAIL` | Yes | Verified sender email address |
| `PORT` | No | Port for production server (default: 8080) |

### Configuration Classes

The app uses environment-based configuration switching:

- **DevelopmentConfig** — Debug mode enabled, relaxed cookie security
- **ProductionConfig** — Debug disabled, secure cookies, same-site lax policy

## Usage

### User Roles

- **Anonymous users** — Can browse published articles, search, and view public profiles
- **Registered users** — Automatically assigned "editor" role upon registration
- **Editors** — Can create, edit, and delete their own posts
- **Admins** — Full access to all content management features

### Creating Posts

1. Log in to your account
2. Navigate to `/new` or click "New Post" in the navigation
3. Use the TipTap rich text editor to compose your post
4. Optionally check "Publish immediately" to make the post public
5. Click "Add Post" to save

Unpublished posts are visible only to their author.

### User Profiles

- Public profiles are accessible at `/profile/<username>`
- Shows user info, published posts, and drafts (visible only to the profile owner)
- Edit your profile at `/profile/edit`

## Testing

The test suite uses Docker-based PostgreSQL via testcontainers for isolation.

### Run all tests

```bash
pytest
```

### Run with verbose output

```bash
pytest -v
```

### Run specific test file

```bash
pytest tests/test_blog.py
```

### Run specific test function

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
| `create_user` | Creates and returns a test user with "editor" role |
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

### Rollback last migration

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
- Python 3.12-slim base
- Node.js 20.x for frontend asset building
- Automatic migration execution on startup
- Gunicorn with 4 workers and 120s timeout

### Railway

Deploy with one click using the included `railway.json` configuration.

### Heroku / Render

The included `Procfile` supports Heroku-style deployments:

```
release: alembic upgrade head
web: gunicorn --bind 0.0.0.0:$PORT wsgi:app
```

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) provides:

1. **Test** — Runs pytest against PostgreSQL 16 service container
2. **Build** — Builds Docker image with Trivy security scanning (HIGH/CRITICAL thresholds)
3. **Deploy** — Deploys to Railway via CLI with health check verification
4. **Backup** — Automated PostgreSQL backups using `pg_dump` + gzip (7-day retention)

## API Reference

### Health Check

```
GET /health
```

Returns database connectivity status:

```json
{ "status": "healthy" }
```

### User Info API

```
GET /api/user/<user_id>
```

Returns public user information:

```json
{
  "username": "example_user",
  "joined": "Jun 04, 2026",
  "roles": ["editor"],
  "post_count": 5
}
```

## Routes

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | No | Homepage with featured post and latest articles |
| GET | `/post/<post_id>` | No | View single post |
| GET | `/articles` | No | All published articles |
| GET | `/search?q=<query>` | No | Search published posts |
| GET | `/new` | Yes | New post form |
| POST | `/add` | Yes | Create new post |
| GET | `/edit/<post_id>` | Yes | Edit post (author only) |
| POST | `/save/<post_id>` | Yes | Save edited post |
| GET | `/delete/<post_id>` | Yes | Delete post (author only) |
| GET | `/profile/<username>` | No | User profile page |
| GET/POST | `/profile/edit` | Yes | Edit user profile |
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

- **User ↔ Role**: Many-to-many via `roles_users` junction table (CASCADE delete)
- **User → Post**: One-to-many (`Post.author` backref)

## Backup

Automated database backups are handled by `scripts/backup.sh`:

- Uses `pg_dump` to create SQL backups
- Compresses with gzip
- Auto-deletes backups older than 7 days

Manual backup:

```bash
bash scripts/backup.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests to ensure they pass (`pytest`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License.
