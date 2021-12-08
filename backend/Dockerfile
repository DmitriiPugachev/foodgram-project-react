FROM python:3.8.5

WORKDIR /code
COPY requirements.txt .
RUN pip install -r /code/requirements.txt
COPY . .
RUN python manage.py load_data
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000