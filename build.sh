#!/bin/bash

# Exit on error
set -e

# Install system dependencies
apt-get update
apt-get install -y curl build-essential python3-dev

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download and install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] &amp;&amp; \. "$NVM_DIR/nvm.sh"

# Install Node.js
nvm install 20.0.0
nvm use 20.0.0

# Verify Node.js installation
node --version
npm --version

# Install frontend dependencies and build
cd frontend
npm install
npm run build
cd ..

# Create necessary directories
mkdir -p app/static

# Move frontend build to static directory
cp -r frontend/dist/* app/static/

echo "Build completed successfully!"