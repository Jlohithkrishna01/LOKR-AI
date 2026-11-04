# LOKR AI — Production-Grade Intelligent AI Chatbot

**LOKR AI** is a modern, production-style AI chatbot web application inspired by the usability of ChatGPT, featuring original branding, real-time web search capabilities, document intelligence, multi-turn conversational context, user authentication, profile customization, and theme toggling.

---

## 🌟 Key Features

### 1. 🔐 Complete Authentication System
* **Sign Up**: Full name, email validation, strong password requirements (8+ characters, letters and numbers), duplicate email protection, and bcrypt hashing.
* **Sign In**: Email and password authentication with "Remember Me" session support and JWT access tokens.
* **Forgot & Reset Password**: Secure token-based password reset workflow with expiration and direct reset links.
* **Protected Routes**: Instant session verification and automatic redirects for unauthorized users.

### 2. 💬 ChatGPT-Like Conversational Experience
* **Welcome Screen**: Dynamic personalized greetings (`Good morning, [User] 👋`) and 5 one-click suggestion cards:
  * *Explain a concept*
  * *Write code*
  * *Analyze a document*
  * *Search the web*
  * *Help with a project*
* **Real-Time Streaming**: Smooth Server-Sent Events (SSE) token streaming with a typing cursor.
* **Multi-turn Context**: Full conversation memory across successive turns within each chat.
* **Stop Generation**: Immediate stream abortion button to stop AI generation on command.
* **Markdown & Syntax Highlighting**: Rich rendering with headings, bullet points, numbered lists, tables, inline code, and syntax-highlighted code blocks with language badges and one-click copy buttons.
* **Response Actions**: One-click Copy response, Regenerate response, and Like/Dislike feedback toggles.

### 3. 🌐 Real-Time Web Search & Source Citations
* **Automatic Detection**: Intelligently identifies questions requiring live, real-time information (e.g., current news, leaders, weather, stock prices, 2025/2026 events).
* **Live Search Synthesis**: Fetches verified web results via DuckDuckGo and weaves live facts into the AI response.
* **Visual Source Cards**: Displays clickable source badges with website names, article titles, URLs, and summaries.
* **Database Citations**: Sources are persisted in MySQL linked to the corresponding AI message.

### 4. 📄 File Upload & Document Intelligence
* **Multi-format Support**: Upload `.pdf`, `.docx`, `.txt`, `.csv`, `.md`, `.json`, and images.
* **Document Extraction**: Automatic text extraction from PDFs (`pypdf`) and Word documents (`python-docx`).
* **Document QA**: Ask questions like *"Summarize this document"*, *"Extract key points"*, or *"Analyze this resume"*.
* **File Attachment Chips**: Displays attached files with file-type icons, size indicators, and removal options.

### 5. 🗂️ Conversation History & Search
* **Time-Grouped History**: Sidebar chats neatly organized into:
  * **Today**
  * **Yesterday**
  * **Previous 7 Days**
  * **Older**
* **Instant Search**: Search through conversation titles and message content in real time.
* **Management**: Inline conversation renaming and deletion with confirmation.
* **New Chat**: Starts clean conversations while keeping all past conversations safely stored in MySQL.

### 6. 👤 User Profile & Settings
* **User Profile Modal**: View account creation date, total conversations count, total messages sent, and bio.
* **Avatar Upload**: Upload profile pictures with automated square cropping and thumbnail generation.
* **Change Password**: Change passwords securely inside the account dashboard.
* **Settings Modal**:
  * *Appearance*: Light Mode, Dark Mode, and System Theme.
  * *Chat Preferences*: Enter to Send toggle, message timestamps toggle, and default AI model selector.
  * *Privacy*: Clear all chat history and permanent account deletion.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, React Markdown, Remark GFM, Prism Syntax Highlighter |
| **Backend** | Python 3.13, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2, PyJWT, Bcrypt, HTTPX, PyPDF, Python-Docx, Pillow |
| **Database** | MySQL 8.0 (`successfully` database) |
| **AI Engine** | Groq Cloud API (`qwen/qwen3.8-27b`, `openai/gpt-oss-120b`) |
| **Web Search** | DuckDuckGo Real-Time Search API (`ddgs`) |

---

## 📂 Project Structure

```text
D:\ai app\
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py          # Signup, Login, Forgot & Reset Password, Me
│   │   │   ├── users.py         # Profile, Avatar upload, Change password
│   │   │   ├── chats.py         # Conversations CRUD, History search
│   │   │   ├── ai.py            # Real-time SSE streaming, Web search injection
│   │   │   ├── files.py         # File uploads and document extraction
│   │   │   └── settings.py      # User settings and account deletion
│   │   ├── database/
│   │   │   ├── base.py          # Declarative Base
│   │   │   └── session.py       # SQLAlchemy engine & SessionLocal
│   │   ├── models/              # User, UserSettings, Conversation, Message, Source
│   │   ├── schemas/             # Pydantic v2 validation models
│   │   ├── services/
│   │   │   ├── ai_service.py    # AIService abstraction for Groq / OpenAI
│   │   │   ├── web_search.py    # DDGS search & query intent detector
│   │   │   ├── file_service.py  # PDF, Word, text extraction & avatar cropping
│   │   │   └── security.py      # Bcrypt hashing & JWT utilities
│   │   ├── middleware/
│   │   │   └── auth_deps.py     # JWT token verification dependency
│   │   ├── config.py            # Pydantic settings & environment configuration
│   │   └── main.py              # FastAPI application & CORS configuration
│   ├── uploads/                 # Storage for user avatars and uploaded documents
│   ├── requirements.txt
│   ├── run.py
│   ├── .env
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/            # ChatArea, ChatInput, MessageItem, CodeBlock, SourceCard, WelcomeScreen
│   │   │   ├── common/          # Logo, Avatar, ThemeToggle, Modal
│   │   │   ├── layout/          # Sidebar, Topbar
│   │   │   ├── profile/         # ProfileModal, ChangePasswordModal
│   │   │   └── settings/        # SettingsModal
│   │   ├── context/             # AuthContext, ChatContext, ThemeContext
│   │   ├── pages/               # LoginPage, SignupPage, ForgotPasswordPage, ResetPasswordPage, ChatPage
│   │   ├── services/            # api.ts (HTTP client & SSE stream reader)
│   │   ├── types/               # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.ts
│   ├── .env
│   └── .env.example
│
└── README.md
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* **Node.js** v18+ (tested with Node v24)
* **Python** 3.10+ (tested with Python 3.13)
* **MySQL Server** 8.0+ running on port `3306`

### 2. Database Setup
Create the database in MySQL (if not already existing):
```sql
CREATE DATABASE successfully CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Backend Setup & Run
Open a terminal in `D:\ai app\backend`:
```powershell
# 1. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# 2. Verify dependencies (already installed)
pip install -r requirements.txt

# 3. Start the FastAPI server
python run.py
```
> The backend server will start on **`http://127.0.0.1:8000`** with interactive API docs at **`http://127.0.0.1:8000/docs`**.

### 4. Frontend Setup & Run
Open a new terminal in `D:\ai app\frontend`:
```powershell
# 1. Install dependencies (already installed)
npm install

# 2. Start the Vite development server
npm run dev
```
> The frontend application will start on **`http://127.0.0.1:5173`**.

---

## 🔒 Environment Variables

### Backend (`backend/.env`)
```env
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/successfully?charset=utf8mb4
GROQ_API_KEY=your_groq_api_key_here
GROQ_DEFAULT_MODEL=qwen/qwen3.8-27b
GROQ_FALLBACK_MODEL=openai/gpt-oss-120b
JWT_SECRET=your_jwt_secret_key_change_in_production
```

### Frontend (`frontend/.env`)
```env
VITE_API_URL=/api
```

---

## 🚀 GitHub Pages & Deployment

### Automated GitHub Pages Deployment
A GitHub Actions workflow is provided at `.github/workflows/deploy-pages.yml` that automatically builds and deploys the frontend whenever changes are pushed to `main`.

To enable GitHub Pages in your repository:
1. Go to your GitHub repository: [Jlohithkrishna01/Ai_App](https://github.com/Jlohithkrishna01/Ai_App)
2. Click **Settings** > **Pages** (under the "Code and automation" section).
3. Under **Build and deployment** > **Source**, select **GitHub Actions**.
4. Once selected, pushing to `main` will automatically trigger the deployment workflow, and your frontend will be live at:
   `https://jlohithkrishna01.github.io/Ai_App/`

> **Note**: GitHub Pages hosts the static frontend application. To connect the live frontend to your backend API, deploy the FastAPI backend to a cloud host (such as Render, Railway, or Fly.io) and configure `VITE_API_URL` to point to your live backend endpoint.

---

## 🧪 Testing Checklist Completed
- [x] User Signup with validation and password hashing
- [x] User Login with JWT generation and persistence
- [x] Forgot Password request & token generation
- [x] Password Reset & confirmation screen
- [x] New Chat creation and auto-title generation
- [x] SSE Real-time streaming with typing animations
- [x] Multi-turn conversational memory
- [x] Stop Generation button functionality
- [x] Real-time Web Search intent detection
- [x] DuckDuckGo live search with source cards
- [x] Source links and citations saved to MySQL
- [x] File upload and text extraction (PDF, Word, TXT, CSV, Images)
- [x] Chat history grouped by Today, Yesterday, Previous 7 Days, Older
- [x] Chat history search across conversation titles and messages
- [x] Conversation inline rename and delete
- [x] User Profile modal and avatar upload with 256x256 cropping
- [x] Change password modal
- [x] Settings modal (Account, Appearance, Chat, Privacy)
- [x] Clear all conversations & Delete account
- [x] Light, Dark, and System theme toggling with localStorage persistence
- [x] Responsive layout with collapsible sidebar and mobile drawer
