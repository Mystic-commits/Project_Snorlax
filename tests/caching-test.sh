#!/bin/bash
# Live Task F path: /api/cached with ETag "v1" (Backend B, also on A).
# This is the URL that returned 304 through nginx on 1 Oct.

set -e

URL="${URL:-https://app.team1.test:8443/api/cached}"

echo "=== TASK F: HTTP CACHING TEST ==="
echo "URL: $URL"
echo

RESPONSE=$(curl -s -i "$URL")
echo "$RESPONSE" | grep -E -i "HTTP/|Cache-Control|ETag|X-Backend"

ETAG=$(echo "$RESPONSE" | grep -i "^ETag:" | tr -d '\r' | awk '{print $2}')
echo
echo "Observed ETag: $ETAG"

if [ -z "$ETAG" ]; then
  ETAG='"v1"'
fi

echo
echo "Conditional request If-None-Match: $ETAG"
COND_RESPONSE=$(curl -s -i -H "If-None-Match: $ETAG" "$URL")
echo "$COND_RESPONSE" | grep -E -i "HTTP/|ETag|Cache-Control|X-Backend"

STATUS_CODE=$(echo "$COND_RESPONSE" | head -n1 | awk '{print $2}')
if [ "$STATUS_CODE" != "304" ]; then
  echo "[FAIL] expected 304, got $STATUS_CODE"
  echo "Retry against one origin: URL=http://10.7.31.47:3002/api/cached $0"
  exit 1
fi

echo
echo "=== HTTP CACHING TEST PASSED ==="
