# BPIT ERP

Django (DRF + JWT) backend + React (Vite) frontend.

## Core Module (built)
- Custom User model with roles (Admin, Faculty, Student, Staff)
- Department model (CSE, IT, ECE, EEE, AIDS seeded)
- JWT-based login (`/api/auth/login/`, `/api/auth/refresh/`, `/api/auth/me/`)
- Users CRUD (admin-only write access)
- Departments CRUD (admin-only write access)
- React login page + dashboard showing Departments & Users tables

## Setup

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # or use seed below
python manage.py runserver
```

Default seeded admin (created via shell, see below): `bpit` / `bpit@admin123`

To reseed departments + admin user:
```bash
python manage.py shell
```
```python
from core.models import User
from departments.models import Department

for code, name in [("CSE","Computer Science & Engineering"),("IT","Information Technology"),
                    ("ECE","Electronics & Communication Engineering"),
                    ("EEE","Electrical & Electronics Engineering"),
                    ("AIDS","Artificial Intelligence & Data Science")]:
    Department.objects.get_or_create(code=code, defaults={"name": name})

u = User(username="bpit", role=User.Role.ADMIN, is_staff=True, is_superuser=True)
u.set_password("bpit@admin123")
u.save()
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs at `http://localhost:5173`, talks to backend at `http://localhost:8000/api`.

## Student Records Module (built)
- Student model: enrollment_no, name, department (FK), batch, semester, section, phone, email
- Optional link to a User account (`user_account`) for future student login
- Full CRUD via `/api/students/` (admin-only write)
- Filters: `?department=CSE`, `?batch=2024-28`, `?section=A`, `?semester=3`
- Search: `?search=<name/enrollment/email/phone>`
- Bulk import: `POST /api/students/bulk-import/` (multipart form, field `file`, .csv or .xlsx)
  - Required columns: `enrollment_no, name, department_code, batch`
  - Optional columns: `semester, section, phone, email`
  - Re-importing the same `enrollment_no` updates the existing record (no duplicates)
  - All columns read as strings to avoid pandas mangling phone/enrollment numbers
- React Students page: filter bar, add-student form, bulk import via file picker, delete

## Next module (planned)
Results/Exams — result upload and report generation, building on Student Records.
