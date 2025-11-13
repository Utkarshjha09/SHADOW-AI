# SHADOW Voice Assistant - Deployment Guide

## Deployment Options Overview

Since SHADOW uses Ollama as the AI backend, you have multiple deployment strategies depending on your needs:

| Option | Cost | Ollama AI | Best For | Setup Time |
|--------|------|-----------|----------|------------|
| **Render (Free)** | Free | ❌ Fallback only | Testing, demos | 5 minutes |
| **VPS** | $6-12/mo | ✅ Full AI | Personal/team use | 30 minutes |
| **Docker** | $12-24/mo | ✅ Full AI | Production | 1 hour |
| **Local Desktop** | Free | ✅ Full AI | Personal use | 5 minutes |

---

## Option 1: Render Deployment (Recommended - Free)

Deploy the web interface without Ollama. Fallback responses work for basic queries.

### Features Available:
✅ Web interface with voice recognition  
✅ Hindi & English TTS  
✅ Wake word detection  
✅ Fallback responses (time, date, greetings)  
❌ Full AI conversations (no Ollama)  
⚠️ App sleeps after 15 min inactivity (free tier)

### Step-by-Step Deployment:

**1. Push to GitHub:**
```bash
git add .
git commit -m "Update deployment configuration"
git push origin main
```

**2. Create Render Account:**
- Go to [render.com](https://render.com)
- Sign up with GitHub (free)

**3. Create New Web Service:**
- Click **"New +"** → **"Web Service"**
- Connect your **SHADOW** repository
- Grant repository access

**4. Configure Service:**
```
Name: shadow-voice-assistant
Environment: Python 3
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python src/web/api_server.py
Instance Type: Free
```

**5. Add Environment Variables (Optional):**
```bash
HOST=0.0.0.0
PORT=10000
DEBUG=False
```

**6. Deploy:**
- Click **"Create Web Service"**
- Wait 2-3 minutes for build
- Access at: `https://shadow-voice-assistant.onrender.com/voice`

### After Deployment:
- Test voice interface at `/voice`
- Try wake words: "Hey Shadow", "Sunn Shadow"
- Check Hindi TTS functionality
- Fallback responses work without Ollama

---

## Option 2: VPS/Cloud Server with Ollama

Deploy on a VPS where you can install Ollama for full AI capabilities.

### Recommended Providers:
- **DigitalOcean** - $6/month (1GB RAM minimum)
- **Linode** - $5/month
- **AWS EC2** - t3.small or larger
- **Google Cloud** - e2-small instance
- **Vultr** - $6/month

### System Requirements:
- Ubuntu 22.04 or later
- 2GB RAM minimum (4GB recommended)
- 10GB disk space
- Public IP address

### Step-by-Step Setup:

**1. Create VPS Instance:**
- Choose Ubuntu 22.04 LTS
- Minimum 2GB RAM
- Get public IP address

**2. SSH into Server:**
```bash
ssh root@your-server-ip
```

**3. Install Ollama:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini
```

**4. Install Python & Dependencies:**
```bash
apt update
apt install python3 python3-pip python3-venv git -y
```

**5. Clone and Setup SHADOW:**
```bash
git clone https://github.com/YOUR_USERNAME/SHADOW.git
cd SHADOW
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**6. Run as Service (Persistent):**

Create systemd service file:
```bash
sudo nano /etc/systemd/system/shadow.service
```

Add this configuration:
```ini
[Unit]
Description=SHADOW Voice Assistant
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/SHADOW
Environment="PATH=/root/SHADOW/venv/bin"
ExecStart=/root/SHADOW/venv/bin/python src/web/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**7. Enable and Start Service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable shadow
sudo systemctl start shadow
sudo systemctl status shadow
```

**8. Configure Firewall:**
```bash
ufw allow 8000/tcp
ufw enable
```

**9. Access Your App:**
```
http://your-server-ip:8000/voice
```

### Optional: Add Domain & HTTPS

**Using Nginx:**
```bash
apt install nginx certbot python3-certbot-nginx -y

# Create Nginx config
nano /etc/nginx/sites-available/shadow
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/shadow /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Add SSL
certbot --nginx -d your-domain.com
```

Now access via: `https://your-domain.com`

---

## Option 3: Docker Deployment (Production)

## Option 3: Docker Deployment (Production)

Best for scalable production deployments with Ollama included.

### Prerequisites:
- Docker installed
- Docker Compose installed
- 4GB RAM minimum

### Step-by-Step Setup:

**1. Create Dockerfile:**
```dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 8000

CMD ["python", "src/web/api_server.py"]
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: shadow-ollama
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434"]
      interval: 30s
      timeout: 10s
      retries: 3

  shadow:
    build: .
    container_name: shadow-app
    ports:
      - "8000:8000"
    depends_on:
      - ollama
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - HOST=0.0.0.0
      - PORT=8000
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

volumes:
  ollama_data:
```

**3. Build and Run:**
```bash
docker-compose up -d
```

**4. Pull Ollama Model:**
```bash
docker exec -it shadow-ollama ollama pull phi3:mini
```

**5. Access Application:**
```
http://localhost:8000/voice
```

**6. View Logs:**
```bash
docker-compose logs -f shadow
```

**7. Stop Services:**
```bash
docker-compose down
```

---

## Option 4: Hybrid - Local Ollama + Cloud Web Interface

Keep Ollama running locally, deploy web interface to cloud with ngrok tunnel.

### Setup:

**1. Install ngrok:**
- Download from [ngrok.com](https://ngrok.com)
- Sign up for free account

**2. Start Ollama Locally:**
```bash
ollama serve
```

**3. Create ngrok Tunnel:**
```bash
ngrok http 11434
```

Copy the HTTPS forwarding URL (e.g., `https://abcd-1234.ngrok.io`)

**4. Deploy to Render:**
- Follow Option 1 steps
- Add environment variable:
  ```
  OLLAMA_HOST=https://abcd-1234.ngrok.io
  ```

**5. Update on Render:**
- Your deployed app now uses your local Ollama
- Full AI features available

**Limitations:**
- ngrok tunnel must stay active
- Free ngrok URL changes on restart
- Not suitable for production

---

## Option 5: Desktop Application (No Deployment)

Run SHADOW locally on your PC with full features.

### Setup:

**1. Install Ollama:**
- Download from [ollama.com](https://ollama.com/download)
- Install and run

**2. Pull Model:**
```bash
ollama pull phi3:mini
```

**3. Run SHADOW:**

**Windows:**
```bash
start_voice_web.bat
```

**Linux/Mac:**
```bash
./start_voice_web.sh
# or
python src/web/api_server.py
```

**4. Access:**
```
http://localhost:8000/voice
```

### Features:
✅ Full AI conversations  
✅ Hindi & English TTS  
✅ Wake word detection  
✅ No deployment needed  
✅ Complete privacy (all local)

---

## Environment Variables Reference

### For Render/Cloud Deployment:
```bash
# Server Configuration
HOST=0.0.0.0
PORT=10000
DEBUG=False

# Ollama Configuration (if available)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Security (optional)
ALLOWED_ORIGINS=*
SECRET_KEY=your-secret-key-here
```

### For Local Development:
```bash
HOST=127.0.0.1
PORT=8000
DEBUG=True
OLLAMA_HOST=http://localhost:11434
```

---

## Testing Your Deployment

### Health Check:
```bash
# Test web server
curl http://your-domain.com/api/health

# Test Ollama connection
curl http://your-domain.com/api/ollama/status
```

### Voice Interface Test:
1. Open `/voice` in browser
2. Allow microphone access
3. Say "Hey Shadow"
4. Test Hindi: "Sunn Shadow, kya haal hai?"
5. Test English: "Hey Shadow, what time is it?"

### API Endpoint Tests:
```bash
# Test chat
curl -X POST http://your-domain.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "language": "en"}'

# Test Hindi TTS
curl -X POST http://your-domain.com/api/tts/hindi \
  -H "Content-Type: application/json" \
  -d '{"text": "नमस्ते"}'
```

---

## Troubleshooting

### Render Deployment Issues:

**Build Fails:**
- Check Python version in `runtime.txt`
- Verify all packages in `requirements.txt` are compatible
- Check build logs in Render dashboard

**App Won't Start:**
- Ensure `Procfile` exists
- Check start command: `python src/web/api_server.py`
- Review application logs

**App Sleeps (Free Tier):**
- Expected behavior after 15 minutes inactivity
- First request after sleep takes 30-60 seconds
- Upgrade to paid tier for always-on

### VPS Issues:

**Ollama Not Running:**
```bash
# Check status
systemctl status ollama

# Restart
systemctl restart ollama

# View logs
journalctl -u ollama -f
```

**SHADOW Service Not Starting:**
```bash
# Check logs
journalctl -u shadow -f

# Check Python path
which python3

# Test manually
cd /root/SHADOW
source venv/bin/activate
python src/web/api_server.py
```

**Port Already in Use:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Docker Issues:

**Container Won't Start:**
```bash
# Check logs
docker-compose logs shadow

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

**Ollama Model Not Found:**
```bash
# Pull model again
docker exec -it shadow-ollama ollama pull phi3:mini

# List models
docker exec -it shadow-ollama ollama list
```

---

## Performance Optimization

### Render (Free Tier):
- App sleeps after inactivity - expected
- Use UptimeRobot to ping every 15 minutes
- Upgrade to Starter ($7/month) for always-on

### VPS:
- Use nginx reverse proxy
- Enable gzip compression
- Add CDN for static files (Cloudflare)
- Monitor with `htop` and `netstat`

### Docker:
- Limit container resources in docker-compose
- Use alpine base images to reduce size
- Implement Redis for session caching

---

## Security Best Practices

### For Production:
1. **Use HTTPS** - Required for microphone access
2. **Set SECRET_KEY** - For session security
3. **Configure CORS** - Restrict allowed origins
4. **Update Dependencies** - Regularly check for updates
5. **Monitor Logs** - Check for suspicious activity
6. **Use Firewall** - Only expose necessary ports
7. **Strong Passwords** - For VPS access
8. **Regular Backups** - Database and config files

### Example Nginx Security Headers:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
```

---

## Cost Comparison

| Option | Setup | Monthly | Pros | Cons |
|--------|-------|---------|------|------|
| **Render Free** | Free | Free | Easy setup, no maintenance | No AI, sleeps, slow |
| **Render Paid** | Free | $7 | Always-on, automatic | No Ollama support |
| **VPS** | $0 | $6-12 | Full control, Ollama works | Manual setup, maintenance |
| **Docker VPS** | $0 | $12-24 | Scalable, production-ready | Complex setup |
| **Local** | Free | Free | Full features, private | Not publicly accessible |

---

## Recommended Setup by Use Case

### Personal Use:
→ **Local Desktop** (Option 5)  
Run on your PC with full Ollama features

### Team Demo/Testing:
→ **Render Free** (Option 1)  
Quick deployment for testing web interface

### Small Team (5-10 users):
→ **VPS with Ollama** (Option 2)  
Full AI at low cost

### Production (100+ users):
→ **Docker on Cloud** (Option 3)  
Scalable with load balancing

### Development/Testing:
→ **Hybrid with ngrok** (Option 4)  
Test cloud deployment with local AI

---

## Next Steps After Deployment

1. **Monitor Performance:**
   - Set up monitoring (UptimeRobot, Pingdom)
   - Check error logs regularly
   - Monitor resource usage

2. **Gather Feedback:**
   - Test all features thoroughly
   - Get user feedback on voice recognition
   - Improve wake word detection based on usage

3. **Iterate:**
   - Add new features based on feedback
   - Update dependencies regularly
   - Improve performance bottlenecks

4. **Scale:**
   - Upgrade resources as needed
   - Add load balancer for high traffic
   - Consider CDN for global access

---

## Support & Resources

- **GitHub Issues:** Report bugs and request features
- **Documentation:** See README.md for usage guide
- **Ollama Docs:** [ollama.com/docs](https://ollama.com/docs)
- **Render Docs:** [render.com/docs](https://render.com/docs)
- **Docker Docs:** [docs.docker.com](https://docs.docker.com)

---

## Quick Reference Commands

**Render Deployment:**
```bash
git push origin main
# Deploy via Render dashboard
```

**VPS Deployment:**
```bash
ssh root@your-ip
git clone https://github.com/YOUR_USERNAME/SHADOW.git
cd SHADOW
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python src/web/api_server.py
```

**Docker Deployment:**
```bash
docker-compose up -d
docker exec -it shadow-ollama ollama pull phi3:mini
```

**Local Run:**
```bash
ollama serve &
start_voice_web.bat  # Windows
# or
python src/web/api_server.py  # Linux/Mac
```

---

**Choose the option that best fits your needs and budget. For most users starting out, Render (Option 1) is the easiest way to get SHADOW online quickly!**
