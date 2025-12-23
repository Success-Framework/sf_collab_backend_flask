# 1. Update packages
sudo apt update

# 2. Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

# 3. Add Docker’s official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. Set up the repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Update apt again
sudo apt update

# 6. Install Docker and Docker Compose plugin
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 7. Enable and start Docker service
sudo systemctl enable docker
sudo systemctl start docker

# 8. Test Docker
docker --version
docker compose version
# 9. Login to Docker Hub
docker login --username your_docker_username --password-stdin <<EOF
your_docker_password

# Pull the latest image from Docker Hub
docker pull your_docker_username/sforger_api:latest

# Run Docker Compose in detached mode and build
sudo docker compose -f docker-compose-prod.yml up -d --build