
# Nginx Reverse Proxy Setup for SF Collab Backend Flask

This document provides detailed instructions for configuring Nginx as a reverse proxy for the **SF Collab Backend** Flask application, enabling efficient request handling and SSL/TLS support.

---

## Prerequisites

* Server with a public IP address or domain name where the Flask application is hosted.
* SSH access to the production server.
* Root or sudo privileges.

---

## Nginx Installation

Update your system and install Nginx from the official repository:

```bash
sudo apt update
sudo apt install curl gnupg2 ca-certificates lsb-release
curl -fsSL https://nginx.org/keys/nginx_signing.key | sudo gpg --dearmor -o /usr/share/keyrings/nginx-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] http://nginx.org/packages/ubuntu $(lsb_release -cs) nginx" | sudo tee /etc/apt/sources.list.d/nginx.list
sudo apt update
sudo apt install nginx
```

Verify the installation:

```bash
nginx -v
```

---

## Nginx Configuration

### Start and Enable Nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

### Create Flask Application Configuration

Edit the Nginx configuration file:

```bash
cd /etc/nginx/conf.d/
sudo nano flaskapp.conf
sudo mv default.conf default.conf.disabled
```

### Add the Server Block

Add the following configuration to `flaskapp.conf`:

```nginx
server {
  listen 80;
  listen [::]:80;
  server_name api.sfcollab.com;  # Replace with your domain or IP

  location / {
    proxy_pass http://localhost:5000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
  }
}
```

### Verify Configuration

```bash
sudo nginx -t
```

Expected output:

```bash
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

### Reload Nginx

```bash
sudo systemctl reload nginx
```

Your Flask application is now accessible via your domain or public IP address.
