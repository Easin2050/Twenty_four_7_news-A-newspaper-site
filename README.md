# 🗞️ Twenty_Four_7 News API

A full-featured **news portal REST API** built with **Django REST Framework**, designed for digital journalism platforms.  
It provides **role-based access control**, **article publishing**, **ratings**, **email notifications**, and **secure authentication**.

---

## 🚀 Features

### 👤 User Management
- Register and log in using **email-based authentication**
- Role-based users:
  - **Admin** – full access to manage all resources
  - **Editor** – can create, update, and manage news articles
  - **Reader** – can browse and rate news articles
- Profile & image support (via `UserProfile` and `UserImage` models)

### 📰 News & Articles
- Editors can create, update, and delete news articles  
- Admin can manage all articles  
- Readers can view all published articles  

### ⭐ Ratings System
- Readers can rate articles only once  
- Editors receive an **email notification** when their article is rated  
- The rating user also gets a **thank-you email**

### 📧 Email Notifications
- Email verification
- Automatic notifications to editors and users

### 🔐 Authentication
- JWT-based authentication (via `djoser` or DRF auth)
- Only authenticated users can rate or update their profile

### 🧠 Developer-Friendly
- Beautiful, interactive **Swagger** and **Redoc** documentation
- Supports **DRF pagination**, **custom permissions**, and **custom serializers**
- Organized modular API structure

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Django, Django REST Framework |
| Database | PostgreSQL |
| Auth | JWT (via Djoser / DRF) |
| Docs | Swagger & Redoc |
| Env | Python|
| Others | Debug Toolbar, Custom Pagination, Custom Permissions |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/Twenty_Four_7_news.git
cd Twenty_Four_7_news
```
### 2️⃣ Create a virtual environment & activate it

python -m venv .news_env

## Linux / Mac
source .news_env/bin/activate
## Windows
.news_env\Scripts\activate

### 3️⃣ Install dependencies
pip install -r requirements.txt

### 4️ Create a .env file in the project root
SECRET_KEY=your-secret-key
* DEBUG=True

* DB_NAME=news_db
* DB_USER=postgres
* DB_PASSWORD=yourpassword
* DB_HOST=localhost
* DB_PORT=5432

* EMAIL_HOST=smtp.gmail.com
* EMAIL_USE_TLS=True
* EMAIL_PORT=587
* EMAIL_HOST_USER=your_email@gmail.com
* EMAIL_HOST_PASSWORD=your_app_password
* DEFAULT_FROM_EMAIL=your_email@gmail.com


### 5️⃣ Apply migrations

python manage.py migrate

### 6️⃣ Create a superuser

python manage.py createsuperuser

### 7️⃣ Run the server

python manage.py runserver

### 🧭 API Documentation

Swagger UI	http://127.0.0.1:8000/swagger/

Redoc	http://127.0.0.1:8000/redoc/

## 🧾 License

This project is licensed under the MIT License

## 🧑‍💻 Author

Md Easin
📧 easin562050@gmail.com

💻 GitHub: [@Easin2050](https://github.com/Easin2050)


