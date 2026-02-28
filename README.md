# 🎓 University Welfare System API

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-green)
![Supabase](https://img.shields.io/badge/Database-Supabase-3ECF8E)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-yellow)
![OpenAPI](https://img.shields.io/badge/OpenAPI-3.1-blue)
![Maintained](https://img.shields.io/badge/Maintained-Yes-brightgreen)

A **modern backend API for managing university welfare systems**, built with **FastAPI** and **Supabase**.
This system helps universities manage **student welfare services, job opportunities, vendor approvals, price management, and course enrollments**.

---

# 🚀 Features

✅ Student welfare service APIs

✅ Vendor management and price approval workflow

✅ Job search and job applications

✅ Course enrollment system

✅ Security verification endpoints

✅ Approval workflow system

✅ Admin reports generation

✅ Supabase cloud database integration

✅ Fully documented API using **Swagger (OpenAPI)**

---

# 🧠 System Architecture

Client Applications interact with the FastAPI backend, which communicates with Supabase for data storage and retrieval.

```
Client / Browser / Mobile App
            │
            ▼
        FastAPI Server
            │
            ▼
      Supabase Database
```

---

# 📂 Project Structure

```
student_welfare/
│
├── routers/              # API route modules
│
├── app.py                # Application configuration
├── main.py               # Main FastAPI application
├── database.py           # Supabase database connection
│
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables (not uploaded)
│
└── venv/                 # Virtual environment (ignored)
```

---

# ⚙️ Installation Guide

## 1️⃣ Clone the Repository

```
git clone https://github.com/shivam-9s/student-welfare-api.git
cd student-welfare-api
```

---

## 2️⃣ Create Virtual Environment

```
python -m venv venv
```

Activate environment:

### Windows

```
venv\Scripts\activate
```

### Mac / Linux

```
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

## 4️⃣ Setup Environment Variables

Create a `.env` file in the project root.

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_api_key
```

You can get these values from:

```
Supabase Dashboard → Settings → API
```

---

## ▶️ Run the Server

```
uvicorn main:app --reload
```

Server will start at:

```
http://127.0.0.1:8000
```

---

# 📑 API Documentation

FastAPI automatically provides **interactive API documentation**.

### Swagger UI

```
http://127.0.0.1:8000/docs
```

### ReDoc

```
http://127.0.0.1:8000/redoc
```

---

# 🔌 Available API Endpoints

## Root

| Method | Endpoint | Description      |
| ------ | -------- | ---------------- |
| GET    | `/`      | API health check |

---

## 💡 Idea Management

| Method | Endpoint        | Description     |
| ------ | --------------- | --------------- |
| POST   | `/ideas/submit` | Submit new idea |

---

## 💰 Vendor Price Management

| Method | Endpoint                         | Description                 |
| ------ | -------------------------------- | --------------------------- |
| PUT    | `/vendors/update-price`          | Propose vendor price change |
| POST   | `/admin/approve-price/{item_id}` | Admin approves price        |

---

## 📝 Approval Workflow

| Method | Endpoint                               | Description            |
| ------ | -------------------------------------- | ---------------------- |
| POST   | `/approvals/move-to-next/{request_id}` | Process approval stage |

---

## 🔍 Search Services

| Method | Endpoint          | Description           |
| ------ | ----------------- | --------------------- |
| GET    | `/search/vendors` | Search vendors        |
| GET    | `/search/jobs`    | Search available jobs |

---

## 💼 Job Services

| Method | Endpoint      | Description   |
| ------ | ------------- | ------------- |
| POST   | `/jobs/apply` | Apply for job |

---

## 🎓 Course Enrollment

| Method | Endpoint          | Description        |
| ------ | ----------------- | ------------------ |
| POST   | `/courses/enroll` | Enroll in a course |

---

## 🔐 Security Verification

| Method | Endpoint                        | Description         |
| ------ | ------------------------------- | ------------------- |
| GET    | `/security/verify`              | Verify permissions  |
| GET    | `/security/verify-vendor-staff` | Verify vendor staff |

---

## 📊 Admin Reports

| Method | Endpoint                     | Description                  |
| ------ | ---------------------------- | ---------------------------- |
| GET    | `/admin/registration-report` | Generate registration report |

---

# 🧪 Example API Response

```
{
  "status": "University Welfare API is Online"
}
```

---

# 🛠 Technologies Used

| Technology   | Purpose               |
| ------------ | --------------------- |
| **FastAPI**  | Backend API framework |
| **Supabase** | Cloud database        |
| **Python**   | Programming language  |
| **Uvicorn**  | ASGI server           |
| **OpenAPI**  | API documentation     |

---

# 📈 Future Improvements

* Student authentication system
* AI-based welfare recommendation engine
* Admin dashboard
* Notification system
* Mobile application integration
* Analytics for welfare usage

---

# 🤝 Contributing

Contributions are welcome!

Steps:

```
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request
```

---

# 📜 License

This project is licensed under the **MIT License**.

---

# 👨‍💻 Author

**Shivam Kumar**

GitHub:
https://github.com/shivam-9s

---

⭐ If you like this project, consider giving it a **star on GitHub!**
