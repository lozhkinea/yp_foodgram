FROM python:3.10-slim
WORKDIR /app
COPY ./backend/requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt --no-cache-dir
COPY ./backend .
CMD gunicorn --bind 0:8000 foodgram.wsgi:application
