FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python scripts/init_db.py
EXPOSE 8000 8501
CMD ["python", "scripts/run_dev.py"]
