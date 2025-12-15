
FROM python:3.11-slim


WORKDIR /app


COPY requirements.txt requirements.txt
COPY app.py app.py


RUN pip install --no-cache-dir -r requirements.txt


ENV PORT=8080
EXPOSE 8080


CMD ["python", "app.py"]
