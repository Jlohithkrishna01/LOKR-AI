
# LOKR AI — Intelligent AI Chatbot

<p align="center">
  <strong>LOKR AI</strong><br/>
  An Intelligent AI-Powered Chatbot Platform
</p>

<p align="center">
  <b>Founder & CEO: Jangiti Lohithkrishna</b>
</p>

<p align="center">
  A modern AI chatbot featuring intelligent conversations,
  real-time web search, document intelligence, user authentication,
  and personalized settings.
</p>

---

## 🌟 About LOKR AI

LOKR AI is an AI-powered chatbot web application inspired by modern conversational AI platforms.

It provides users with an intelligent conversational experience through AI-powered responses, real-time web search, document analysis, conversation history, and personalized account settings.

The platform combines a React frontend with a Python FastAPI backend and MySQL database.

## ✨ Key Features

### 1. 🔐 Authentication System
- User registration and login.
- Email validation.
- Secure password hashing using bcrypt.
- JWT-based authentication.
- Remember Me session support.
- Forgot and reset password functionality.
- Protected application routes.

### 2. 💬 Intelligent Chat Experience
- Personalized welcome screen.
- AI-powered conversations.
- Real-time response streaming using SSE.
- Multi-turn conversational context.
- Stop AI response generation.
- Markdown response rendering.
- Syntax-highlighted code blocks.
- Copy and regenerate responses.
- Like and dislike feedback.

### 3. 🌐 Real-Time Web Search
- Automatic detection of search-related questions.
- Live web search integration using DuckDuckGo.
- AI-generated search summaries.
- Clickable source cards.
- Website links and source citations.
- MySQL-based source persistence.

### 4. 📄 File Upload & Document Intelligence
- PDF file support.
- DOCX document support.
- TXT, CSV, Markdown and JSON support.
- Image uploads.
- PDF text extraction using PyPDF.
- Word document extraction using Python-Docx.
- Document summarization and question answering.

### 5. 🗂️ Conversation Management
- Conversation history.
- Search conversations.
- Automatic chat title generation.
- Rename conversations.
- Delete conversations.
- New chat functionality.
- Time-based chat organization.

### 6. 👤 User Profile & Settings
- User profile management.
- Profile picture upload.
- Avatar cropping.
- Change password.
- Light mode.
- Dark mode.
- System theme.
- Chat preferences.
- Privacy settings.
- Account deletion.

### 7. 📱 Responsive Interface
- Modern user interface.
- Responsive design.
- Collapsible sidebar.
- Mobile-friendly navigation.
- Custom LOKR AI branding.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 19, TypeScript, Vite |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| Database | MySQL 8.0 |
| Authentication | JWT, Bcrypt |
| AI Integration | Groq Cloud API |
| Web Search | DuckDuckGo (DDGS) |
| Streaming | Server-Sent Events (SSE) |
| Document Processing | PyPDF, Python-Docx |
| Image Processing | Pillow |
| API Server | Uvicorn |
| ORM | SQLAlchemy |

---

## 📂 Project Structure

```text
LOKR-AI/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── database/
│   │   ├── middleware/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── tests/
│   ├── uploads/
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── context/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── index.css
│   │
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── .env.example
│
├── .gitignore
├── README.md
└── start-all.bat
```

---

## 🚀 Installation & Setup

### 1. Prerequisites

Install the following software:

- Python 3.10 or above.
- Node.js 18 or above.
- npm.
- MySQL Server 8.0 or above.
- Git.

### 2. Clone the Repository

```bash
git clone https://github.com/Jlohithkrishna01/LOKR-AI.git
```

Open the project:

```bash
cd LOKR-AI
```

### 3. Database Setup

Open MySQL and execute:

```sql
CREATE DATABASE lokr_ai
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Use the database name in your backend configuration.

### 4. Backend Setup

Open PowerShell:

```powershell
cd backend
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure your backend `.env` file using `.env.example`.

Start the backend:

```powershell
python run.py
```

Backend URL:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Frontend Setup

Open another terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Configure frontend environment variables using `.env.example`.

Start the frontend:

```powershell
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

## 🔑 Environment Variables

Never upload real API keys, passwords, or secrets to GitHub.

### Backend Environment

Create `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@127.0.0.1:3306/lokr_ai?charset=utf8mb4

GROQ_API_KEY=your_groq_api_key

GROQ_DEFAULT_MODEL=qwen/qwen3.8-27b

GROQ_FALLBACK_MODEL=openai/gpt-oss-120b

JWT_SECRET=replace_with_a_secure_random_secret
```

### Frontend Environment

Create `frontend/.env`:

```env
VITE_API_URL=/api
```

Use the actual configuration required by your application.

---

## 🧪 Testing

The project includes backend test files covering areas such as:

- Authentication and user functionality.
- Date and time handling.
- Greeting functionality.
- Web search.
- Search resilience.
- Grounding and response quality.
- Cinema-related queries.

Run the tests from the backend directory:

```powershell
python -m pytest
```

---

## 🔒 Security

- Password hashing with bcrypt.
- JWT-based authentication.
- Protected API routes.
- Environment-based configuration.
- Never expose private API keys.
- Do not commit `.env` files.
- Validate user inputs.

---

## 🌍 Repository

**GitHub Repository:**

https://github.com/Jlohithkrishna01/LOKR-AI

**Project:** LOKR AI

**Founder & CEO:** Jangiti Lohithkrishna

---

## 🎯 Vision

LOKR AI aims to build an intelligent AI platform that makes AI technology more accessible, useful, and powerful for students, developers, businesses, and everyday users.

---

<p align="center">
  <strong>LOKR AI</strong>
  <br/>
  Built with innovation and intelligence.
  <br/><br/>
  © 2026 LOKR AI. All Rights Reserved.
</p>
