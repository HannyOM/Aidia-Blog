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

A post describes a problem to be solved.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `title` | String(50) | Problem title |
| `content` | Text | Problem content (HTML) |
| `author_id` | Integer | Foreign key to User |
| `date` | Date | Publication date |
| `is_published` | Boolean | Published status (default: False) |
| `industry` | String(50) | Industry of the problem (default: Other) |
| `country` | String(100) | Country of the problem (default: General) |
| `status` | String(20) | Problem status: open, in_progress, or solved (default: open) |

## Comment

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `content` | Text | Comment text |
| `date` | DateTime | Comment timestamp |
| `post_id` | Integer | Foreign key to Post |
| `user_id` | Integer | Foreign key to User |

## Vote

A vote states whether a problem is worth solving.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `post_id` | Integer | Foreign key to Post |
| `user_id` | Integer | Foreign key to User |
| `is_like` | Boolean | True for worth solving. False for not worth solving |

The database enforces a unique constraint on the `post_id` and `user_id` columns. Each user has one vote per post.

## Suggestion

A suggestion proposes a solution for a problem.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `content` | Text | Solution text |
| `date` | DateTime | Suggestion timestamp |
| `problem_id` | Integer | Foreign key to Post |
| `user_id` | Integer | Foreign key to User |

## SuggestionVote

A suggestion vote states whether a solution is good.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `suggestion_id` | Integer | Foreign key to Suggestion |
| `user_id` | Integer | Foreign key to User |
| `is_good` | Boolean | True for a good solution. False for a solution that is not good |

The database enforces a unique constraint on the `suggestion_id` and `user_id` columns. Each user has one vote per suggestion.

## Relationships

- **User ↔ Role**: Many-to-many via the `roles_users` junction table (CASCADE delete).
- **User → Post**: One-to-many (`Post.author` backref).
- **User → Comment**: One-to-many (`Comment.user` backref).
- **User → Vote**: One-to-many (`Vote.user` backref).
- **User → Suggestion**: One-to-many (`Suggestion.user` backref).
- **User → SuggestionVote**: One-to-many (`SuggestionVote.user` backref).
- **Post → Comment**: One-to-many. Deleting a post deletes its comments.
- **Post → Vote**: One-to-many. Deleting a post deletes its votes.
- **Post → Suggestion**: One-to-many. Deleting a post deletes its suggestions.
- **Suggestion → SuggestionVote**: One-to-many. Deleting a suggestion deletes its votes.