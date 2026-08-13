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
| GET | `/` | No | Homepage with rotating quotes, a featured post, and latest articles |
| GET | `/post/<post_id>` | No | View a single post |
| GET | `/articles` | No | All published articles |
| GET | `/search?q=<query>` | No | Search published posts |
| GET | `/new` | Yes | New post form (admin or editor) |
| GET/POST | `/add` | Yes | Create a new post |
| GET/POST | `/edit/<post_id>` | Yes | Edit a post (author only) |
| POST | `/save/<post_id>` | Yes | Save an edited post (author only) |
| GET | `/delete/<post_id>` | Yes | Delete a post (author only) |
| GET | `/check-email` | No | Confirmation reminder after registration |
| GET | `/profile/<username>` | No | User profile page |
| POST | `/message/<username>` | No | Send a message to a user |
| GET/POST | `/profile/edit` | Yes | Edit a user profile |
| GET | `/api/user/<user_id>` | No | User info JSON API |
| POST | `/post/<post_id>/vote` | Yes | Like or dislike a post |
| POST | `/post/<post_id>/comment` | Yes | Add a comment to a post |
| POST | `/comment/<comment_id>/delete` | Yes | Delete a comment (comment author, post author, or admin) |
| GET | `/health` | No | Health check endpoint |

Flask-Security also provides the `/login`, `/logout`, `/register`, and `/confirm` routes.
