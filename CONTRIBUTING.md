# Contributing to NLPCRM

Thank you for your interest in contributing to NLPCRM! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- Git
- Virtual environment tool (venv)

### Setup Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/Amanvarma2231/NLPCRM.git
   cd NLPCRM
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   copy .env.example .env
   # Edit .env with your credentials
   ```

## 📋 Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused

### Commit Messages
Use conventional commit format:
```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example:
```
feat(nlp): add sentiment analysis for email extraction

Implemented advanced sentiment detection using Qwen 2.5 model
to better categorize incoming leads.

Closes #123
```

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

## 🧪 Testing

Before submitting a PR:
1. Test all modified functionality
2. Ensure no existing features are broken
3. Test on both local SQLite and SQLite Cloud (if available)

## 📝 Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clean, documented code
   - Follow the style guidelines
   - Test thoroughly

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

4. **Push to Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Provide clear description
   - Reference related issues
   - Add screenshots if UI changes

## 🐛 Reporting Bugs

When reporting bugs, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version)
- Error logs/screenshots

## 💡 Feature Requests

For feature requests:
- Describe the feature clearly
- Explain the use case
- Provide examples if possible

## 📞 Contact

- **Developer**: Aman Varma
- **Email**: amangurauli@gmail.com
- **LinkedIn**: [Aman Varma](https://www.linkedin.com/in/aman-v-697771345/)
- **GitHub**: [@Amanvarma2231](https://github.com/Amanvarma2231)

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to NLPCRM! 🎉
