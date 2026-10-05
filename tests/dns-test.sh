#!/bin/bash
set -e

DOMAIN="app.team1.test"
EXPECTED_IP="10.7.18.79"
DNS="10.7.19.196"

echo "=== DNS RESOLUTION TEST ==="
echo "Domain: $DOMAIN"
echo "Expected A record: $EXPECTED_IP via $DNS"
echo

echo "1. Query team DNS directly"
RESOLVED_IP=$(dig +short @"$DNS" "$DOMAIN" | tail -n1)
echo "Resolved: $RESOLVED_IP"

if [ "$RESOLVED_IP" != "$EXPECTED_IP" ]; then
  echo "[FAIL] expected $EXPECTED_IP"
  exit 1
fi
echo "[PASS] authoritative answer from Mac 1"

echo
echo "2. Flags / ANSWER section"
dig @"$DNS" "$DOMAIN" | grep -E -A 2 "ANSWER SECTION|flags:"
echo
echo "=== DNS TEST PASSED ==="
