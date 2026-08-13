# Agent Guidelines for flask-production-blog-app

## Project Overview
- **Type**: Flask web application (blog)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Testing**: pytest with testcontainers (Docker-based PostgreSQL)
- **Authentication**: Flask-Security with roles-based access control

## Build, Lint, and Test Commands

### Running Tests

Run all tests:
```bash
pytest
```

Run a single test file:
```bash
pytest tests/test_blog.py
```

Run a single test function:
```bash
pytest tests/test_blog.py::test_index
```

Run tests with verbose output:
```bash
pytest -v
```

Run tests matching a pattern:
```bash
pytest -k "test_login"
```

### Development Server

Run the Flask app:
```bash
flask run
# or
python wsgi.py
```

Run in debug mode:
```bash
export DEBUG=1 && flask run
```

### Database Migrations

Create a migration:
```bash
flask db migrate -m "migration message"
```

Apply migrations:
```bash
flask db upgrade
```

Rollback:
```bash
flask db downgrade
```

---

## Code Style Guidelines

### Imports
Organize imports in the following order (separate groups with blank lines):
1. Standard library (`os`, `datetime`, `typing`)
2. Third-party packages (`flask`, `sqlalchemy`)
3. Local application modules (`from .models import ...`)

```python
# Standard library
from datetime import datetime
from typing import List

# Third-party
from flask import Blueprint, render_template
from flask_security.core import UserMixin, RoleMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Local
from . import db
from .models import Post
```

### Type Annotations
- Use SQLAlchemy's `Mapped` and `mapped_column` for type-safe column definitions
- Use `| None` syntax for nullable types (Python 3.10+)
- Add `# type: ignore` comments for SQLAlchemy ORM attributes where needed
- Use explicit type hints for all function parameters and return values

```python
class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(50), nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    author_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), nullable=False)
    date: Mapped[datetime] = mapped_column(db.Date, nullable=False)
```

### Naming Conventions
- **Variables/functions**: snake_case (`create_app`, `all_posts`)
- **Classes**: PascalCase (`User`, `Role`, `Post`)
- **Constants**: UPPER_SNAKE_CASE
- **Database tables**: singular, lowercase (`user`, `role`, `post`)
- **Blueprint names**: snake_case (`bp = Blueprint("blog", __name__)`)

### Formatting
- Use **double quotes** for strings
- Maximum line length: 100 characters (soft guideline)
- Use blank lines sparingly to separate logical sections
- Align assignments with spaces after `=`

```python
# Good
app.config.from_mapping(
    DEBUG = os.environ.get("DEBUG") == "1",
    SECRET_KEY = os.environ.get("SECRET_KEY"),
)

# Avoid
app.config.from_mapping({
    'DEBUG': os.environ.get("DEBUG") == "1",
})
```

### Error Handling
- Use Flask's `abort()` for HTTP errors (e.g., `abort(403)`)
- Use `flash()` for user-facing error messages
- Validate form inputs early and return errors inline

```python
if not title:
    error = "Title is required."
    return render_template("blog/new.html", error_msg=error)
```

### Routes/Views
- Use `@bp.route()` decorator pattern
- Place `@auth_required()` and role decorators above route decorators
- Use descriptive endpoint names matching blueprint name (`url_for("blog.index")`)

```python
@bp.route("/edit/<int:post_id>", methods=["GET", "POST"])
@auth_required()
def edit(post_id):
    # ...
```

### Database Operations
- Use `db.session.commit()` after `db.session.add()` or modifications
- Use `db.get_or_404(Model, id)` for 404 handling on lookups
- Use `filter_by()` for simple filters, `filter()` for complex queries

```python
# Simple lookup with 404
post = db.get_or_404(Post, post_id)

# Query with filter
post = Post.query.filter_by(id=post_id).first()
```

### Testing Conventions
- Test files: `test_*.py` in `tests/` directory
- Use fixtures from `conftest.py` for common setup (`client`, `app`, `db`, `auth`)
- Use `@pytest.mark.parametrize` for testing multiple inputs
- Use `with app.app_context()` when accessing database in tests
- Test client returns follow redirects with `follow_redirects=True`

```python
def test_add_post(client, create_user, auth, app):
    auth.login()
    response = client.get("/new")
    assert response.status_code == 200

    client.post("/add", data={"post_title": "Title", "post_content": "Content"})
    with app.app_context():
        count = Post.query.count()
        assert count == 1
```

### Security
- Never commit secrets to version control (use `.env` files)
- Use environment variables for configuration (`os.environ.get()`)
- Enable CSRF protection in forms (Flask-WTF handles this)
- Use proper password hashing (Flask-Security provides this)

### File Organization
```
bloggr/
  __init__.py      # App factory, extensions, blueprint registration
  models.py        # SQLAlchemy models (User, Role, Post)
  blog.py          # Blueprint with routes
  roles.py         # Role initialization signals
  templates/       # Jinja2 templates
  static/         # CSS, JS, images
```

---

## Common Patterns

### Application Factory
```python
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(...)
    
    if test_config is not None:
        app.config.update(test_config)
    
    db.init_app(app)
    # ... initialize other extensions
    
    return app
```

### Model with Relationships
```python
class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    posts: Mapped[List[Post]] = relationship(backref="author", lazy=True)
```

### Using Test Fixtures
```python
def test_something(client, app, db, create_user, auth):
    # client: test client for HTTP requests
    # app: Flask application instance
    # db: database instance
    # create_user: creates and returns a test user
    # auth: helper for login/logout
```

---

## Production Safety & Development Workflow

This application is live in production on Railway. Protect production at all times.

### Branches
main = production. Never develop directly on main.
development = integration/staging.
Use feature/*, fix/*, or similar branches for individual changes.
Start new work from development.
feature/* → development → staging/testing → main → production

### Rules
Before changing anything, run:

git status
git branch --show-current
git branch -a
Never modify, reset, delete, force-push, or directly commit to main.
Never use production as a testing environment.
Never point local/development/staging code at the production database.
Never expose, commit, copy, or modify production secrets.
Never perform destructive production database operations without explicit human approval.
Test changes locally and, when available, on the staging Railway environment before production.
Review the final diff, tests, migrations, environment-variable requirements, and potential production risks before declaring a change ready.
Do not deploy or push to main automatically. Production deployment requires explicit approval from the project owner.
If the repository contains unexpected uncommitted changes, do not discard them. Stop and ask.
Never use destructive commands such as:
git reset --hard
git clean -fd
git push --force

unless explicitly authorized.

### OpenCode Responsibilities

OpenCode may:

Create development/feature branches.
Modify code.
Write and run tests.
Run migrations in development/staging.
Commit and push feature/development branches.
Review changes and report risks.
Update the README.md file when a change affects documented behavior.

OpenCode must stop and request human approval for:

Production deployment.
Pushing/merging to main.
Production Railway configuration changes.
Production secrets.
Destructive production database operations.
Any irreversible or potentially production-impacting action.
Production Release

Before requesting approval, report:

Changes:
Tests:
Migrations:
Environment changes:
Known risks:
Rollback approach:

When in doubt: stop, explain the risk, and ask before touching production.

---

## Documentation Sync (README.md)

The README.md file documents the behavior of this application. Keep it accurate. Before you finish any task, run the README relevance check below.

### README Relevance Check

Compare your change against the table below. If your change affects a documented area, update the matching README section in the same change. Use the ASD-STE100 skill for the update. Match the existing README style: active voice, short sentences, and tables.

| Code change | README.md section to update |
|---|---|
| New or changed feature or behavior | Features, Usage |
| New or changed route or endpoint | Routes, API Reference |
| New or changed environment variable | Configuration, Environment Variables |
| New or changed configuration class | Configuration, Configuration Classes |
| New or changed dependency | Tech Stack |
| New or changed model or relationship | Database Models |
| New or changed file or directory in `bloggr/` | Project Structure |
| New or changed deployment or CI config | Deployment, CI/CD Pipeline |
| New or changed test fixture or command | Testing |
| New or changed script | Backup |

### No README Change Needed

A README.md change is not needed for these cases:

- Pure refactors that do not change behavior.
- Bug fixes that do not change documented behavior.
- Comments, formatting, or documentation of internal code.
- Changes that do not affect how the app works.

If you are not sure whether the README.md needs a change, ask the user.