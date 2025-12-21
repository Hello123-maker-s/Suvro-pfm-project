# 💰 Personal Finance Manager (PFM)

A full-stack **Django-based Personal Finance Manager** that helps users track income, expenses, budgets, savings, investments, and receive intelligent insights using Machine Learning.

This project is developed as part of the **Master of Computer Applications (MCA)** curriculum.

---

## 🚀 Features

### 🔐 User Management
- User registration & login
- Secure authentication
- Password reset via email
- User-specific financial data

### 💸 Income & Expense Tracking
- Add, edit, delete income/expense entries
- Categorize incomes/expenses
- CSV upload support for transactions
- Monthly and yearly summaries

### 📊 Budget Management
- Create category-wise budgets
- Real-time budget usage tracking
- Automatic alerts when budget exceeds limits

### 🏦 Savings & Investments
- Track savings goals
- Investment portfolio tracking
- Estimated returns & performance overview

### 📈 Reports & Dashboard
- Interactive dashboard
- Monthly expense breakdown
- Category-wise spending analysis
- Visual charts and summaries

### 🤖 AI / ML Income/Expense Classifier
- Automatically categorizes incomes & expenses using NLP
- Uses sentence embeddings + logistic regression
- Improves categorization accuracy for unstructured transaction descriptions

> ⚠️ Note: ML module may be conditionally disabled on free-tier deployments due to memory constraints.

### 📧 Email Notifications
- Password reset emails
- Budget limit alerts
- SMTP-based email system (Gmail supported)

---

## 🛠️ Tech Stack

### Backend
- **Python 3**
- **Django**
- **Gunicorn**

### Frontend
- Django Templates
- HTML, CSS, JavaScript
- Bootstrap

### Database
- **PostgreSQL**
- Neon / Railway / Local PostgreSQL supported

### Machine Learning
- scikit-learn
- SentenceTransformers
- pandas, numpy
- joblib

### Deployment
- Railway / Hugging Face Spaces / PythonAnywhere
- Neon (PostgreSQL)
- Whitenoise (static files)

---

## 🗂️ Project Structure

personalfinancemanager/
│
├── accounts/ # User authentication
├── finance/ # Core finance logic
├── budget/ # Budget management
├── savings/ # Savings module
├── investment/ # Investment tracking
├── ml/ # Machine Learning module
├── core/ # Dashboard & utilities
│
├── templates/ # HTML templates
├── static/ # Static assets
├── manage.py
└── requirements.txt
