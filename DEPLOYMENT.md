# NLPCRM Deployment Guide

Complete guide for deploying NLPCRM to various platforms.

---

## 📋 Prerequisites

- Python 3.9+
- Git
- Platform account (Heroku/Railway/Render/AWS)
- Required API keys:
  - HuggingFace API Key
  - SQLite Cloud URL (optional)
  - Email credentials (SMTP/POP3)
  - WhatsApp Business API (optional)

---

## 🚀 Local Development

### Windows

```powershell
# 1. Clone repository
git clone https://github.com/Amanvarma2231/NLPCRM.git
cd NLPCRM

# 2. Run setup script
setup.bat

# 3. Configure .env file
# Edit .env with your credentials

# 4. Start application
start.bat
```

### Linux/Mac

```bash
# 1. Clone repository
git clone https://github.com/Amanvarma2231/NLPCRM.git
cd NLPCRM

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Start application
python run.py
```

**Access**: http://localhost:5000

---

## ☁️ Cloud Deployment

### Heroku

1. **Install Heroku CLI**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create nlpcrm-app
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set HF_API_KEY=your_huggingface_key
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set ADMIN_EMAIL=admin@nlpcrm.com
   heroku config:set ADMIN_PASSWORD=your_secure_password
   heroku config:set SMTP_HOST=smtp.gmail.com
   heroku config:set SMTP_PORT=587
   heroku config:set SMTP_USER=your_email@gmail.com
   heroku config:set SMTP_PASSWORD=your_app_password
   heroku config:set POP3_HOST=pop.gmail.com
   heroku config:set POP3_PORT=995
   heroku config:set POP3_USER=your_email@gmail.com
   heroku config:set POP3_PASSWORD=your_app_password
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Open Application**
   ```bash
   heroku open
   ```

**Note**: Heroku uses the `Procfile` for deployment configuration.

---

### Railway

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Set Environment Variables**
   ```bash
   railway variables set HF_API_KEY=your_key
   railway variables set SECRET_KEY=your_secret
   # Add all other variables
   ```

5. **Deploy**
   ```bash
   railway up
   ```

**Alternative**: Connect GitHub repository via Railway dashboard for automatic deployments.

---

### Render

1. **Create Account** at https://render.com

2. **New Web Service**
   - Connect GitHub repository
   - Select branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --workers=4 --threads=2 --worker-class=gthread --timeout=120 --bind=0.0.0.0:$PORT run:app`

3. **Environment Variables**
   Add in Render dashboard:
   ```
   HF_API_KEY=your_key
   SECRET_KEY=your_secret
   ADMIN_EMAIL=admin@nlpcrm.com
   ADMIN_PASSWORD=your_password
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email
   SMTP_PASSWORD=your_password
   POP3_HOST=pop.gmail.com
   POP3_PORT=995
   POP3_USER=your_email
   POP3_PASSWORD=your_password
   ```

4. **Deploy**
   - Render will automatically deploy on push to main branch

---

### AWS (Elastic Beanstalk)

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB**
   ```bash
   eb init -p python-3.11 nlpcrm-app
   ```

3. **Create Environment**
   ```bash
   eb create nlpcrm-env
   ```

4. **Set Environment Variables**
   ```bash
   eb setenv HF_API_KEY=your_key SECRET_KEY=your_secret
   # Add all other variables
   ```

5. **Deploy**
   ```bash
   eb deploy
   ```

6. **Open Application**
   ```bash
   eb open
   ```

---

### Google Cloud Platform (App Engine)

1. **Create `app.yaml`**
   ```yaml
   runtime: python311
   entrypoint: gunicorn -b :$PORT run:app
   
   env_variables:
     HF_API_KEY: "your_key"
     SECRET_KEY: "your_secret"
     ADMIN_EMAIL: "admin@nlpcrm.com"
     ADMIN_PASSWORD: "your_password"
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

2. **Deploy**
   ```bash
   gcloud app deploy
   ```

---

### DigitalOcean App Platform

1. **Create Account** at https://digitalocean.com

2. **Create App**
   - Connect GitHub repository
   - Select branch: `main`

3. **Configure**
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `gunicorn --workers=4 --bind=0.0.0.0:$PORT run:app`

4. **Environment Variables**
   Add in DigitalOcean dashboard

5. **Deploy**
   - Automatic deployment on push

---

## 🔧 Configuration

### Required Environment Variables

```env
# Core
SECRET_KEY=generate_random_32_char_string
ADMIN_EMAIL=admin@nlpcrm.com
ADMIN_PASSWORD=secure_password_here

# AI/NLP
HF_API_KEY=hf_your_huggingface_api_key
HF_MODEL=Qwen/Qwen2.5-7B-Instruct

# Database (Optional - falls back to local SQLite)
SQLITE_CLOUD_URL=sqlitecloud://your-cluster.sqlite.cloud:8860/db?apikey=your-key

# Email (SMTP - Sending)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_specific_password

# Email (POP3 - Receiving)
POP3_HOST=pop.gmail.com
POP3_PORT=995
POP3_USER=your_email@gmail.com
POP3_PASSWORD=your_app_specific_password

# WhatsApp (Optional)
WHATSAPP_API_KEY=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_VERIFY_TOKEN=nlpcrm_verify_token

# Flask (Optional)
FLASK_DEBUG=False
PORT=5000
```

---

## 🔐 Security Checklist

### Before Production Deployment

- [ ] Change default admin password
- [ ] Generate strong SECRET_KEY (32+ characters)
- [ ] Enable HTTPS/SSL
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use environment variables (never hardcode)
- [ ] Enable Flask-Talisman for security headers
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Review CORS settings
- [ ] Enable logging and monitoring
- [ ] Set up error tracking (Sentry, etc.)

---

## 📊 Database Setup

### Local SQLite (Default)
- Automatically creates `nlpcrm.db` in project root
- No additional configuration needed
- Good for development and small deployments

### SQLite Cloud (Recommended for Production)
1. Create account at https://sqlitecloud.io
2. Create a database cluster
3. Get connection URL
4. Set `SQLITE_CLOUD_URL` environment variable
5. Application will automatically use cloud database

---

## 🔗 Webhook Configuration

### WhatsApp Business API

1. **Meta Developer Console**
   - Go to https://developers.facebook.com
   - Create app → WhatsApp → Get Started

2. **Configure Webhook**
   - Callback URL: `https://your-domain.com/webhooks/whatsapp`
   - Verify Token: `nlpcrm_verify_token` (or your custom token)
   - Subscribe to: `messages`

3. **Get Credentials**
   - Phone Number ID
   - Access Token
   - Add to environment variables

### Microsoft Teams

1. **Create Bot**
   - Azure Portal → Bot Services
   - Create new bot registration

2. **Configure Webhook**
   - Messaging endpoint: `https://your-domain.com/webhooks/teams`

### Zoom

1. **Zoom Marketplace**
   - Create app → Webhook Only
   - Event notification endpoint: `https://your-domain.com/webhooks/zoom`

---

## 📧 Email Setup (Gmail)

### Enable POP3 Access

1. **Gmail Settings**
   - Settings → Forwarding and POP/IMAP
   - Enable POP for all mail
   - Enable IMAP

2. **App Password**
   - Google Account → Security
   - 2-Step Verification (must be enabled)
   - App passwords → Generate
   - Use this password in `SMTP_PASSWORD` and `POP3_PASSWORD`

---

## 🧪 Testing Deployment

```bash
# Health check
curl https://your-domain.com/

# Test login
curl -X POST https://your-domain.com/login \
  -d "email=admin@nlpcrm.com&password=your_password"

# Test API
curl https://your-domain.com/contacts
```

---

## 📈 Monitoring & Logs

### View Logs

**Heroku**:
```bash
heroku logs --tail
```

**Railway**:
```bash
railway logs
```

**AWS**:
```bash
eb logs
```

### Monitoring Tools

- **Sentry**: Error tracking
- **New Relic**: Performance monitoring
- **Datadog**: Infrastructure monitoring
- **LogDNA**: Log management

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart application
# (Platform-specific restart command)
```

### Database Migrations

Currently using automatic schema updates. For major changes:
1. Backup database
2. Deploy new version
3. Verify data integrity

---

## 🆘 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

**Database Connection Failed**
- Check SQLITE_CLOUD_URL format
- Verify network connectivity
- Falls back to local SQLite automatically

**Email Not Working**
- Verify SMTP/POP3 credentials
- Check if POP3 is enabled in Gmail
- Use app-specific password (not main password)

**AI Extraction Failing**
- Verify HF_API_KEY is valid
- Check HuggingFace API status
- Review API rate limits

---

## 📞 Support

For deployment issues:
- **Email**: amangurauli@gmail.com
- **GitHub Issues**: https://github.com/Amanvarma2231/NLPCRM/issues
- **LinkedIn**: [Aman Varma](https://www.linkedin.com/in/aman-v-697771345/)

---

**Last Updated**: January 2026  
**Version**: 3.1.0
