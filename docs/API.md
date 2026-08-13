# API Reference

## Health Check

```
GET /health
```

The endpoint reports database connectivity. It returns HTTP 200 when the database is reachable:

```json
{ "status": "healthy", "database": "connected" }
```

It returns HTTP 503 when the database is not reachable:

```json
{ "status": "unhealthy", "database": "disconnected" }
```

## User Info API

```
GET /api/user/<user_id>
```

The endpoint returns public user information. It requires no authentication:

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
| GET | `/` | No | Homepage with rotating quotes, a featured problem, and latest problems |
| GET | `/post/<post_id>` | No | View a single problem |
| GET | `/articles` | No | All published problems |
| GET | `/search?q=<query>` | No | Search published problems |
| GET | `/new` | Yes | New problem form (any registered user) |
| GET/POST | `/add` | Yes | Create a new problem |
| GET/POST | `/edit/<post_id>` | Yes | Edit a problem (author only) |
| POST | `/save/<post_id>` | Yes | Save an edited problem (author only) |
| GET | `/delete/<post_id>` | Yes | Delete a problem (author only) |
| GET | `/check-email` | No | Confirmation reminder after registration |
| GET | `/profile/<username>` | No | User profile page |
| POST | `/message/<username>` | No | Send a message to a user |
| GET/POST | `/profile/edit` | Yes | Edit a user profile |
| GET | `/api/user/<user_id>` | No | User info JSON API |
| POST | `/post/<post_id>/vote` | Yes | Vote on problem severity |
| POST | `/post/<post_id>/suggest` | Yes | Propose a solution for a problem |
| POST | `/suggestion/<suggestion_id>/vote` | Yes | Vote on whether a solution is good |
| POST | `/post/<post_id>/status` | Yes | Update a problem status (problem author or admin) |
| POST | `/suggestion/<suggestion_id>/delete` | Yes | Delete a suggestion (suggestion author, problem author, or admin) |
| POST | `/post/<post_id>/comment` | Yes | Add a comment to a problem |
| POST | `/comment/<comment_id>/delete` | Yes | Delete a comment (comment author, problem author, or admin) |
| GET | `/health` | No | Health check endpoint |

Flask-Security also provides the `/login`, `/logout`, `/register`, and `/confirm` routes.
