FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY foodgram_project/. .

CMD ["waitress-serve", "--listen=127.0.0.1:8000", "foodgram_project.wsgi:application"]