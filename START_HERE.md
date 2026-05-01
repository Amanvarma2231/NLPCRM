# NLPCRM - Quick Start Guide

## ✅ System Status: READY

All tests passed! Your NLPCRM installation is working perfectly.

## 🚀 Start Application

### Method 1: Simple Start (Recommended)
```bash
python run.py
```

### Method 2: With Verification
```bash
python test_app.py
python run.py
```

### Method 3: Automated Script
```bash
run_app.bat
```

## 🌐 Access Application

Once started, open your browser:

- **URL**: http://localhost:5000
- **Email**: admin@nlpcrm.com
- **Password**: admin@2026

## ✅ System Verification Results

```
[OK] Python 3.13.3
[OK] All dependencies installed
[OK] Environment configured
[OK] Database connected (Local SQLite)
[OK] AI service initialized
[OK] Email service configured
[OK] All routes registered (31 total)
```

## 📊 Features Available

### ✅ Working Features:
- ✅ User Authentication (Login/Logout)
- ✅ Dashboard with Analytics
- ✅ Contact Management (Add/Edit/Delete/Export)
- ✅ AI-Powered Lead Extraction (Qwen 2.5)
- ✅ Email Integration (SMTP/POP3)
- ✅ WhatsApp Integration
- ✅ Sentiment Analysis
- ✅ Lead Scoring
- ✅ Smart Deduplication
- ✅ Activity Tracking
- ✅ Multi-source Sync
- ✅ CSV Export
- ✅ AI Chat Analyst
- ✅ Webhook Support (WhatsApp, Teams, Zoom)

### 📧 Email Configuration:
- SMTP: Configured (amangurauli@gmail.com)
- POP3: Configured (amangurauli@gmail.com)
- Status: Ready to send/receive

### 🤖 AI Configuration:
- Model: Qwen/Qwen2.5-7B-Instruct
- API: HuggingFace
- Status: Active

### 💾 Database:
- Type: SQLite (Local)
- File: nlpcrm.db
- Status: Connected
- Note: SQLite Cloud fallback active

## 🔧 Troubleshooting

### If Port 5000 is Busy:
```bash
# Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### If Dependencies Missing:
```bash
pip install -r requirements.txt
```

### If Database Issues:
```bash
# Delete and recreate
del nlpcrm.db
python run.py
```

## 📝 Environment Variables

All required variables are configured in `.env`:

```
✅ SECRET_KEY
✅ HF_API_KEY
✅ ADMIN_EMAIL
✅ ADMIN_PASSWORD
✅ SMTP_HOST/PORT/USER/PASSWORD
✅ POP3_HOST/PORT/USER/PASSWORD
✅ WHATSAPP_API_KEY
✅ SQLITE_CLOUD_URL
```

## 🎯 Next Steps

1. **Start the application**: `python run.py`
2. **Open browser**: http://localhost:5000
3. **Login**: admin@nlpcrm.com / admin@2026
4. **Explore features**: Dashboard, Contacts, AI Engine
5. **Test email**: Settings > Email Integration
6. **Sync data**: Dashboard > Sync All

## 📞 Support

- **Email**: amangurauli@gmail.com
- **GitHub**: https://github.com/Amanvarma2231/NLPCRM
- **Documentation**: See COMMANDS.md, API.md, DEPLOYMENT.md

---

**NLPCRM v3.1** | © 2026 Aman Varma | MIT License

**Status**: ✅ Production Ready
