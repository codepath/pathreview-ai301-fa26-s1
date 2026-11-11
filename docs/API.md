# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### Health

`GET /health` — Returns service status and dependency health.

### Authentication

`POST /auth/register` — Create a new account.
`POST /auth/login` — Obtain a JWT access token.

### Getting a token

Register, or log in, to get an access token. Login takes form fields, and `username` is the email.

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "changeme123"}'

curl -X POST http://localhost:8000/auth/login \
  -d "username=you@example.com&password=changeme123"
```

Both return a token. Use it below as `$TOKEN`.

### Profiles

`POST /profiles` — Create a profile with resume and GitHub username.

Multipart form data. All fields are optional. `resume_file` must be PDF, Markdown or plain text.

```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer $TOKEN" \
  -F "github_username=octocat" \
  -F "portfolio_url=https://example.com" \
  -F "resume_file=@resume.md;type=text/markdown"
```
`GET /profiles/{profile_id}` — Retrieve a profile.
`DELETE /profiles/{profile_id}` — Delete a profile and associated data.

### Reviews

`POST /reviews` — Request a new portfolio review for a profile.

JSON body with a required `profile_id`. It returns right away with status `pending`.

```bash
curl -X POST http://localhost:8000/reviews \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "<profile_id>"}'
```
`GET /reviews/{review_id}` — Retrieve a completed review.
`GET /reviews` — List reviews for the authenticated user (paginated).

## Interactive Docs

When the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
