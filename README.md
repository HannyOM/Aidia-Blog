# AIDIA

AIDIA is a "What to Build" platform. Users describe real problems from any industry and country. The community votes on how serious each problem is. Users propose solutions. The community votes on whether each solution is good.

## Features

- **Describe Problems** — Any registered user can describe a problem. They choose an industry and a country.
- **Severity Voting** — Registered users vote on whether a problem is worth solving. Each user has one vote per problem.
- **Propose Solutions** — Registered users propose a solution for a problem. A solution can use software, hardware, or both.
- **Solution Quality Voting** — Registered users vote on whether a solution is good. Each user has one vote per solution.
- **Problem Status** — The problem author or an admin sets the status: open, in progress, or solved.
- **Draft/Publish Workflow** — New problems have draft status. Publish a problem when it is ready.
- **Browse and Search** — Users browse problems. Search matches problem titles, content, industry, and country.
- **User Authentication** — Users can register, log in, and confirm their email. Flask-Security handles authentication.
- **Email Verification** — The app verifies email addresses with the Mailboxlayer API at registration.
- **User Profiles** — Public profiles show published problems. Drafts are visible only to the profile owner.
- **Contact Authors** — Visitors can send a message from a profile page. The app emails the message to the profile owner.
- **Comments** — Registered users can comment on published problems. The comment author, the problem author, or an admin can delete a comment.
- **Rotating Quotes** — The homepage masthead shows a rotating series of quotes.
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
├── bloggr/                    # Main application package
│   ├── __init__.py            # App factory and configuration
│   ├── models.py              # SQLAlchemy ORM models
│   ├── constants.py           # Industries, countries, and problem statuses
│   ├── blog.py                # Blueprint with route handlers
│   ├── roles.py               # Role assignment signal handlers
│   ├── email_service.py       # Resend.com email integration
│   ├── email_verification.py  # Mailboxlayer email verification
│   ├── forms.py               # Flask-WTF forms
│   ├── quotes.py              # Homepage rotating quotes
│   ├── templates/             # Jinja2 HTML templates
│   └── static/                # CSS and JS assets
├── tests/                     # Pytest test suite
├── migrations/                # Alembic database migrations
├── docs/                      # Detailed documentation
│   ├── API.md                 # Routes and API endpoints
│   ├── DATABASE.md            # Database models and relationships
│   └── DEPLOYMENT.md          # Deployment, migrations, and backup
├── scripts/
│   └── backup.sh              # PostgreSQL backup script
├── .github/workflows/ci-cd.yml # GitHub Actions pipeline
├── Dockerfile                 # Production Docker image
├── pyproject.toml             # Python dependencies
├── package.json               # Node.js dependencies
├── railway.json               # Railway deployment config
├── Procfile                   # Process definition
├── wsgi.py                    # WSGI entry point
└── start.sh                   # Container entrypoint
```

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Node.js 20+ and npm
- Docker (for testing)

### Installation

1. Clone the repository.

   ```bash
   git clone <repository-url>
   cd flask-production-blog-app
   ```

2. Install Python dependencies.

   ```bash
   pip install -e ".[dev]"
   ```

3. Install Node.js dependencies.

   ```bash
   npm install
   ```

4. Create a `.env` file in the project root. Set the environment variables listed in the [Environment Variables](#environment-variables) section.

5. Build the frontend assets.

   ```bash
   npm run build-css
   npm run build-js
   ```

6. Run the database migrations.

   ```bash
   flask db upgrade
   ```

7. Start the development server.

   ```bash
   flask run
   ```

   The application is available at `http://localhost:5000`.

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FLASK_ENV` | No | Selects the configuration class: `development` or `production`. Default: `development` |
| `SECRET_KEY` | Yes | Flask session secret key |
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECURITY_PASSWORD_SALT` | Yes | Argon2 password hashing salt |
| `SECURITY_EMAIL_SUBJECT_REGISTER` | No | Subject line for the registration email |
| `RESEND_API_KEY` | No | Resend API key. Required for email features |
| `RESEND_FROM_EMAIL` | No | Verified sender email address. Required for email features |
| `MAILBOXLAYER_ACCESS_KEY` | No | Mailboxlayer API key. Required for email verification |
| `MAILBOXLAYER_API_URL` | No | Mailboxlayer API endpoint. Default: `https://apilayer.net/api/check` |
| `PORT` | No | Port for the production server (default: 8080) |

## Configuration

The app selects its configuration class from the `FLASK_ENV` variable.

- **DevelopmentConfig** — Debug mode is enabled. Cookie security is relaxed.
- **ProductionConfig** — Debug mode is disabled. Cookies use secure settings. Same-site policy is lax.

## Usage

| Role | Capabilities |
|------|--------------|
| Anonymous | Browse published problems, search, view profiles, view comments and vote counts, and send messages. Must log in to comment or vote. |
| Registered user | Receives the "editor" role on registration. Can describe problems, comment, vote on problem severity, propose solutions, and vote on solution quality. |
| Editor | Can create, edit, and delete their own problems. Can update the status of their own problems. |
| Admin | Can update the status of any problem. The author-only rule for editing and deleting still applies. |

## Testing

The tests use PostgreSQL from Docker. The testcontainers library provides the database. Each test run is isolated from other runs.

```bash
pytest
```

## Deployment

The app deploys to Railway. The CI/CD pipeline runs tests, builds the Docker image, scans it for vulnerabilities, and deploys to production.

See the [Deployment documentation](docs/DEPLOYMENT.md) for Docker, Railway, CI/CD, migrations, and backup details.

## Documentation

- [API Reference](docs/API.md) — Routes and API endpoints
- [Database Models](docs/DATABASE.md) — Models and relationships
- [Deployment](docs/DEPLOYMENT.md) — Deployment, migrations, and backup
- [Design System](DESIGN.md) — Visual theme and component guidelines

## License

This project is licensed under the MIT License.