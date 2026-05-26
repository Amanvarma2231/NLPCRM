
# 🚀 NLPCRM: Next-Gen AI-Powered Customer Intelligence

<div align="center">

![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-production-success.svg)

### *Transforming unstructured conversations into actionable neural intelligence.*

[Features](#-premium-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Demo](#-demo) • [Support](#-support)

</div>

---

## 📖 Overview

**NLPCRM** is a state-of-the-art Customer Relationship Management system designed for the enterprise era. It leverages high-performance **Natural Language Processing (NLP)** to ingest, analyze, and structure communication from every major channel—turning raw text into precise business signals.

### Why NLPCRM?

- 🎯 **AI-First Design**: Built around Qwen 2.5 for intelligent lead extraction
- 🔄 **Multi-Channel Sync**: WhatsApp, Gmail, Teams, and more
- 📊 **Smart Analytics**: Real-time sentiment analysis and lead scoring
- 🎨 **Modern UI**: Stunning Neural Indigo design with glassmorphism
- 📱 **PWA Ready**: Install as native app on any device
- 🔐 **Enterprise Security**: CSRF protection, secure sessions, encrypted data

---

## 💎 Premium Features

### 🧠 Neural Lead Extraction
- **AI-Powered Engine**: Powered by **Qwen 2.5** for high-accuracy entity extraction (Name, Email, Company, Intent)
- **Multichannel Ingestion**: Seamlessly sync signals from **WhatsApp Business**, **Gmail**, and **Microsoft Teams**
- **Auto-Triage**: Intelligent lead scoring and importance categorization based on neural sentiment analysis
- **Smart Deduplication**: Automatically merges duplicate contacts with intelligent data merging

### 🎨 Stunning "Neural Indigo" UI
- **Premium Hybrid Design**: A sleek dark-mode aesthetic with high-contrast Action Tokens (Neon Lime & Deep Indigo)
- **Frosted Glassmorphism**: High-end visual depth with real-time blur and sophisticated micro-animations
- **Intelligence Drawer**: Slide-out neural profiles for deep-diving into individual lead signals without losing context
- **Responsive Design**: Perfect experience on desktop, tablet, and mobile

### 📱 Enterprise Mobility (PWA)
- **Installable Desktop/Mobile**: Full Progressive Web App support—install NLPCRM as a native application via Chrome or Safari
- **Offline Reliability**: Service Worker integration for high-speed local caching and reliable access
- **Push Notifications**: Stay updated with real-time alerts (coming soon)

### 🤖 CRM Chat Analyst
- **Interactive AI Assistant**: Query your customer database using natural language (e.g., *"Find me high-interest leads from TechCorp"*)
- **Real-time Analytics**: Ask the AI for complex data summaries and trend analysis
- **Context-Aware**: Understands your CRM data and provides intelligent insights

### 📧 Email Integration
- **SMTP Support**: Send emails directly from NLPCRM
- **POP3 Inbox**: Automatically fetch and analyze incoming emails
- **Smart Extraction**: AI extracts contact info from email conversations
- **Gmail Ready**: Works seamlessly with Gmail and other providers

### 📊 Advanced Analytics
- **Sentiment Analysis**: Track positive, negative, and neutral interactions
- **Lead Scoring**: AI-powered importance scoring (0-10 scale)
- **Priority Tracking**: High, Medium, Low urgency classification
- **Source Attribution**: Track which channels generate the best leads
- **Activity Timeline**: Complete audit log of all interactions

---

## 🏗️ Enterprise Architecture

- **Backend**: Python 3.9+ / Flask Enterprise
- **Database**: Hybrid SQLite Cloud with Local Fallback (High Availability)
- **Intelligence**: Hugging Face Inference API (Qwen 2.5 Architecture)
- **Security**: Google OAuth 2.0 / Talisman (Security Headers) / ProxyFix (CSRF Ready)

---

## 🛠️ Quick Start

### Manual Setup

#### 1. Clone Repository
```bash
git clone https://github.com/Amanvarma2231/NLPCRM.git
cd NLPCRM
```

#### 2. Create Virtual Environment
```powershell
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
# Copy example environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your credentials
```

**Required Environment Variables**:
```env
# Core Configuration
SECRET_KEY=your_secure_random_key_here
ADMIN_EMAIL=admin@nlpcrm.com
ADMIN_PASSWORD=admin@2026

# AI/NLP
HF_API_KEY=your_huggingface_api_key
HF_MODEL=Qwen/Qwen2.5-7B-Instruct

# Database (Optional - uses local SQLite if not set)
SQLITE_CLOUD_URL=sqlitecloud://your-cluster.sqlite.cloud:8860/db?apikey=your-key

# Email Integration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
POP3_HOST=pop.gmail.com
POP3_PORT=995
POP3_USER=your_email@gmail.com
POP3_PASSWORD=your_app_password

# WhatsApp (Optional)
WHATSAPP_API_KEY=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

#### 5. Launch Application
```bash
python run.py
```

#### 6. Access Application
```
URL: http://localhost:5000
Email: admin@nlpcrm.com
Password: admin@2026
```

---

## 📚 Documentation

- **[API Documentation](API.md)** - Complete API reference
- **[Deployment Guide](DEPLOYMENT.md)** - Deploy to Heroku, Railway, AWS, etc.
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Security Policy](SECURITY.md)** - Security guidelines and reporting
- **[Changelog](CHANGELOG.md)** - Version history and updates

---

## 🎬 Demo

### Screenshots

**Dashboard**
![Dashboard](https://via.placeholder.com/800x400/1e293b/ccff00?text=Neural+Dashboard)

**Contact Management**
![Contacts](https://via.placeholder.com/800x400/1e293b/6366f1?text=Smart+Contact+Management)

**AI Chat Analyst**
![AI Chat](https://via.placeholder.com/800x400/1e293b/22c55e?text=AI+Powered+Insights)

### Live Demo

Coming soon! 🚀

---

## ✨ Key Highlights

- ✅ **Production Ready**: Battle-tested with enterprise-grade security
- ✅ **Cloud Native**: Deploy anywhere - Heroku, AWS, Railway, Render
- ✅ **AI-Powered**: Qwen 2.5 for intelligent lead extraction
- ✅ **Multi-Channel**: WhatsApp, Email, Teams integration
- ✅ **Smart Deduplication**: Never lose data with intelligent merging
- ✅ **Real-time Analytics**: Live sentiment and priority tracking
- ✅ **PWA Support**: Install as native app on any device
- ✅ **Open Source**: MIT License - use freely

---

## 🛣️ Roadmap

### Version 3.2 (Q2 2026)
- [ ] Multi-user support with RBAC
- [ ] Advanced reporting dashboard
- [ ] Email campaign management
- [ ] Calendar integration
- [ ] Slack integration

### Version 4.0 (Q4 2026)
- [ ] Mobile app (React Native)
- [ ] Custom AI model fine-tuning
- [ ] Multi-tenant architecture
- [ ] Advanced workflow automation
- [ ] Marketplace for integrations

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Steps

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 🐛 Issues & Support

- **Bug Reports**: [GitHub Issues](https://github.com/Amanvarma2231/NLPCRM/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/Amanvarma2231/NLPCRM/discussions)
- **Email Support**: amangurauli@gmail.com

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🧑‍💻 Lead Developer

<div align="center">

**Aman Varma**  
*Full Stack Developer & AI Specialist*

[![Email](https://img.shields.io/badge/Email-amangurauli%40gmail.com-red?style=for-the-badge&logo=gmail)](mailto:amangurauli@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Aman%20Varma-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/aman-v-697771345/)
[![GitHub](https://img.shields.io/badge/GitHub-%40Amanvarma2231-black?style=for-the-badge&logo=github)](https://github.com/Amanvarma2231)

</div>

---

<div align="center">

### ⭐ If you find NLPCRM useful, please give it a star!

**Built with ❤️ for Enterprise Intelligence and UI Excellence**

NLPCRM v3.1 • © 2026 Aman Varma • MIT License

</div>
