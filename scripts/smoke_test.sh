#!/bin/sh
set -eu

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "Checking readiness..."
curl --fail --silent "$BASE_URL/health/ready"
echo

echo "Creating user..."
curl --fail --silent       -X POST "$BASE_URL/users"       -H "Content-Type: application/json"       -d '{"name":"Paulina","email":"paulina@example.com"}'
echo

echo "Listing data..."
curl --fail --silent "$BASE_URL/users"
echo
