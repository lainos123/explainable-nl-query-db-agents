# Docker Setup Guide

## What is Docker?
Docker packages your app and all its dependencies into a "container" that runs the same way everywhere. Think of it like a shipping container for software!

## Prerequisites
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Make sure Docker is running (you'll see the whale icon in your system tray)

## Quick Start

### 1. Set up environment variables
```bash
# Copy the example environment file
cp env.example .env

# Edit .env and add your actual values
# - Add your OpenAI API key
# - Change the secret key if you want
```

### 2. Build and run everything
```bash
# Navigate to the web_app directory
cd web_app

# Build all containers
docker-compose build

# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

### 3. Access your app
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## Common Commands

### Start/Stop
```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove everything (including data)
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
```

### Rebuild after changes
```bash
# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up --build
```

### Access containers
```bash
# Get into backend container
docker-compose exec backend bash

# Get into frontend container
docker-compose exec frontend sh
```

## Troubleshooting

### Port already in use
If you get "port already in use" errors:
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000

# Kill the process or change ports in docker-compose.yml
```

### Permission issues
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Clear everything and start fresh
```bash
# Stop and remove everything
docker-compose down -v

# Remove all images
docker system prune -a

# Start fresh
docker-compose up --build
```

## What Each File Does

- **Dockerfile.backend**: Instructions to build the Django container
- **Dockerfile.frontend**: Instructions to build the Next.js container  
- **docker-compose.yml**: Orchestrates all containers together
- **.dockerignore**: Tells Docker what files to ignore
- **env.example**: Template for environment variables
