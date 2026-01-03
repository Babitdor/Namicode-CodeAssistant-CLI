---
name: docker-deploy
description: Expert capability for containerizing applications, authoring optimized Dockerfiles, managing images and containers, orchestrating multi-service stacks with Docker Compose, and handling networking, volumes, and security best practices.
---

# Docker Deploy Skill

## Overview

This skill enables the comprehensive lifecycle management of containerized applications using Docker. It guides the transformation of source code into portable, isolated containers, ensuring consistency across development, testing, and production environments. Key capabilities include writing efficient Dockerfiles, managing container networking and storage volumes, and orchestrating complex multi-container applications using Docker Compose. By solving environment parity issues ("it works on my machine") and simplifying dependency management, this skill is essential for modern DevOps workflows, microservices architectures, and CI/CD pipelines.

## Core Competencies

- **Dockerfile Authoring**: Creating optimized, secure, and minimal container images using multi-stage builds, specific base image tags, and proper layer caching strategies.
- **Container Lifecycle Management**: Building, running, stopping, removing, and inspecting containers using the Docker CLI with precise flag configurations.
- **Multi-Container Orchestration**: Defining and running multi-service applications (e.g., Web App + Database + Cache) using Docker Compose YAML files.
- **Data Persistence**: Configuring volumes and bind mounts to manage stateful data, ensuring database persistence and sharing data between the host and containers.
- **Networking**: Implementing custom bridge networks to facilitate secure communication between containers while isolating them from the outside world.
- **Image Optimization**: Reducing image size and attack surface using alpine-based images, `.dockerignore` files, and non-root user execution.
- **Troubleshooting & Debugging**: Executing commands inside running containers, viewing logs, and diagnosing startup failures and networking issues.

## When to Use This Skill

### Primary Use Cases
- **Containerizing a Legacy Application**: When a user needs to take an existing Python, Node.js, Go, or Java application and package it so it runs identically on any server.
- **Setting Up Local Development Environments**: When a developer needs to spin up dependencies like PostgreSQL, Redis, or Elasticsearch without installing them natively on their host OS.
- **Deploying Microservices**: When breaking a monolith into smaller services that need to communicate via a virtual network and be scaled independently.
- **Standardizing CI/CD Pipelines**: When configuring a build server to create artifacts as Docker images for deployment to staging or production.

### Trigger Phrases
- "Create a Dockerfile for this application"
- "Help me set up Docker Compose for this stack"
- "How do I deploy this container to production?"
- "Optimize this Docker image size"
- "Why does my container keep crashing?"

## Detailed Instructions

### Phase 1: Assessment & Planning
1.  **Analyze Application Stack**:
    *   Identify the runtime language (e.g., Python 3.9, Node 18).
    *   List system-level dependencies (e.g., build-essential, libxml2).
    *   Determine exposed ports (e.g., 8080, 3000) and required environment variables.
2.  **Determine State Requirements**:
    *   Check if the application generates persistent data (databases, uploads, logs).
    *   Plan to use Docker Volumes for persistence if yes.
3.  **Select Base Images**:
    *   Choose an official, minimal image (e.g., `node:18-alpine` or `python:3.9-slim`) to ensure security and small size.

### Phase 2: Implementation
1.  **Create `.dockerignore`**:
    *   Exclude unnecessary files to prevent context bloat and security leaks (e.g., `node_modules`, `.git`, `__pycache__`, `.env`).
2.  **Write the Dockerfile**:
    *   Use a multi-stage build if the application requires compilation.
    *   Install dependencies before copying source code to leverage caching.
    *   Set the `USER` to a non-root user.
    *   Define the `ENTRYPOINT` or `CMD` to run the application.
3.  **Build the Image**:
    *   Execute `docker build -t app-name:tag .`
4.  **Container Execution (Single)**:
    *   Run `docker run -d -p 80:8080 -v volume_name:/path --name my-app app-name:tag`
5.  **Orchestration (Multi-Container)**:
    *   Create `docker-compose.yml` defining services, networks, and volumes.
    *   Run `docker compose up -d` to build and start the stack.

### Phase 3: Verification & Refinement
1.  **Health Check**:
    *   Verify the container is running: `docker ps`
    *   Check application logs: `docker logs <container_id>`
2.  **Network Testing**:
    *   Use `curl http://localhost:<mapped_port>` or `docker exec -it <container_id> /bin/sh` to test internal connectivity.
3.  **Cleanup**:
    *   Remove dangling images: `docker image prune`
    *   Stop and remove unused containers: `docker container prune`

## Technical Reference

### Key Commands & Tools
```bash
# Building an image with a tag
docker build -t myapp:v1 .

# Running a container in detached mode with port mapping
docker run -d -p 8080:80 --name web-server myapp:v1

# Executing a shell inside a running container for debugging
docker exec -it <container_id> /bin/sh

# Viewing logs for a specific container
docker logs -f <container_id>

# Building and starting services defined in compose file
docker compose up -d --build

# Stopping and removing containers, networks, and images created by compose
docker compose down

# Listing all Docker volumes
docker volume ls

# Removing unused Docker objects (dangling images, stopped containers, unused networks)
docker system prune
```

### Common Patterns

**Optimized Multi-Stage Dockerfile (Node.js Example)**
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production Run
FROM node:18-alpine
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Python Dockerfile with Virtual Environment**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run as non-root user
RUN useradd -m myuser
USER myuser

CMD ["python", "app.py"]
```

### Configuration Templates

**Docker Compose Template (Web + DB)**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgres://user:password@db:5432/mydb
    depends_on:
      - db
    volumes:
      - .:/app # Hot reloading for dev

  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb

volumes:
  postgres_data:
```

## Best Practices

### Do's
- **Use `.dockerignore`**: Always exclude local configuration files, dependencies, and version control to speed up builds and reduce image size.
- **Leverage Build Cache**: Order Dockerfile instructions from least frequently changing to most frequently changing (e.g., copy `requirements.txt` before source code).
- **Run as Non-Root**: Create a specific user in the Dockerfile and switch to it to minimize security risks.
- **Pin Versions**: Use specific tags for base images (e.g., `node:18.2.0` instead of `node:latest` or `node:18`) to ensure reproducibility.
- **Use Multi-Stage Builds**: Separate build tools from the final runtime image to drastically reduce the final artifact size.

### Don'ts
- **Don't Store Secrets**: Never commit passwords, API keys, or certificates inside the Dockerfile. Use environment variables or Docker Secrets at runtime.
- **Don't Run as Root**: Avoid running the application process as the root user inside the container.
- **Don't Use `latest` in Production**: The `latest` tag is a moving target and can break deployments unpredictably.
- **Don't Embed Configuration**: Keep configuration specific to the environment outside the image; inject it via environment variables or mounted config files.
- **Don't Install Unnecessary Tools**: Avoid package managers (like apt-get install) in the final stage unless strictly necessary to reduce the attack surface.

## Troubleshooting Guide

### Common Issues

#### Issue: Container Exits Immediately
**Symptoms:** `docker ps` shows the container is not running. `docker logs` shows nothing or a quick exit.
**Cause:** The main process defined in `CMD` or `ENTRYPOINT` terminated, or there is an error in the startup script preventing the application from staying alive in the foreground.
**Solution:**
1. Run `docker logs <container_id>` to see the error message.
2. Ensure the application runs in the foreground (not as a daemon/background service) so Docker can track the process.
3. Check for missing dependencies or entrypoint script permissions.

#### Issue: Permission Denied on Volume Bind Mounts
**Symptoms:** Application fails to write files to a mounted directory, or "Read-only file system" errors.
**Cause:** The UID/GID of the user inside the container does not match the permissions of the directory on the host machine.
**Solution:**
1. Adjust permissions on the host directory (`chmod 777` is insecure but effective for quick testing).
2. Configure the container to run as a user with a UID that matches the host user (using `user` directive in docker-compose or `-u` flag).
3. Use Docker Volumes instead of Bind Mounts if possible, as Docker manages the permissions for volumes automatically.

#### Issue: Port Already in Use
**Symptoms:** Error message `Bind for 0.0.0.0:8080 failed: port is already allocated`.
**Cause:** Another service (Docker container or native host process) is using the specified port on the host.
**Solution:**
1. Identify the process using the port: `lsof -i :8080` (Mac/Linux) or `netstat -ano | findstr :8080` (Windows).
2. Stop the conflicting process, or map the container to a different host port (e.g., `-p 8081:8080`).

#### Issue: Cannot Connect to Database from Web Container
**Symptoms:** Web app logs show "Connection refused" or "Unknown host" when trying to reach the DB.
**Cause:** Using `localhost` to refer to another container. `localhost` inside a container refers to itself, not other containers on the same network.
**Solution:** Use the service name defined in `docker-compose.yml` as the hostname. For example, if the service is named `db`, the connection string should be `postgres://user:pass@db:5432/mydb`.

## Examples

### Example 1: Containerizing a Python Flask Application

**User Request:** "I have a simple Flask app in `app.py` and a `requirements.txt`. I need a Dockerfile and instructions to run it."

**Approach:**
1.  Create a `.dockerignore` file containing `venv`, `.git`, `*.pyc`.
2.  Create a `Dockerfile`:
    ```dockerfile
    FROM python:3.9-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 5000
    CMD ["python", "app.py"]
    ```
3.  Build the image: `docker build -t flask-app .`
4.  Run the container: `docker run -p 5000:5000 flask-app`
5.  Verify: `curl http://localhost:5000`

**Expected Outcome:** The Flask application starts inside the container, maps port 5000 to the host, and responds to HTTP requests.

### Example 2: Multi-Container Environment with Docker Compose

**User Request:** "I need a local environment for my Next.js frontend that talks to a Redis cache. Set up Docker Compose for me."

**Approach:**
1.  Create a `Dockerfile` for Next.js (standard Node build).
2.  Create `docker-compose.yml`:
    ```yaml
    services:
      frontend:
        build: .
        ports:
          - "3000:3000"
        depends_on:
          - redis
        environment:
          - REDIS_HOST=redis
      
      redis:
        image: redis:alpine
        ports:
          - "6379:6379"
    ```
3.  Start the stack: `docker compose up -d --build`
4.  Check status: `docker compose ps`

**Expected Outcome:** Both the Next.js development server and Redis instance start simultaneously. The frontend can connect to Redis using the hostname `redis`.

## Integration Notes

### Works Well With
- **CI/CD Tools (GitHub Actions, GitLab CI)**: Automate building images and pushing to Docker Hub on code push.
- **Kubernetes (k8s)**: For advanced scaling and orchestration; Docker images are the standard artifact for K8s.
- **Nginx/Traefik**: Use as a reverse proxy in front of Docker containers to handle SSL and routing.

### Prerequisites
- **Docker Engine**: Must be installed and running on the host machine.
- **Basic CLI Knowledge**: Understanding of terminal commands and file system navigation.
- **Network Access**: Required to pull base images from Docker Hub or other registries.

## Quick Reference Card

| Task | Command/Action |
|------|----------------|
| Build Image | `docker build -t name:tag .` |
| Run Container | `docker run -d -p host:container name:tag` |
| View Logs | `docker logs <container_id>` |
| Access Shell | `docker exec -it <container_id> sh` |
| Stop Container | `docker stop <container_id>` |
| Remove Container | `docker rm <container_id>` |
| Start Compose | `docker compose up -d` |
| Stop Compose | `docker compose down` |

## Notes & Limitations

- **Platform Differences**: Docker on Mac/Windows runs inside a lightweight VM (using WSL2 or HyperKit), which can introduce file system performance differences (especially with bind mounts) compared to native Linux.
- **Orchestration Limits**: While Docker Swarm is available for clustering, this skill focuses primarily on single-host deployment and Docker Compose. For massive scale (100s of nodes), Kubernetes is the industry standard, not Docker Compose.
- **Resource Constraints**: Containers share the host kernel; resource limits (CPU/RAM) must be explicitly set using flags (e.g., `--memory="512m"`) to prevent a runaway container from crashing the host.
- **Data Persistence**: Containers are ephemeral. Unless volumes are configured, data is lost when the container is removed.

---