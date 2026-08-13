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

---

## Production Safety & Development Workflow

This application is live in production on Railway. Protect production at all times.

### Branches
main = production. Never develop directly on main.
Use feature/*, fix/*, or similar branches for individual changes.
Start new work from main.
feature/* → main → production

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

## Documentation Sync

The README.md and the files in `docs/` document the behavior of this application. Keep them accurate. Before you finish any task, run the relevance check below.

### Relevance Check

Compare your change against the table below. If your change affects a documented area, update the matching file in the same change. Use the ASD-STE100 skill for the update. Match the existing style: active voice, short sentences, and tables.

| Code change | File to update |
|---|---|
| New or changed feature or behavior | README.md: Features, Usage |
| New or changed route or endpoint | `docs/API.md` |
| New or changed environment variable | README.md: Environment Variables |
| New or changed configuration class | README.md: Configuration |
| New or changed dependency | README.md: Tech Stack |
| New or changed model or relationship | `docs/DATABASE.md` |
| New or changed file or directory in `bloggr/` | README.md: Project Structure |
| New or changed deployment, CI, or migration | `docs/DEPLOYMENT.md`, README.md: Deployment |
| New or changed test fixture or command | README.md: Testing |
| New or changed script or backup | `docs/DEPLOYMENT.md` |

### No Documentation Change Needed

A README.md or `docs/` change is not needed for these cases:

- Pure refactors that do not change behavior.
- Bug fixes that do not change documented behavior.
- Comments, formatting, or documentation of internal code.
- Changes that do not affect how the app works.

If you are not sure whether the README.md needs a change, ask the user.