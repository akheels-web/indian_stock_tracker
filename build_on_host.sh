#!/bin/bash
# Build images on Proxmox host (which has internet) and save them
# Run this script on the Proxmox HOST (not inside LXC)

set -e

LXC_IP="192.168.10.25"  # Change this to your LXC container IP
LXC_NAME="stocks"       # Change this to your LXC container name
PROJECT_DIR="/opt/indian_stock_tracker"

echo "Building images on Proxmox host..."
cd "$PROJECT_DIR"

# Build all images
docker compose build

# Save images to tar files
docker save indian_stock_tracker-backend:latest > backend.tar
docker save indian_stock_tracker-frontend:latest > frontend.tar
docker save indian_stock_tracker-scheduler:latest > scheduler.tar

echo "Transferring images to LXC container $LXC_IP..."
scp backend.tar frontend.tar scheduler.tar root@$LXC_IP:/opt/indian_stock_tracker/

echo "Loading images inside LXC..."
pct exec $LXC_NAME -- bash -c "cd /opt/indian_stock_tracker && docker load < backend.tar && docker load < frontend.tar && docker load < scheduler.tar"

echo "Starting containers inside LXC..."
pct exec $LXC_NAME -- bash -c "cd /opt/indian_stock_tracker && docker compose up -d"

echo "Cleaning up tar files..."
rm -f backend.tar frontend.tar scheduler.tar
ssh root@$LXC_IP "cd /opt/indian_stock_tracker && rm -f backend.tar frontend.tar scheduler.tar"

echo "Done!"
