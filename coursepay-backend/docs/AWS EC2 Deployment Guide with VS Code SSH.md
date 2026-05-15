# AWS EC2 Deployment Guide for Django, PostgreSQL, and Docker

This guide explains how to deploy this Django backend on an AWS EC2 Ubuntu server using VS Code SSH, Git, Docker, and Docker Compose.

The goal is simple:

```text
Your Laptop + VS Code
        |
        | SSH connection
        v
AWS EC2 Ubuntu Server
        |
        | Docker Compose
        v
Django container + PostgreSQL container
```

---

## 1. What EC2 Is

EC2 means **Elastic Compute Cloud**.

In simple words, EC2 is a Linux computer running inside AWS cloud. Instead of running the Django project only on your laptop, you rent a small server from AWS and keep your backend running there.

Why it is required:

- Razorpay webhooks need a public server URL.
- Other users cannot access `localhost` on your laptop.
- EC2 gives us a public IP address.
- Docker can run Django and PostgreSQL on the server in the same way it runs locally.

---

## 2. Create an EC2 Instance

### Recommended Starting Setup

Use this for learning and testing:

```text
AMI: Ubuntu Server 22.04 LTS or 24.04 LTS
Instance type: t2.micro or t3.micro
Storage: 20 GB minimum
Key pair: Create/download .pem file
Security group: Allow SSH and app port
```

What these things mean:

| Item | What it is | Why it is required |
| --- | --- | --- |
| AMI | Operating system image | Gives the server Ubuntu Linux |
| Instance type | CPU/RAM size | Decides how powerful the server is |
| Storage | Server disk space | Stores code, Docker images, database volume |
| Key pair | SSH login key | Lets your laptop securely connect to EC2 |
| Security group | Firewall rules | Controls which ports are open from the internet |

---

## 3. Security Group Rules

Open these inbound rules in the EC2 security group:

| Type | Port | Source | Why |
| --- | --- | --- | --- |
| SSH | `22` | Your IP only | Required for VS Code SSH / terminal login |
| Custom TCP | `8000` | `0.0.0.0/0` | Required to access Django dev server from browser |
| HTTP | `80` | `0.0.0.0/0` | Required later if using Nginx |
| HTTPS | `443` | `0.0.0.0/0` | Required later for SSL |

For the current Docker setup, Django runs on port `8000`, so port `8000` must be open.

Important: for production, avoid exposing Django development server directly forever. Later we should put Nginx + Gunicorn in front of it.

---

## 4. Connect to EC2 Using Normal SSH First

After creating the instance, AWS gives a public IP like:

```text
13.201.45.100
```

From your local terminal:

```bash
ssh -i path/to/your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

Example:

```bash
ssh -i coursepay-key.pem ubuntu@13.201.45.100
```

What this command does:

- `ssh` starts a secure remote login.
- `-i coursepay-key.pem` tells SSH which private key to use.
- `ubuntu` is the default username for Ubuntu EC2.
- `YOUR_EC2_PUBLIC_IP` is the public address of your server.

Why this is required:

- We need to install Git, Docker, and run deployment commands on the EC2 machine.

If the key permission gives an error on Linux/Mac:

```bash
chmod 400 coursepay-key.pem
```

This protects the private key so SSH accepts it.

On Windows, keep the `.pem` file somewhere safe like:

```text
C:\Users\YourName\.ssh\coursepay-key.pem
```

---

## 5. Use VS Code SSH

VS Code SSH lets you open the EC2 server like a normal project folder inside VS Code.

### Install Extension

In VS Code:

```text
Extensions -> Search "Remote - SSH" -> Install
```

What it does:

- Adds remote server support to VS Code.
- Lets VS Code edit files directly on EC2.
- Lets you open an EC2 terminal inside VS Code.

### Add SSH Config

Open VS Code command palette:

```text
Ctrl + Shift + P
```

Search:

```text
Remote-SSH: Open SSH Configuration File
```

Add:

```sshconfig
Host coursepay-ec2
    HostName YOUR_EC2_PUBLIC_IP
    User ubuntu
    IdentityFile C:\Users\YourName\.ssh\coursepay-key.pem
    ServerAliveInterval 60
    ServerAliveCountMax 5
```

What each line does:

| Line | Meaning |
| --- | --- |
| `Host coursepay-ec2` | Friendly name shown in VS Code |
| `HostName` | EC2 public IP |
| `User ubuntu` | Linux username |
| `IdentityFile` | Path to your `.pem` key |
| `ServerAliveInterval 60` | Sends keep-alive signal every 60 seconds |
| `ServerAliveCountMax 5` | Allows a few missed signals before disconnect |

Why keep-alive is required:

- EC2 SSH sometimes disconnects when the network is idle.
- VS Code may show "connection lost" if Wi-Fi changes or the laptop sleeps.
- Keep-alive reduces random connection breaks.

### Connect from VS Code

Open command palette:

```text
Remote-SSH: Connect to Host
```

Select:

```text
coursepay-ec2
```

Then open the server folder:

```text
/home/ubuntu
```

---

## 6. Update the Server

Run this on EC2:

```bash
sudo apt update
```

What it does:

- Downloads the latest package list from Ubuntu repositories.

Why it is required:

- Without this, Ubuntu may not know the latest versions of Git, Docker dependencies, and security patches.

Then run:

```bash
sudo apt upgrade -y
```

What it does:

- Upgrades installed packages.

Why it is required:

- Keeps the server secure and avoids dependency problems.

---

## 7. Install Git

```bash
sudo apt install git -y
```

What it does:

- Installs Git on the EC2 server.

Why it is required:

- Git pulls your project code from GitHub or another remote repository.

Check installation:

```bash
git --version
```

---

## 8. Install Docker

Install Docker using Ubuntu packages:

```bash
sudo apt install docker.io -y
```

What it does:

- Installs Docker Engine.

Why it is required:

- Docker runs Django and PostgreSQL inside containers.

Start Docker:

```bash
sudo systemctl start docker
```

Enable Docker on server restart:

```bash
sudo systemctl enable docker
```

What this does:

- Starts Docker automatically if EC2 reboots.

Check Docker:

```bash
docker --version
```

---

## 9. Allow Ubuntu User to Run Docker

By default, Docker commands require `sudo`.

Run:

```bash
sudo usermod -aG docker ubuntu
```

What it does:

- Adds the `ubuntu` user to the Docker group.

Why it is required:

- Lets us run `docker compose` without writing `sudo` every time.

Important: log out and reconnect after this:

```bash
exit
```

Then reconnect using SSH or VS Code SSH.

Check:

```bash
docker ps
```

If this works without `sudo`, Docker permission is fixed.

---

## 10. Install Docker Compose

Modern Docker usually includes Compose as:

```bash
docker compose version
```

If this command works, you are ready.

If it does not work, install the Compose plugin:

```bash
sudo apt install docker-compose-plugin -y
```

What Docker Compose does:

- Reads `docker-compose.yml`.
- Starts multiple containers together.
- Creates a Docker network.
- Connects Django container to PostgreSQL container.
- Manages volumes for database persistence.

---

## 11. Clone the Project on EC2

Go to the home folder:

```bash
cd /home/ubuntu
```

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
```

Example:

```bash
git clone https://github.com/your-username/coursepay-backend.git
```

Enter the project:

```bash
cd coursepay-backend
```

What this does:

- Downloads the project code onto EC2.

Why it is required:

- Docker needs the local `Dockerfile`, `docker-compose.yml`, Django code, and `requirements.txt`.

---

## 12. Create the `.env` File on EC2

On EC2, create or edit:

```bash
nano .env
```

Example values:

```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=change-this-password

Django_SECRET_KEY=change-this-secret-key
DEBUG=True

REZORPAY_KEY_ID=your_razorpay_key_id
REZORPAY_KEY_SECRET=your_razorpay_key_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

Important for Docker:

```env
DB_HOST=db
```

Why:

- Inside Docker Compose, PostgreSQL service name is `db`.
- Django should connect to `db`, not `127.0.0.1`.
- `127.0.0.1` inside the Django container means the Django container itself, not the PostgreSQL container.

Why `.env` is required:

- Stores secrets and database settings outside code.
- Lets local and EC2 environments use different values.

---

## 13. Update Django `ALLOWED_HOSTS`

Current project setting:

```python
ALLOWED_HOSTS = ['192.168.0.135', 'localhost', '127.0.0.1', '.ngrok-free.dev']
```

On EC2, Django also needs to allow the EC2 public IP or domain.

Example:

```python
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'YOUR_EC2_PUBLIC_IP',
    '.ngrok-free.dev',
]
```

What `ALLOWED_HOSTS` does:

- It is Django's allowed guest list.
- If a request comes from a host not in this list, Django blocks it with `DisallowedHost`.

Why it is required:

- Protects the app from fake Host header attacks.
- Required when `DEBUG=False`.
- Useful even while testing on EC2.

---

## 14. Build and Start Containers

From the project folder:

```bash
docker compose up --build -d
```

What it does:

- `docker compose` reads `docker-compose.yml`.
- `up` starts the services.
- `--build` rebuilds the Django image from the `Dockerfile`.
- `-d` runs containers in background mode.

Why it is required:

- Starts both Django and PostgreSQL on EC2.

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View only Django logs:

```bash
docker compose logs -f web
```

---

## 15. Run Migrations

```bash
docker compose exec web python manage.py migrate
```

What it does:

- Enters the running `web` container.
- Runs Django migrations.
- Creates database tables inside PostgreSQL.

Why it is required:

- Without migrations, Django models do not have actual database tables.

---

## 16. Create Django Admin User

```bash
docker compose exec web python manage.py createsuperuser
```

What it does:

- Creates an admin login for Django admin panel.

Why it is required:

- Lets you manage courses, orders, payments, and users from Django admin.

If you want to use environment variables:

```bash
docker compose exec web python manage.py createsuperuser --noinput
```

This uses:

```env
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
```

---

## 17. Test in Browser

Open:

```text
http://YOUR_EC2_PUBLIC_IP:8000/
```

Admin:

```text
http://YOUR_EC2_PUBLIC_IP:8000/admin/
```

If browser does not open:

Check EC2 security group:

```text
Port 8000 must be open.
```

Check container:

```bash
docker compose ps
```

Check logs:

```bash
docker compose logs -f web
```

---

## 18. Useful Docker Commands on EC2

### Stop Containers

```bash
docker compose stop
```

Stops containers but keeps them.

### Start Existing Containers

```bash
docker compose start
```

Starts stopped containers again.

### Restart After Code Changes

```bash
docker compose up --build -d
```

Rebuilds the app image and restarts services.

### Enter Django Container

```bash
docker compose exec web bash
```

Useful for debugging from inside the container.

### See RAM and CPU Usage

```bash
docker stats
```

Useful when EC2 becomes slow or containers stop unexpectedly.

---

## 19. Memory Issue on Small EC2 Instances

Small EC2 instances like `t2.micro` or `t3.micro` usually have around 1 GB RAM.

Common symptoms:

- `docker compose up --build` suddenly stops.
- SSH disconnects during Docker build.
- Server becomes very slow.
- PostgreSQL container exits.
- Terminal shows `Killed`.
- `pip install` fails during image build.

Why it happens:

- Docker image build uses RAM.
- PostgreSQL also needs memory.
- Python package installation can spike memory.
- Ubuntu itself needs memory.

### Check Memory

```bash
free -h
```

What it does:

- Shows available RAM and swap.

Check running processes:

```bash
top
```

What it does:

- Shows which process is using CPU/RAM.

### Add Swap Memory

Swap is fake RAM using disk space. It is slower than real RAM but helps prevent crashes.

Create 2 GB swap:

```bash
sudo fallocate -l 2G /swapfile
```

Protect swap file:

```bash
sudo chmod 600 /swapfile
```

Format it as swap:

```bash
sudo mkswap /swapfile
```

Turn it on:

```bash
sudo swapon /swapfile
```

Make it permanent after reboot:

```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Check:

```bash
free -h
```

Why swap helps:

- Docker builds and PostgreSQL get breathing room.
- The server is less likely to kill processes.

Better long-term fix:

- Use at least `t3.small` or `t3.medium` for smoother Docker + PostgreSQL deployment.

---

## 20. SSH / VS Code Connection Keeps Breaking

Common causes:

- Laptop internet is unstable.
- Laptop goes to sleep.
- EC2 public IP changed after stop/start.
- VS Code SSH server got stuck.
- Server is overloaded due to low RAM.
- Security group does not allow your current IP.

### Fix 1: Add SSH Keep Alive

In your local SSH config:

```sshconfig
Host coursepay-ec2
    HostName YOUR_EC2_PUBLIC_IP
    User ubuntu
    IdentityFile C:\Users\YourName\.ssh\coursepay-key.pem
    ServerAliveInterval 60
    ServerAliveCountMax 5
```

What it does:

- Sends small signals so the SSH session does not look idle.

### Fix 2: Use Elastic IP

Problem:

- EC2 public IP can change when you stop and start the instance.

Solution:

- Create an Elastic IP.
- Attach it to the EC2 instance.

Why it helps:

- Your SSH config keeps working.
- Razorpay webhook URL does not change every time.

### Fix 3: Restart VS Code Remote Server

In VS Code command palette:

```text
Remote-SSH: Kill VS Code Server on Host
```

Then reconnect.

Why it helps:

- Sometimes the VS Code remote agent gets stuck on EC2.

### Fix 4: Check Server Memory

```bash
free -h
```

If memory is almost full, add swap or stop containers:

```bash
docker compose stop
```

### Fix 5: Keep Long Commands Running Even if SSH Drops

Install `tmux`:

```bash
sudo apt install tmux -y
```

Start a session:

```bash
tmux new -s deploy
```

Run deployment commands inside tmux.

If SSH breaks, reconnect and run:

```bash
tmux attach -t deploy
```

What tmux does:

- Keeps your terminal session alive on EC2.
- Docker builds continue even if your SSH connection drops.

Why it is useful:

- Very helpful when `docker compose up --build -d` takes time.

---

## 21. Common Problems and Fixes

| Problem | Cause | Fix |
| --- | --- | --- |
| Browser cannot open app | Port `8000` blocked | Open port `8000` in security group |
| `DisallowedHost` error | EC2 IP not in `ALLOWED_HOSTS` | Add EC2 public IP to Django settings |
| Django cannot connect to DB | `DB_HOST=127.0.0.1` inside Docker | Use `DB_HOST=db` |
| Docker permission denied | User not in Docker group | Run `sudo usermod -aG docker ubuntu`, then reconnect |
| Build gets killed | Low RAM | Add swap or use bigger instance |
| SSH keeps disconnecting | Idle timeout, weak network, low RAM | Add keep-alive, use tmux, add swap |
| EC2 IP changed | Instance was stopped/started | Use Elastic IP |
| Postgres data disappeared | Docker volume deleted | Avoid `docker compose down -v` unless you want to delete DB |

---

## 22. Deployment Command Checklist

Fresh EC2 setup:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install git docker.io docker-compose-plugin tmux -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu
```

Then logout and reconnect.

Project setup:

```bash
cd /home/ubuntu
git clone YOUR_REPOSITORY_URL
cd coursepay-backend
nano .env
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose ps
```

After code update:

```bash
cd /home/ubuntu/coursepay-backend
git pull
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose logs -f web
```

---

## 23. Important Production Notes

The current setup is good for learning and first deployment testing.

Before real production:

- Set `DEBUG=False`.
- Use a strong secret key.
- Add EC2 IP or domain to `ALLOWED_HOSTS`.
- Use real Razorpay production keys.
- Use Nginx as reverse proxy.
- Use Gunicorn instead of Django `runserver`.
- Add HTTPS using Certbot.
- Restrict CORS instead of `CORS_ALLOW_ALL_ORIGINS=True`.
- Take PostgreSQL backups.

Current command in `Dockerfile`:

```dockerfile
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

This is okay for learning deployment, but for production it should later become Gunicorn.

---

## 24. Mental Model

Think of deployment like this:

```text
EC2 = rented computer
Ubuntu = operating system
SSH = remote login tunnel
VS Code SSH = edit EC2 files from laptop
Git = brings project code to EC2
Docker = runs app in isolated boxes
Docker Compose = starts Django + PostgreSQL together
Security Group = AWS firewall
ALLOWED_HOSTS = Django firewall
Swap = emergency backup memory
tmux = terminal that survives SSH disconnect
```

If something breaks, check in this order:

```text
1. Is EC2 running?
2. Is SSH working?
3. Is Docker running?
4. Are containers running?
5. Are logs showing errors?
6. Is port 8000 open?
7. Is EC2 IP inside ALLOWED_HOSTS?
8. Is DB_HOST=db?
9. Is memory full?
```
