# 📚 Student Study Planner

A modern web-based application designed to help students organize their academic tasks, track deadlines, receive AI-powered study recommendations, and generate progress reports.

## ✨ Features

- **🔐 User Authentication**: Secure registration and login with password hashing
- **📝 Task Management**: Create, edit, delete, and track your study tasks
- **📋 Dashboard**: View all tasks with real-time statistics and completion tracking
- **🤖 AI Study Assistant**: Get personalized study plans and recommendations using AI
- **📄 PDF Reports**: Generate professional progress reports in PDF format
- **⚡ REST API**: Full API endpoints for task management
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **PDF Generation**: ReportLab
- **AI Integration**: Google Generative AI (Gemini)
- **Authentication**: Password hashing with PBKDF2

## 📋 Requirements

- Python 3.8+
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone or Extract the Project
```bash
cd student-study-planner
```

### 2. Create Virtual Environment (Recommended)
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Key (Optional - for AI Features)
Get a free Gemini API key from [Google AI Studio](https://ai.google.dev):

```bash
# On Windows
set GOOGLE_API_KEY="your-api-key"

# On macOS/Linux
export GOOGLE_API_KEY="your-api-key"
```

### 5. Run the Application
```bash
python app.py
```

The application will be available at: **http://localhost:5000**

### 6. Create Demo Account
- **Email**: demo@example.com
- **Password**: demo123

Or register a new account!

## 📁 Project Structure

```
student-study-planner/
├── app.py                 # Main Flask application
├── auth.py               # Authentication functions
├── database.py           # Database operations
├── ai.py                 # AI integration
├── report.py             # PDF report generation
├── requirements.txt      # Python dependencies
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── assistant.html
│   ├── 404.html
│   └── 500.html
│
├── static/              # Static files
│   ├── style.css        # Styling
│   └── script.js        # Client-side logic
│
└── reports/             # Generated PDF reports (created automatically)
```

## 🔌 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Tasks
- `GET /api/tasks` - Get all tasks for logged-in user
- `POST /api/tasks` - Create a new task
- `PUT /api/tasks/<id>` - Update task status
- `DELETE /api/tasks/<id>` - Delete a task

### AI Assistant
- `POST /api/ai/study-plan` - Get AI study recommendations

### Reports
- `GET /api/report/generate` - Generate PDF report
- `GET /reports/<filename>` - Download generated report

## 💾 Database Schema

### Users Table
```sql
id (INTEGER PRIMARY KEY)
name (TEXT)
email (TEXT UNIQUE)
password (TEXT HASHED)
created_at (TIMESTAMP)
```

### Tasks Table
```sql
id (INTEGER PRIMARY KEY)
user_id (INTEGER FOREIGN KEY)
title (TEXT)
description (TEXT)
deadline (TEXT)
status (TEXT: 'pending' or 'completed')
created_at (TIMESTAMP)
```

## 🤖 AI Features

The AI Study Assistant uses Google's Gemini API to provide personalized study recommendations:

- Create study schedules
- Prioritize tasks
- Suggest study techniques
- Answer study-related questions

**Note**: Requires GOOGLE_API_KEY environment variable to be set.

## 📊 Generate Reports

Click "Generate PDF Report" on the dashboard to create a professional PDF with:
- Student name and date
- Progress statistics
- Task summary
- Study recommendations

## 🔒 Security Features

- Password hashing using PBKDF2
- Session-based authentication
- CSRF protection via Flask
- SQL injection prevention with parameterized queries
- Secure password storage

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is already in use:
```bash
python app.py --port 5001
```

### Database Issues
To reset the database, simply delete `study_planner.db` file:
```bash
rm study_planner.db  # On Windows: del study_planner.db
```

The database will be recreated on next run.

### AI Features Not Working
Make sure:
1. `google-generativeai` is installed: `pip install google-generativeai`
2. GOOGLE_API_KEY environment variable is set
3. You have valid API key from [Google AI Studio](https://ai.google.dev)

## 📚 Learning Outcomes

This project demonstrates:
1. **REST API Development** - Full CRUD operations with Flask
2. **Database Management** - SQLite with proper schema design
3. **User Authentication** - Secure login/registration system
4. **PDF Generation** - Creating reports using ReportLab
5. **AI Integration** - Using external AI APIs in applications

## 📝 Capstone Concept Implementation

This project fulfills all 5 required capstone concepts:

| Concept | Implementation |
|---------|----------------|
| **API Endpoints** | `/register`, `/login`, `/tasks`, `/report` |
| **Database** | SQLite with users and tasks tables |
| **Authentication** | Secure registration + login + password hashing |
| **PDF Reporting** | Generate student progress reports |
| **LLM Integration** | AI-powered study assistant with Gemini API |

## 🚀 Deployment

### Render.com (Free)
1. Push to GitHub
2. Connect repository to Render
3. Set environment variable: GOOGLE_API_KEY
4. Deploy!

### Railway
1. Connect GitHub account
2. Select repository
3. Add environment variable
4. Deploy

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Author

Created as a capstone project demonstrating full-stack web development with Python and Flask.

---

**Happy Studying! 🎓**
