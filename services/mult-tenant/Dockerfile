FROM python:3.10

WORKDIR /django

RUN apt-get update && apt-get install -y wget

RUN wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

COPY requirements.txt .
RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]