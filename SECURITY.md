# Security Policy

## Supported Versions

Currently supported versions of NLPCRM:

| Version | Supported          |
| ------- | ------------------ |
| 3.1.x   | :white_check_mark: |
| 3.0.x   | :x:                |
| < 3.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in NLPCRM, please follow these steps:

### 1. **Do Not** Publicly Disclose

Please do not create a public GitHub issue for security vulnerabilities.

### 2. Report Privately

Send an email to: **amangurauli@gmail.com**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### 3. Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 1-3 days
  - High: 1-2 weeks
  - Medium: 2-4 weeks
  - Low: Next release cycle

### 4. Disclosure Policy

- We will acknowledge your report within 48 hours
- We will provide regular updates on the fix progress
- Once fixed, we will publicly disclose the vulnerability with credit to you (if desired)
- We request 90 days before public disclosure to allow users to update

## Security Best Practices

### For Users

1. **Environment Variables**
   - Never commit `.env` file to version control
   - Use strong, unique SECRET_KEY
   - Rotate API keys regularly

2. **Database Security**
   - Use SQLite Cloud with proper authentication
   - Regular backups
   - Restrict database access

3. **API Keys**
   - Keep HuggingFace API keys secure
   - Use environment variables, not hardcoded values
   - Monitor API usage for anomalies

4. **Email Credentials**
   - Use app-specific passwords (not main password)
   - Enable 2FA on email accounts
   - Regularly review connected apps

5. **Production Deployment**
   - Use HTTPS only
   - Enable Flask-Talisman in production
   - Set secure session cookies
   - Use strong admin passwords

### For Developers

1. **Code Review**
   - All PRs require review
   - Security-focused code review for auth/data handling
   - Use static analysis tools

2. **Dependencies**
   - Keep dependencies updated
   - Monitor for security advisories
   - Use `pip-audit` for vulnerability scanning

3. **Input Validation**
   - Validate all user inputs
   - Sanitize data before database operations
   - Use parameterized queries

4. **Authentication**
   - Implement rate limiting
   - Use secure session management
   - Protect against CSRF attacks

## Known Security Considerations

### Current Implementation

1. **Authentication**: Simple email/password (admin only)
   - Future: Multi-user with OAuth2
   
2. **CSRF Protection**: Enabled via Flask-WTF
   - Webhooks are exempted (as required)

3. **Session Security**: HTTPOnly cookies with SameSite=Lax
   - Future: Add secure flag for HTTPS

4. **API Rate Limiting**: Basic rate limiting via Flask-Limiter
   - Future: Advanced rate limiting per user

## Security Features

### Implemented

- ✅ CSRF Protection (Flask-WTF)
- ✅ Secure Session Cookies
- ✅ Input Validation
- ✅ SQL Injection Prevention (Parameterized Queries)
- ✅ XSS Prevention (Template Auto-escaping)
- ✅ Environment Variable Protection
- ✅ Error Handling (No sensitive data in errors)

### Planned

- 🔄 Two-Factor Authentication (2FA)
- 🔄 OAuth2 Integration
- 🔄 Role-Based Access Control (RBAC)
- 🔄 Audit Logging
- 🔄 API Key Management
- 🔄 Advanced Rate Limiting

## Contact

For security concerns, contact:
- **Email**: amangurauli@gmail.com
- **LinkedIn**: [Aman Varma](https://www.linkedin.com/in/aman-v-697771345/)

---

**Thank you for helping keep NLPCRM secure!** 🔒
