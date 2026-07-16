from django.core.management.base import BaseCommand
from core.models import Department

DEPARTMENTS = [
    ("CSE", "Computer Science & Engineering"),
    ("IT", "Information Technology"),
    ("ECE", "Electronics & Communication Engineering"),
    ("EEE", "Electrical & Electronics Engineering"),
    ("AIDS", "Artificial Intelligence & Data Science"),
]


class Command(BaseCommand):
    help = "Seed BPIT departments"

    def handle(self, *args, **options):
        for code, name in DEPARTMENTS:
            obj, created = Department.objects.get_or_create(code=code, defaults={"name": name})
            self.stdout.write(f"{'Created' if created else 'Exists'}: {obj}")
