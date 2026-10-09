FROM python:3.12-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=build /install /usr/local
COPY src ./src
COPY datos ./datos
ENV PYTHONPATH=/app/src
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "aula.api.app:app", "--host", "0.0.0.0", "--port", "8000"]