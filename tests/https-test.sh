#!/bin/bash
set -e

URL="${URL:-https://app.team1.test:8443/api/status}"

echo "=== HTTPS TEST ==="
echo "URL: $URL"
echo "Do not pass -k. The client must trust the mkcert/OpenSSL CA."
echo

curl -i "$URL"
echo
echo "=== HTTPS TEST PASSED ==="
