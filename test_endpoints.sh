#!/bin/bash

# Colors for output
GREEN="[0;32m"
RED="[0;31m"
NC="[0m"

# Base URL
BASE_URL="https://aso-tool.onrender.com"

echo "🔍 Testing ASO Tool API Endpoints..."

# 1. Health Check
echo -e "
${GREEN}Testing Health Check Endpoint${NC}"
curl -s "$BASE_URL/health" | jq .

# 2. App Analysis
echo -e "
${GREEN}Testing App Analysis Endpoint${NC}"
curl -s "$BASE_URL/api/analyze/app/com.badhobuyer" | jq .

# 3. Competitor Analysis
echo -e "
${GREEN}Testing Competitor Analysis Endpoint${NC}"
curl -s -X POST "$BASE_URL/api/analyze/competitors/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.badhobuyer",
    "competitor_ids": ["com.udaan.android", "club.kirana"]
  }' | jq .

# 4. Keyword Analysis
echo -e "
${GREEN}Testing Keyword Analysis Endpoint${NC}"
curl -s -X POST "$BASE_URL/api/analyze/keywords/discover" \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "com.badhobuyer",
    "competitor_ids": ["com.udaan.android", "club.kirana"]
  }' | jq .

echo -e "
${GREEN}Tests Complete!${NC}"
