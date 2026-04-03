# 🚀 AI Notes Backend API

A production-ready backend built using **FastAPI**, **MongoDB**, and **OpenAI**, featuring JWT authentication, note management, search functionality, and AI-powered summarization.

---

## 📌 Features

* 🔐 User Authentication (JWT)
* 📝 Create, Read, Update, Delete Notes
* 🔍 Search Notes by Query
* 🤖 AI-powered Note Summarization
* 🗄️ MongoDB Database Integration
* 🌐 Deployed REST API

---

## 🛠️ Tech Stack

* **Backend:** FastAPI
* **Database:** MongoDB
* **Authentication:** JWT (python-jose)
* **AI Integration:** OpenAI API
* **Deployment:** Render

---

## ⚙️ How to Run the Project Locally

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/notes_manager.git
cd notes_manager
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Mac/Linux
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create a `.env` file in the root folder:

```env
OPENAI_API_KEY=your_openai_api_key
MONGO_URI=your_mongodb_connection_string
```

---

### 5️⃣ Run the Server

```bash
uvicorn main:app --reload
```

---

### 6️⃣ Open API Docs

```text
http://127.0.0.1:8000/docs
```

---

## 🌐 Deployed API

```text
https://your-app-name.onrender.com
```

Swagger UI:

```text
https://your-app-name.onrender.com/docs
```

---

## 📡 API Endpoints

### 🔐 Authentication

| Method | Endpoint  | Description             |
| ------ | --------- | ----------------------- |
| POST   | `/signup` | Register new user       |
| POST   | `/login`  | Login and get JWT token |

---

### 📝 Notes

| Method | Endpoint           | Description    |
| ------ | ------------------ | -------------- |
| POST   | `/notes`           | Create a note  |
| GET    | `/notes`           | Get all notes  |
| GET    | `/notes?query=...` | Search notes   |
| GET    | `/notes/{note_id}` | Get note by ID |
| PUT    | `/notes/{note_id}` | Update note    |
| DELETE | `/notes/{note_id}` | Delete note    |

---

### 🤖 AI Feature

| Method | Endpoint                   | Description         |
| ------ | -------------------------- | ------------------- |
| POST   | `/notes/{note_id}/summary` | Generate AI summary |

---

## 🔐 Authentication Usage

1. Login using `/login`
2. Copy the access token
3. Click **Authorize** in Swagger UI
4. Enter:

```
Bearer <your_token>
```

---

## 🤖 Notes on AI Usage

* The application uses **OpenAI GPT model (`gpt-4o-mini`)** for summarizing notes.
* AI generates concise summaries (2–3 lines) from note content.
* Summaries are **cached in the database** to reduce repeated API calls.
* If the OpenAI API fails, a fallback summary is generated using basic text truncation.

---

## ⚠️ Important Notes

* `.env` file is used locally, but in deployment (Render), environment variables must be added manually.
* MongoDB Atlas must allow access (`0.0.0.0/0` IP whitelist).
* JWT tokens are required for all protected routes.

---

## 🚀 Future Improvements

* Refresh Tokens
* Pagination
* Tagging System
* Role-Based Access Control
* Frontend Integration (React)

---

## 👨‍💻 Author

**Ajay Chakraborty**

---

## Link for opening the backend :

https://notes-manager-1-kagv.onrender.com/docs


## ⭐ If you like this project

Give it a ⭐ on GitHub!
