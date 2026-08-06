FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY agent_registry_service /app/agent_registry_service

ENV ARZIN_BIND_HOST=0.0.0.0
ENV ARZIN_BIND_PORT=8080

EXPOSE 8080
CMD ["python", "-m", "agent_registry_service.main"]
