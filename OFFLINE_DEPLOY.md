# Offline Deployment Guide (No Internet in LXC)

Your Proxmox LXC container cannot access the internet for Docker builds.
Here are three ways to deploy:

## Option 1: Build on Proxmox Host, Transfer to LXC (Recommended)

On your **Proxmox HOST** (not inside LXC):

```bash
cd /opt/indian_stock_tracker

# Build images
docker compose build

# Save images
docker save indian_stock_tracker-backend > backend.tar
docker save indian_stock_tracker-frontend > frontend.tar
docker save indian_stock_tracker-scheduler > scheduler.tar

# Transfer to LXC (replace with your LXC IP)
scp *.tar root@192.168.10.25:/opt/indian_stock_tracker/
```

Inside your **LXC container**:

```bash
cd /opt/indian_stock_tracker

# Load images
docker load < backend.tar
docker load < frontend.tar
docker load < scheduler.tar

# Start (no build needed!)
docker compose -f docker-compose.yml up -d
```

## Option 2: Use Pre-built Images (No Build at All)

The `docker-compose.offline.yml` uses official Docker Hub images directly:
- `python:3.11-slim` for backend & scheduler
- `nginx:alpine` for frontend
- `postgres:16-alpine` for database
- `redis:7-alpine` for cache

These are pulled once and cached. Inside LXC:

```bash
cd /opt/indian_stock_tracker

# Use the offline compose file
docker compose -f docker-compose.offline.yml up -d

# Note: First run installs pip packages at runtime (takes ~2-3 minutes)
# Subsequent restarts are fast because packages are cached in the container
```

## Option 3: Fix LXC Internet Access (One-time)

Your LXC container likely needs DNS configuration. On the **Proxmox HOST**:

```bash
# Edit LXC config
nano /etc/pve/lxc/<LXC_ID>.conf

# Add these lines:
lxc.cgroup2.devices.allow = c 10:200 rwm
lxc.mount.entry = /dev/net/tun dev/net/tun none bind,create=file

# Inside LXC, fix DNS:
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# Make it permanent
apt install -y resolvconf
echo "nameserver 8.8.8.8" > /etc/resolvconf/resolv.conf.d/head
resolvconf -u
```

Then restart Docker inside LXC:
```bash
systemctl restart docker
```

## Current Status

The frontend is now a static HTML file (no React build needed) that fetches data from the API.
It auto-refreshes every 30 seconds.

Access the app at: http://your-lxc-ip:3000
