# SF Collab Backend Flask Deployment Guide

This guide provides detailed instructions for deploying the **SF Collab Backend** Flask application using **Docker** and **Docker Compose**, including setup for development and production environments, environment configuration, and deployment to a remote server.

---

## Prerequisites

* **Git** installed on your local machine.
* **Docker** and **Docker Compose** installed. Follow the official guides:

  * [Docker](https://docs.docker.com/get-docker/)
  * [Docker Compose](https://docs.docker.com/compose/install/)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Success-Framework/sf_collab_backend_flask.git
cd sf_collab_backend_flask
```

---

### 2. Configure Environment Variables

Create `.env.development` and `.env.production` files in the project root, based on `env.example`. Fill in all required values for your environment:

```env
PORT=5000
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
JWT_SECRET_KEY=<generate similarly>
GITHUB_CLIENT_ID=<your-github-client-id>
GITHUB_CLIENT_SECRET=<your-github-client-secret>
GOOGLE_CLIENT_ID=<your-google-client-id>
GOOGLE_CLIENT_SECRET=<your-google-client-secret>

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<your-email@gmail.com>
MAIL_PASSWORD=<your-app-password>
MAIL_DEFAULT_SENDER=noreply@example.com

MYSQL_USER=sfcollab
MYSQL_PASSWORD=sfcollab_pass
MYSQL_DATABASE=defaultdb
MYSQL_ROOT_PASSWORD=sfcollab_pass
DATABASE_URL=mysql+pymysql://sfcollab:sfcollab_pass@db:3306/defaultdb

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

LOG_LEVEL=INFO
LOG_FILE=app.log
FLASK_ENV=development  # or production
```

---

### 3. Development Setup

Build and run the Docker containers for development:

```bash
cd docker
docker-compose -f docker-compose-dev.yml up -d --build
cd ..
```

Your development backend will be available at: `http://localhost:5000` or `http://localhost:5001` depending on your port mapping.

---

### 4. Production Setup

#### Build and Push Docker Image

```bash
docker buildx build --platform linux/amd64 -t sforger_api:latest .
docker tag sforger_api:latest <your_dockerhub_username>/sforger_api:latest
docker push <your_dockerhub_username>/sforger_api:latest
```

#### Transfer Files to Production Server

```bash
scp -i <your_key_path>/sf_key_pair.pem ./docker/docker-compose-prod.yml \
   ./docker/db/init.sql ./.env.production ./docker/setup.sh \
   ubuntu@<your_server_ip>:/home/ubuntu/
```

#### Connect to Server and Deploy

```bash
ssh -i <your_key_path>/sf_key_pair.pem ubuntu@<your_server_ip>
chmod +x setup.sh
nano setup.sh  # Update Docker Hub credentials if necessary
./setup.sh
```

This will set up **SF Collab Backend**, along with **MySQL** and **Redis** services, running in Docker containers. Nginx is configured as a reverse proxy to forward requests from port 80 to the Flask app on port 5000.

> Refer to [Nginx Reverse Proxy Setup](./nginx_reverse_proxy.md) for detailed configuration.

---

### 5. Access the Application

* **Development:** `http://localhost:5000`
* **Production:** `https://api.sfcollab.com`

---

### Notes

* Ensure all sensitive credentials are set correctly in the environment files.
* Use `docker logs <container_name>` to troubleshoot any issues with containerized services.
* Make sure MySQL and Redis containers are running before starting the Flask app.
