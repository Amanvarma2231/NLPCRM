# 🔧 Gmail POP3 Setup Guide

## ❌ Problem: POP3 Access Disabled

Gmail mein POP3 by default disabled hota hai. Enable karna padega.

---

## ✅ Solution: Enable POP3 in Gmail

### Step 1: Gmail Settings Open Karo

1. Gmail kholo: https://mail.google.com
2. Login karo (amangurauli@gmail.com)
3. Top-right corner mein **Settings (⚙️)** icon click karo
4. **"See all settings"** click karo

---

### Step 2: Forwarding and POP/IMAP Tab

1. **"Forwarding and POP/IMAP"** tab pe jao
2. **"POP Download"** section dekho

---

### Step 3: Enable POP

**Option 1 (Recommended):**
- Select: **"Enable POP for all mail"**

**Option 2:**
- Select: **"Enable POP for mail that arrives from now on"**

**When messages are accessed with POP:**
- Select: **"Keep Gmail's copy in the Inbox"**

---

### Step 4: Enable IMAP (Optional but Recommended)

1. Same page pe neeche **"IMAP Access"** section hai
2. Select: **"Enable IMAP"**

---

### Step 5: Save Changes

1. Neeche scroll karo
2. **"Save Changes"** button click karo

---

### Step 6: Verify App Password

Gmail 2-Step Verification ke saath App Password use karna padta hai.

**Check if you have App Password:**
1. Google Account kholo: https://myaccount.google.com
2. **Security** section pe jao
3. **"2-Step Verification"** dekho
4. Agar enabled hai, toh **"App passwords"** option milega

**Current App Password in .env:**
```
SMTP_PASSWORD=ohmpmddxlqlahmno
POP3_PASSWORD=ohmpmddxlqlahmno
```

Yeh valid hai ya nahi check karo.

---

## 🔄 Alternative: Use IMAP Instead of POP3

Agar POP3 enable nahi ho raha, toh IMAP use kar sakte hain.

### Update .env file:

```env
# Replace POP3 with IMAP
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USER=amangurauli@gmail.com
IMAP_PASSWORD=ohmpmddxlqlahmno
```

---

## 🧪 Test Again

POP3 enable karne ke baad:

```bash
cd C:\Users\AMAN VARMA\OneDrive\Attachments\Desktop\NLPCRM
python test_email.py
```

---

## 📸 Screenshots Guide

### Gmail Settings:
```
Settings (⚙️) → See all settings → Forwarding and POP/IMAP

POP Download:
○ Disable POP
● Enable POP for all mail
○ Enable POP for mail that arrives from now on

When messages are accessed with POP:
● Keep Gmail's copy in the Inbox

IMAP Access:
● Enable IMAP
```

---

## 🆘 Still Not Working?

### Option 1: Use IMAP (Better Alternative)
Main IMAP support add kar dunga - yeh zyada reliable hai

### Option 2: Check App Password
Naya App Password generate karo:
1. https://myaccount.google.com/security
2. 2-Step Verification → App passwords
3. Generate new password
4. Update in .env file

### Option 3: Less Secure Apps (Not Recommended)
Gmail ne yeh option remove kar diya hai, isliye App Password use karo

---

## ✅ Next Steps

1. **Gmail mein POP3 enable karo** (steps above)
2. **Test karo**: `python test_email.py`
3. **Agar fail ho**, toh batao - main IMAP support add kar dunga

**Abhi Gmail settings mein jao aur POP3 enable karo! 🚀**
