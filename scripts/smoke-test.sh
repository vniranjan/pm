#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ROOT_STATUS="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/)"
if [[ "$ROOT_STATUS" != "200" ]]; then
  echo "Expected / to return 200, got $ROOT_STATUS"
  exit 1
fi

HEALTH_JSON="$(curl -s http://127.0.0.1:8000/api/health)"
if [[ "$HEALTH_JSON" != *'"status":"ok"'* ]]; then
  echo "Health response did not include expected status. Response: $HEALTH_JSON"
  exit 1
fi

echo "Smoke test passed."
