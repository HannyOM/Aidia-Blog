# Database Models

The SQLAlchemy models are defined in `bloggr/models.py`.

## User

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `username` | String(20) | Unique username |
| `email` | String(100) | Unique email address |
| `password` | String(255) | Hashed password (Argon2) |
| `active` | Boolean | Account active status |
| `fs_uniquifier` | String(255) | Flask-Security unique identifier |
| `confirmed_at` | DateTime | Email confirmation timestamp |

## Role

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `name` | String(80) | Unique role name |
| `description` | String(255) | Role description |

## Post

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `title` | String(50) | Post title |
| `content` | Text | Post content (HTML) |
| `author_id` | Integer | Foreign key to User |
| `date` | Date | Publication date |
| `is_published` | Boolean | Published status (default: False) |

## Comment

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `content` | Text | Comment text |
| `date` | DateTime | Comment timestamp |
| `post_id` | Integer | Foreign key to Post |
| `user_id` | Integer | Foreign key to User |

## Vote

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `post_id` | Integer | Foreign key to Post |
| `user_id` | Integer | Foreign key to User |
| `is_like` | Boolean | True for a like. False for a dislike |

The database enforces a unique constraint on the `post_id` and `user_id` columns. Each user has one vote per post.

## Relationships

- **User ↔ Role**: Many-to-many via the `roles_users` junction table (CASCADE delete).
- **User → Post**: One-to-many (`Post.author` backref).
- **User → Comment**: One-to-many (`Comment.user` backref).
- **User → Vote**: One-to-many (`Vote.user` backref).
- **Post → Comment**: One-to-many. Deleting a post deletes its comments.
- **Post → Vote**: One-to-many. Deleting a post deletes its votes.