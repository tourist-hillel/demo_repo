FROM python:3.12-slim

ENV PYTHONBUFFERED=1 \
    PYTHONDONOTWRITEBITECODE=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    libpq-dev \
    python3-dev \ 
    pkg-config \ 
    gcc \
    && rm -rf /var/lib/apt/list/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . . 

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
