# APIFORGE Backend

A Backend with AUTH,JWT authentication,RBAC and CRUD .

## TechStack
# 1. FastAPI
# 2. PostgresSQL 
# 3. Docker for deployment

---

## Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose installed

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/mrigangha/apiforge_backend.git/
cd apiforge_backend
```

### 2. Create a `.env` file

Create a `.env` file in the `backend/` directory:

Database and all are hardcoded for now for test purposes

```env
SECRET=your_secret_key_here
```

### 3. Start the containers

```bash
docker-compose up --build
```

The API will be available at **http://localhost:8000**

---

## Database Migrations

Run migrations after starting the containers:

```bash
# Apply all migrations
docker-compose exec backend alembic upgrade head

# Create a new migration after model changes
docker-compose exec backend alembic revision --autogenerate -m "your message"

# Check current migration status
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

---

## API Docs

Once running, interactive API docs are available at:

- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and get tokens |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/user` | Get current user info |

### Posts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/posts` | Get all posts |
| POST | `/api/v1/posts` | Create a post |
| GET | `/api/v1/posts/{id}` | Get a post by ID |
| PUT | `/api/v1/posts/{id}` | Update a post |
| DELETE | `/api/v1/posts/{id}` | Delete a post |

### Admin (admin role required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/admin/users` | Get all non-admin users |
| GET | `/api/v1/admin/users/{id}` | Get user by ID |
| PATCH | `/api/v1/admin/users/{id}/promote` | Promote user to admin |
| DELETE | `/api/v1/admin/users/{id}` | Delete a user |

---

## Promote a User to Admin

To manually promote a user to admin via the database:

```bash
docker-compose exec db psql -U postgres -d apiforge

UPDATE users SET role = 'admin' WHERE email = 'your@email.com';

\q
```

---

## Useful Commands

```bash
# Start in background
docker-compose up -d --build

# Stop containers
docker-compose down

# View logs
docker-compose logs -f fastapi_app

# Restart backend only
docker-compose restart fastapi_app

# Access the database
docker-compose exec db psql -U postgres -d assignment_db
```
