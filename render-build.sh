#!/usr/bin/env bash
# exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Create static directory
mkdir -p app/static
cp -r frontend/dist/* app/static/