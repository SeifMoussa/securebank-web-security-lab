FROM python:3.12-slim

WORKDIR /workspace

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace/src
ENV SECUREBANK_ENV=container
ENV SECUREBANK_DEBUG=false
ENV SECUREBANK_DATABASE_URL=sqlite:////data/securebank_lab.sqlite3
ENV SECUREBANK_SECRET_KEY=change-me-for-local-lab-container-only
ENV SECUREBANK_SECURE_COOKIE=false
ENV SECUREBANK_HSTS_ENABLED=false

COPY pyproject.toml README.md ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && python -m pip install . \
    && groupadd --system securebank \
    && useradd --system --gid securebank --home-dir /home/securebank --create-home securebank \
    && mkdir -p /data \
    && chown -R securebank:securebank /data /workspace

USER securebank

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()"

CMD ["python", "-m", "uvicorn", "securebank.main:app", "--host", "0.0.0.0", "--port", "8000"]
