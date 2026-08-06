FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY policy_plane_service /app/policy_plane_service

ENV ARZIN_BIND_HOST=0.0.0.0
ENV ARZIN_BIND_PORT=8081

EXPOSE 8081
CMD ["python", "-m", "policy_plane_service.main"]
