# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

### Authentication

`POST /auth/register` — Create a new account.
`POST /auth/login` — Obtain a JWT access token.

Endpoints marked "requires authentication" expect the token from `POST /auth/login` in an `Authorization: Bearer <token>` header. A missing, invalid or expired token returns `401`.

### Profiles

`POST /profiles` — Create a profile with resume and GitHub username.

**Request** (requires authentication). The body is `multipart/form-data`, not JSON. All fields are optional.

| Field | Type | Description | Example |
|---|---|---|---|
| `github_username` | string (max 255 characters) | GitHub username to review. | `octocat` |
| `portfolio_url` | string (max 500 characters) | Link to the user's portfolio site. | `https://octocat.dev` |
| `resume_file` | file upload | Resume as PDF, Markdown (`text/markdown`) or plain text (`text/plain`). | `resume.pdf` |

Example:

```
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer <token>" \
  -F "github_username=octocat" \
  -F "portfolio_url=https://octocat.dev" \
  -F "resume_file=@resume.pdf;type=application/pdf"
```

Returns the created profile: `id`, `user_id`, `github_username`, `portfolio_url`, `created_at` and `resume_filename`. Returns `422` if the resume is not a PDF, Markdown or plain text file, or if a PDF cannot be parsed.

`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

**Request** (requires authentication). The body is `application/json`.

| Field | Type | Description | Example |
|---|---|---|---|
| `profile_id` | string (UUID), required | ID of the profile to review, from `POST /profiles`. | `3fa85f64-5717-4562-b3fc-2c963f66afa6` |

Example:

```
curl -X POST http://localhost:8000/reviews \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"}'
```

The review runs in the background, so the response comes back right away with `status` set to `pending`. Its other fields are `id`, `profile_id`, `sections`, `overall_score`, `error_message`, `created_at` and `updated_at`. Fetch the finished review with `GET /reviews/{review_id}`.

`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
