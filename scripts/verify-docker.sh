#!/usr/bin/env sh
set -eu

BASE_URL="${BASE_URL:-http://localhost:8000}"

cleanup() {
  docker compose down
}

on_failure() {
  echo "Docker smoke verification failed. Recent logs:"
  docker compose logs --no-color || true
}

trap cleanup EXIT
trap on_failure HUP INT TERM

docker compose build
docker compose up -d

attempt=1
until python -c "import urllib.request; urllib.request.urlopen('${BASE_URL}/healthz', timeout=2).read()" >/dev/null 2>&1; do
  if [ "$attempt" -ge 30 ]; then
    on_failure
    exit 1
  fi
  attempt=$((attempt + 1))
  sleep 2
done

python -c "import urllib.request; urllib.request.urlopen('${BASE_URL}/healthz', timeout=5).read()"
python -c "import urllib.request; urllib.request.urlopen('${BASE_URL}/login', timeout=5).read()"
python -c "import urllib.request; urllib.request.urlopen('${BASE_URL}/register', timeout=5).read()"
python -c "import urllib.request; opener=urllib.request.build_opener(urllib.request.HTTPRedirectHandler); response=opener.open('${BASE_URL}/dashboard', timeout=5); assert response.geturl().endswith('/login')"

docker compose ps
docker compose logs --no-color
