FROM python:3.10

WORKDIR /django
RUN pip install kafka-python
RUN pip install django-tenants
RUN pip install django-debug-toolbar
COPY requirements.txt .
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

COPY . .
