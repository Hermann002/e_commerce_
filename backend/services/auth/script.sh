echo "Running migrations..."

python manage.py collectstatic --noinput

python manage.py makemigrations manage_users

python manage.py migrate

python manage.py test

# python manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
  echo " "
  echo "❌ Test step failed, please fix before pushing."
  exit 1
fi

gunicorn auth.wsgi:application --bind 0.0.0.0:8000