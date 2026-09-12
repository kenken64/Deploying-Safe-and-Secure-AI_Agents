# For laptops where installing Python is a fight. Same lab, one command.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -c "from agent import db; db.reset()"
EXPOSE 8000
# Bound to 0.0.0.0 only because the container needs it. This app is deliberately
# vulnerable - never expose it outside your own machine.
CMD ["python", "-m", "uvicorn", "store.app:app", "--host", "0.0.0.0", "--port", "8000"]
