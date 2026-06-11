#  Clinic Services API

A production-ready REST API for searching and managing local clinic services, built with **FastAPI** and **PostgreSQL**.

> Designed as a portfolio-quality project for competition submissions.

---

##  Features

| Feature | Details |
|---|---|
|  Authentication | JWT Bearer Tokens, role-based access (patient / clinic_admin / admin) |
|  Clinic Management | Register, update, list, soft-delete clinics |
|  Smart Search | Filter by service name, district, GPS radius (5/10/20 km) |
|  Specialty Filters | Emergency, Maternal Health, Vaccination Centers |
|  Services | Add/update/delete clinic services with categories & pricing |
|  Doctors | Doctor profiles with specialization, qualifications, availability |
|  Appointments | Book, view, update status, and cancel appointments |
|  Reviews | Rate & review clinics (1–5 stars), auto-computed average rating |
|  Opening Hours | Set opening hours per day of week |
|  GPS Search | Haversine formula for radius-based clinic discovery |
|  Docker | One-command local dev with `docker compose up` |

---

##  Quick Start

### Option A — Docker (Recommended)

```bash
# Clone and enter the project
cd clinic-services-api

# Copy environment variables
cp .env.example .env

# Start everything (API + PostgreSQL)
docker compose up --build
```

API is now running at **http://localhost:8000**
Docs: **http://localhost:8000/docs**

---

### Option B — Local Setup

**Prerequisites**: Python 3.11+, PostgreSQL running locally

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the database in PostgreSQL
psql -U postgres -c "CREATE DATABASE clinic_db;"

# 4. Set up environment variables
cp .env.example .env
# Edit .env and update DATABASE_URL, JWT_SECRET_KEY

# 5. Run the API
uvicorn app.main:app --reload
```

Tables are created automatically on first startup.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/clinic_db` |
| `JWT_SECRET_KEY` | Secret key for signing JWT tokens | *(change this!)* |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `60` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `["http://localhost:3000"]` |

---

##  API Reference

Interactive docs: **http://localhost:8000/docs** (Swagger UI)

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/auth/register` |   Register new user |
| POST | `/api/v1/auth/login` |   Login, get JWT token |
| GET | `/api/v1/auth/me` |   Get current user profile |

### Clinics

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/clinics` |  List all clinics (paginated) |
| POST | `/api/v1/clinics` | clinic_admin | Create a clinic |
| GET | `/api/v1/clinics/search` | Search (service, district, GPS) |
| GET | `/api/v1/clinics/emergency` | List emergency clinics |
| GET | `/api/v1/clinics/maternal` |  List maternal health clinics |
| GET | `/api/v1/clinics/vaccination` |  List vaccination centers |
| GET | `/api/v1/clinics/{id}` |  Get clinic by ID |
| PUT | `/api/v1/clinics/{id}` |  owner | Update clinic |
| DELETE | `/api/v1/clinics/{id}` | owner | Soft-delete clinic |

### Services, Doctors & Opening Hours

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/clinics/{id}/services` |   List services |
| POST | `/api/v1/clinics/{id}/services` | Add service |
| PUT | `/api/v1/clinics/{id}/services/{sid}` |  Update service |
| DELETE | `/api/v1/clinics/{id}/services/{sid}` |  Delete service |
| GET | `/api/v1/clinics/{id}/doctors` |  List doctors |
| POST | `/api/v1/clinics/{id}/doctors` |  Add doctor |
| GET | `/api/v1/clinics/{id}/opening-hours` | Get hours |
| POST | `/api/v1/clinics/{id}/opening-hours` |  Set hours for a day |

### Appointments

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/v1/appointments` |  Book appointment |
| GET | `/api/v1/appointments/my` |  My appointments |
| GET | `/api/v1/appointments/clinic/{id}` |  All clinic appointments |
| PUT | `/api/v1/appointments/{id}/status` |  Update status |
| DELETE | `/api/v1/appointments/{id}` |  Cancel appointment |

### Reviews

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/clinics/{id}/reviews` | List reviews |
| POST | `/api/v1/clinics/{id}/reviews` |  Post a review |
| PUT | `/api/v1/reviews/{id}` |  Update your review |
| DELETE | `/api/v1/reviews/{id}` |  Delete your review |

---

## Example Flow

```bash
# 1. Register as clinic admin
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"full_name":"John Doe","email":"john@clinic.com","password":"secret123","role":"clinic_admin"}'

# 2. Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -F "username=john@clinic.com" -F "password=secret123" | jq -r .access_token)

# 3. Create a clinic
curl -X POST http://localhost:8000/api/v1/clinics \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Kingharman Road Clinic","address":"Kingharman Road","district":"Western Area","phone":"2327000000","latitude":8.484,"longitude":-13.234,"is_maternal":true}'

# 4. Search by service + GPS radius
curl "http://localhost:8000/api/v1/clinics/search?service=Maternal+Care&lat=8.48&lng=-13.23&radius_km=5"

# 5. Book an appointment
curl -X POST http://localhost:8000/api/v1/appointments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"clinic_id":1,"patient_name":"Maliaka","appointment_date":"2026-07-15T10:00:00"}'
```

---

##  Project Structure

```
clinic-services-api/
├── app/
│   ├── main.py              # FastAPI app, routers, lifespan
│   ├── config.py            # Pydantic settings from .env
│   ├── database.py          # SQLAlchemy engine + get_db
│   ├── models/
│   │   ├── user.py          # Users (patient/clinic_admin/admin)
│   │   ├── clinic.py        # Clinics with GPS + specialty flags
│   │   ├── service.py       # Clinic services
│   │   ├── doctor.py        # Doctors per clinic
│   │   ├── appointment.py   # Appointments with status enum
│   │   ├── review.py        # Ratings + reviews
│   │   └── opening_hours.py # Schedule per day of week
│   ├── schemas/             # Pydantic v2 request/response models
│   ├── routes/              # FastAPI routers (auth, clinics, ...)
│   └── utils/
│       ├── auth.py          # JWT + bcrypt password hashing
│       ├── geo.py           # Haversine GPS radius search
│       └── dependencies.py  # get_current_user, role guards
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

##  Role Reference

| Role | Can Do |
|---|---|
| `patient` | Register, login, book appointments, post reviews |
| `clinic_admin` | All patient actions + manage their own clinic (services, doctors, hours) |
| `admin` | Full access to all clinics and operations |

---

##  Database Schema

```
users ──< clinics ──< services
                 ──< doctors
                 ──< appointments >── users
                 ──< reviews >── users
                 ──< opening_hours
```

---

##  Tech Stack

- **FastAPI** — High-performance Python web framework
- **SQLAlchemy 2.0** — ORM and query builder
- **PostgreSQL** — Relational database
- **Pydantic v2** — Data validation and serialization
- **python-jose** — JWT token generation and verification
- **passlib + bcrypt** — Secure password hashing
- **Alembic** — Database migrations (optional)
- **Docker + Docker Compose** — Containerized deployment


