FROM python:3.12-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/ /app/requirements/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN mkdir -p /app/media /app/staticfiles

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "settings.asgi:application"]

