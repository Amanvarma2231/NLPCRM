# NLPCRM - Quick Command Reference

## 🚀 Starting the Application

### Option 1: Automated (Recommended)
```bash
run_app.bat
```

### Option 2: Manual
```bash
python run.py
```

### Option 3: With Virtual Environment
```bash
.venv\Scripts\activate
python run.py
```

## 🔧 Setup Commands

### First Time Setup
```bash
setup.bat
```

### Manual Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your credentials
```

## ✅ Verification

### Check System Status
```bash
python verify_system.py
```

### Check Python Version
```bash
python --version
```

### Check Installed Packages
```bash
pip list
```

## 🌐 Access Application

- **URL**: http://localhost:5000
- **Email**: admin@nlpcrm.com
- **Password**: admin@2026

## 📊 Database

### Local SQLite (Default)
- File: `nlpcrm.db`
- Automatic creation on first run

### SQLite Cloud (Optional)
- Set `SQLITE_CLOUD_URL` in `.env`
- Automatic fallback to local if cloud fails

## 🔑 Environment Variables

### Required
```env
SECRET_KEY=your_secret_key
HF_API_KEY=your_huggingface_key
ADMIN_EMAIL=admin@nlpcrm.com
ADMIN_PASSWORD=admin@2026
```

### Optional
```env
SQLITE_CLOUD_URL=your_cloud_url
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email
SMTP_PASSWORD=your_password
POP3_HOST=pop.gmail.com
POP3_USER=your_email
POP3_PASSWORD=your_password
WHATSAPP_API_KEY=your_key
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process
taskkill /PID <PID> /F
```

### Dependencies Issues
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### Database Issues
```bash
# Delete and recreate database
del nlpcrm.db
python run.py
```

### Clear Cache
```bash
# Delete Python cache
del /s /q __pycache__
del /s /q *.pyc
```

## 📝 Logs

### View Application Logs
```bash
type app.log
```

### Clear Logs
```bash
del app.log
```

## 🔄 Updates

### Pull Latest Changes
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## 🛑 Stop Application

- Press `Ctrl+C` in terminal
- Or close the command window

## 📞 Support

- **Email**: amangurauli@gmail.com
- **GitHub**: https://github.com/Amanvarma2231/NLPCRM
- **Issues**: https://github.com/Amanvarma2231/NLPCRM/issues

---

**NLPCRM v3.1** | © 2026 Aman Varma
