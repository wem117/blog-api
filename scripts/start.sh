#!/bin/bash

# Exit on error
set -e

# Config
VENV="venv"
PY="./$VENV/bin/python"
PIP="./$VENV/bin/pip"

echo "Starting Blog API..."

# 1. Check .env
if [ ! -f ".env" ]; then
    echo "Creating .env..."
    cp .env.example .env
fi

echo "Checking env vars..."
VARS=("SECRET_KEY" "DEBUG" "ALLOWED_HOSTS" "REDIS_URL")
for v in "${VARS[@]}"; do
    val=$(grep "^${v}=" .env | cut -d'=' -f2- | xargs)
    if [ -z "$val" ]; then
        echo "Error: ${v} missing or empty in .env"
        exit 1
    fi
done
echo "Env OK."

# 2. Venv
if [ ! -d "$VENV" ]; then
    echo "Creating venv..."
    python3 -m venv "$VENV"
fi

# 3. Deps
echo "Installing deps..."
$PIP install --upgrade pip > /dev/null
$PIP install -r requirements/base.txt > /dev/null

# 4. Database
echo "Migrating..."
$PY manage.py migrate > /dev/null

# 5. Static
echo "Collecting static..."
$PY manage.py collectstatic --noinput > /dev/null

# 6. Translations
echo "Compiling translations..."
$PY manage.py compilemessages > /dev/null

# 7. Superuser (idempotent)
echo "Ensuring admin..."
$PY manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@example.com').exists():
    User.objects.create_superuser(email='admin@example.com', password='admin123', first_name='Admin', last_name='Adminov')
    print('Admin created.')
else:
    print('Admin exists.')
EOF

# 8. Seed
echo "Seeding data..."
$PY manage.py seed_data

# 9. Result
echo "  "
echo "Success! Project is ready."
echo ""
echo "URLs:"
echo "Admin: http://localhost:8000/admin/"
echo "Swagger: http://localhost:8000/api/docs/"
echo "ReDoc: http://localhost:8000/api/redoc/"
echo "Schema: http://localhost:8000/api/schema/"
echo ""
echo "Creds:"
echo "Email: admin@example.com"
echo "Pass: admin123"
echo "------------------------------------------------"

# 10. Start
echo "Starting server..."
$PY manage.py runserver 0.0.0.0:8000
