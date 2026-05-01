# 🎯 NLPCRM - Simple Step-by-Step Guide

## ✅ Step 1: Test Email Service

Open terminal aur run karo:

```bash
cd C:\Users\AMAN VARMA\OneDrive\Attachments\Desktop\NLPCRM
python test_email.py
```

**Kya hoga:**
- SMTP configuration check hoga
- SMTP connection test hoga
- POP3 configuration check hoga
- POP3 connection test hoga
- Recent emails fetch honge
- AI extraction demo hoga

**Agar test email bhejni hai:**
- Jab prompt aaye, apna email enter karo
- Ya Enter press karke skip karo

---

## ✅ Step 2: Start Application

Same terminal mein run karo:

```bash
python run.py
```

**Kya hoga:**
- Server start hoga
- Port 5000 pe run hoga
- Logs dikhenge

**Terminal ko band mat karo!** Server running rehna chahiye.

---

## ✅ Step 3: Open Browser

Naya browser tab kholo aur jao:

```
http://localhost:5000
```

---

## ✅ Step 4: Login

**Credentials:**
- Email: `admin@nlpcrm.com`
- Password: `admin@2026`

---

## ✅ Step 5: Test Features

### A) Dashboard
- Stats dekho (contacts, messages, sentiment)
- Recent contacts dekho
- Activity timeline dekho

### B) Email Integration Test
1. Settings pe jao
2. Email Integration section dekho
3. "Test Connection" button click karo
4. SMTP aur POP3 dono ka result dekho

### C) View Email Contacts
1. "Sources" menu pe jao
2. "Email" option select karo
3. Email se extracted contacts dekho

### D) Sync All
1. Dashboard pe wapas jao
2. "Sync All" button click karo
3. New contacts automatically add honge

### E) Contact Management
1. "Contacts" menu pe jao
2. All contacts list dekho
3. Export CSV try karo

### F) AI Engine
1. "AI Engine" menu pe jao
2. Sample text paste karo
3. "Extract Contact Info" click karo
4. AI extraction results dekho

---

## 🎥 Video Recording Ke Liye

### Loom Setup:
1. Loom download karo: https://www.loom.com/download
2. Install karo
3. Sign up/Login karo
4. "New Video" click karo
5. "Screen + Camera" ya "Screen Only" select karo

### Recording Steps:
1. **Start Recording**
2. **Terminal dikhao** aur `python test_email.py` run karo
3. **Results dikhao** - SMTP/POP3 tests
4. **Terminal mein** `python run.py` run karo
5. **Browser kholo** - http://localhost:5000
6. **Login karo** - admin@nlpcrm.com / admin@2026
7. **Dashboard tour** - stats, contacts, activity
8. **Settings** - Email integration test
9. **Sources → Email** - Extracted contacts
10. **Sync All** - Live sync demo
11. **Contacts** - Management features
12. **AI Engine** - Extraction demo
13. **Stop Recording**

### Video Mein Ye Batao:
- "Yeh NLPCRM hai - AI-powered CRM"
- "SMTP/POP3 use kar raha hai, OAuth nahi"
- "AI automatically emails se contacts extract karta hai"
- "Multi-channel support hai - Email, WhatsApp, Teams"
- "Real-time analytics aur sentiment analysis"

---

## 🛑 Stop Karne Ke Liye

Terminal mein press karo: **Ctrl + C**

---

## 📊 Expected Results

### Email Test:
```
[OK] SMTP connection OK
[OK] POP3 connection OK
[OK] Found X messages
[OK] Extraction complete
```

### Application:
```
Server running on http://localhost:5000
Access the application at: http://localhost:5000
```

### Browser:
- ✅ Login page loads
- ✅ Dashboard shows stats
- ✅ Email integration works
- ✅ Contacts visible
- ✅ AI extraction works
- ✅ Sync functionality works

---

## 🆘 Agar Problem Aaye

### Port busy hai:
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Email test fail:
1. Gmail settings check karo
2. POP3 enable karo
3. App password use karo (not main password)

### Server start nahi ho raha:
```bash
python test_app.py
```
Errors dekho aur fix karo

---

## ✅ Checklist

Before recording video:
- [ ] Email test pass ho gaya
- [ ] Application start ho gaya
- [ ] Browser mein login ho gaya
- [ ] Dashboard load ho gaya
- [ ] Email integration test pass
- [ ] Contacts visible hain
- [ ] Loom ready hai

---

**Ab bas in steps ko follow karo aur video record karo! 🎬**
