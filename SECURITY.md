# Security Policy

## 📅 Supported Versions

| Version | Supported |
|---------|-----------|
| Latest  | ✅        |

We support the latest pushed version of this repository. Users are encouraged to always use the latest commit to avoid any known vulnerabilities.

---

## 📣 Reporting a Vulnerability

If you discover a security vulnerability in this project (such as an exposed API key, insecure file access, or unsafe command execution), please follow these steps:

1. **Do not create a public issue or pull request.**
2. Email the maintainer **Titash Majumder** privately at:  
   📧 `majumdertitash@gmail.com`
3. Include:
   - Description of the vulnerability
   - Steps to reproduce (if applicable)
   - Any proof of concept or log output

---

## 🔐 Token & Secret Disclosure

If an API key or token is accidentally committed and detected (e.g., Hugging Face, OpenAI), it will be **immediately revoked and rotated**.

If you find any exposed secrets that are still valid, please notify the maintainer immediately.

---

## ✅ Security Best Practices Followed

- `.env` is excluded via `.gitignore`
- Sensitive data is not logged or shared
- Tokens are scoped with minimum permissions
- GitHub secret scanning is monitored and enforced

---

Thank you for helping keep this project secure! 🙏
