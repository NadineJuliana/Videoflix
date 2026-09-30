# Videoflix Backend

## Description

Videoflix Backend is a REST API built with Django and Django REST Framework for a video streaming application.

The project provides user authentication, email activation, password reset functionality and protected video streaming.

Uploaded videos are processed asynchronously using Redis, Django RQ and FFmpeg and converted into multiple HLS resolutions.

---

## Features

- User registration
- Email activation
- Login and logout
- JWT authentication via HTTP-only cookies
- Password reset
- Protected video endpoints
- Asynchronous video processing
- Automatic thumbnail generation
- HLS video streaming
- 480p, 720p and 1080p video resolutions
- PostgreSQL database
- Redis and Django RQ
- Docker setup

---

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- Simple JWT
- PostgreSQL
- Redis
- Django RQ
- FFmpeg
- Gunicorn
- django-cors-headers
- Docker
- Docker Compose

---

## Installation

### Clone the repository

```bash
git clone https://github.com/NadineJuliana/Videoflix.git
cd Videoflix/backend
```

To use the current development version:

```bash
git checkout develop
```

### Environment Variables

Create a `.env` file based on the provided `.env.template`.

**Windows PowerShell**

```powershell
Copy-Item .env.template .env
```

**Linux / macOS**

```bash
cp .env.template .env
```

The `.env.template` contains all required environment variables for Django, PostgreSQL, Redis and the local development setup.

---

## Run with Docker

Build and start the containers:

```bash
docker compose up -d --build
```

The setup starts:

- Django / Gunicorn
- PostgreSQL
- Redis
- Django RQ worker

The backend will be available at:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

The configured development superuser can be found in the `.env` file.

Stop the containers:

```bash
docker compose down
```

---

## Video Processing

Videos can be uploaded through the Django Admin.

After a video is created, processing is started automatically in the background using Django RQ and Redis.

FFmpeg generates:

- a thumbnail
- 480p HLS files
- 720p HLS files
- 1080p HLS files

The processed videos are then available through the protected streaming endpoints.

---

## Authentication

The API uses **JWT authentication via HTTP-only cookies**.

The authentication flow includes:

- registration
- email activation
- login
- token refresh
- logout
- password reset

Authentication cookies are automatically included in requests from the configured frontend origins.

For local development, emails are written to the backend console.

View the backend logs with:

```bash
docker compose logs -f web
```

---

## API Endpoints

### Authentication

| Method | Endpoint |
| --- | --- |
| POST | `/api/register/` |
| GET | `/api/activate/{uid}/{token}/` |
| POST | `/api/login/` |
| POST | `/api/logout/` |
| POST | `/api/token/refresh/` |
| POST | `/api/password_reset/` |
| POST | `/api/password_confirm/{uid}/{token}/` |

### Videos

| Method | Endpoint |
| --- | --- |
| GET | `/api/video/` |
| GET | `/api/video/{movie_id}/{resolution}/index.m3u8` |
| GET | `/api/video/{movie_id}/{resolution}/{segment}/` |

Supported resolutions:

- 480p
- 720p
- 1080p

---

## Frontend Integration

For local testing, the backend is configured for the provided Developer Akademie frontend running on:

```text
http://localhost:5500
http://127.0.0.1:5500
```

The frontend can be started separately on port `5500`, for example using a local development server.

---

## Project Structure

```text
Videoflix/
├── backend/
│   ├── authentication/
│   ├── core/
│   ├── videos/
│   ├── media/
│   ├── static/
│   ├── .env.template
│   ├── backend.Dockerfile
│   ├── backend.entrypoint.sh
│   ├── docker-compose.yml
│   ├── manage.py
│   └── requirements.txt
├── frontend/
├── .gitignore
└── README.md
```

---

## Testing

Tests are organized into **Happy Path** and **Unhappy Path** scenarios to verify expected behavior and proper error handling.

Run the Django system check:

```bash
docker compose exec web python manage.py check
```

Run the authentication and video tests:

```bash
docker compose exec web python manage.py test authentication videos
```

The current test suite contains **57 automated tests**.

---

## Development Notes

The project follows:

- Django REST Framework
- JWT authentication
- HTTP-only cookie authentication
- Separation of concerns
- Environment-based configuration
- Asynchronous background processing
- HLS video streaming
- Happy and unhappy path testing
- Dockerized development

PostgreSQL, Redis, media files and static files use persistent Docker volumes.

After changing dependencies in `requirements.txt`, rebuild the containers:

```bash
docker compose down
docker compose up -d --build
```

The `.env` file is excluded from version control. Create your own `.env` file using the provided `.env.template`.
