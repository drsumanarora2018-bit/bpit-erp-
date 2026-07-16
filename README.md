# BPIT ERP — Core Module (v1)

A real, running web app foundation for BPIT's college ERP system. This first
milestone covers: **login, roles, and departments** — the base every other
module (attendance, results, fees, etc.) will plug into.

## What's included

- **Backend:** Django + Django REST Framework, JWT auth, SQLite (local dev)
  - Custom `User` model with roles: Admin, HOD, Faculty, Student, Accounts
  - `Department` model (CSE, IT, ECE, EEE, AI&DS pre-seeded)
  - Role-based permissions (only Admin can create/manage users)
  - Django admin panel at `/admin/` for quick data entry
- **Frontend:** React (Vite) + React Router
  - Login page
  - Role-aware dashboard (Admin sees all users; others see their own profile)
  - JWT stored client-side with automatic token refresh

## Project structure

```
bpit-erp/
├── backend/            Django project ("config") + "core" app
│   ├── core/           models, views, serializers, permissions
│   ├── db.sqlite3       (created after migrate)
│   └── manage.py
└── frontend/            React (Vite) app
    └── src/
        ├── api/          axios client with JWT refresh
        ├── context/      AuthContext (login/logout/session)
        ├── pages/        Login, Dashboard
        └── components/   ProtectedRoute
```

## Running it locally

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_departments      # adds CSE, IT, ECE, EEE, AIDS
python manage.py createsuperuser       # create your admin login

python manage.py runserver
```

Backend runs at **http://localhost:8000**. Django admin: **http://localhost:8000/admin/**

> ⚠️ After creating your superuser, its `role` defaults to `STUDENT`. Set it to
> `ADMIN` once, either via `/admin/` or the shell:
> ```bash
> python manage.py shell -c "from core.models import User; u=User.objects.get(username='YOUR_USERNAME'); u.role='ADMIN'; u.save()"
> ```

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173** — open this in your browser and log
in with the superuser account you created.

## API reference (v1)

| Method | Endpoint                     | Who                | Purpose                        |
|--------|-------------------------------|---------------------|---------------------------------|
| POST   | `/api/auth/login/`            | Public              | Get JWT access + refresh token  |
| POST   | `/api/auth/refresh/`          | Public              | Refresh access token             |
| GET    | `/api/me/`                    | Any logged-in user  | Current user's profile          |
| GET/POST | `/api/departments/`         | Read: any; Write: Admin | List / create departments   |
| GET/POST | `/api/users/`               | Admin only          | List / create users             |
| POST   | `/api/users/{id}/set_password/` | Admin only        | Reset a user's password         |
| POST   | `/api/users/{id}/toggle_active/`| Admin only        | Enable/disable a user account   |

## What's next (future modules)

This is deliberately scoped as the **foundation** — everything else (student
records, attendance, results, fees, faculty workload, library) will be built
as additional Django apps + React pages that reuse this same login/role
system, so you're not starting over each time. Let me know which module you'd
like next and I'll build it the same way: real code, tested, ready to run.
