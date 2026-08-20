# My 10x Solution: Student Study Planner

**Author**: Asma Hussain — 2026-08-20

**Project Name**: Student Study Planner  
**Date**: 2024  
**Technologies**: Python, Flask, SQLite, HTML/CSS, ReportLab, Google Generative AI

---

## 1. Problem

University students struggle to:
- Organize multiple assignments across different courses
- Prioritize which tasks to complete first
- Track progress towards their academic goals
- Manage deadlines effectively
- Receive personalized study guidance

This lack of organization leads to missed deadlines, procrastination, and academic stress.

---

## 2. Solution

**Student Study Planner** is a web-based task management application designed specifically for students. It enables learners to:

- Create an account and securely manage their academic tasks
- Add assignments with deadlines and descriptions
- Track task completion status in real-time
- Ask an AI study assistant for personalized recommendations
- Generate PDF progress reports to monitor improvement

The application is simple, intuitive, and focuses on solving a real problem students face daily.

---

## 3. Target Users

- University and college students
- High school students managing multiple projects
- Graduate students coordinating complex assignments
- Anyone needing AI-powered study assistance

---

## 4. Key Features

### ✅ Registration & Login
- Secure user account creation
- Password hashing using PBKDF2
- Session-based authentication
- Logout functionality

### ✅ Task Management
- Add new tasks with title, description, and deadline
- Mark tasks as completed or pending
- Delete tasks no longer needed
- View all tasks with filtering by status
- Real-time progress statistics

### ✅ Dashboard
- Visual statistics (total, completed, pending tasks, completion rate)
- Task list with deadline highlighting
- Quick actions for task management
- Professional UI with Bootstrap

### ✅ AI Study Assistant
- Chat interface with AI
- Get personalized study plans
- Ask about exam preparation
- Receive prioritization recommendations
- Powered by Google Gemini API

### ✅ PDF Reports
- Generate professional progress reports
- Includes student name, date, and statistics
- Shows task summary and upcoming assignments
- Download as PDF for sharing or printing

---

## 5. Technologies Used

### Backend
- **Python** - Programming language
- **Flask** - Web framework for building the API
- **SQLite** - Lightweight database

### Frontend
- **HTML5** - Markup
- **CSS3** - Styling with Bootstrap 5
- **JavaScript** - Client-side interactivity

### Additional Libraries
- **ReportLab** - PDF generation
- **Google Generative AI** - LLM integration
- **Werkzeug** - Security utilities

---

## 6. Program Concepts Implemented

### 1. ✅ API Endpoints
Implemented RESTful API with the following endpoints:

```
GET    /api/tasks              - Retrieve all tasks
POST   /api/tasks              - Create new task
PUT    /api/tasks/<id>         - Update task status
DELETE /api/tasks/<id>         - Delete task
POST   /api/ai/study-plan      - AI recommendations
GET    /api/report/generate    - Generate PDF report
```

### 2. ✅ Database Management
SQLite database with two main tables:

**Users Table**
- id, name, email, password (hashed), created_at

**Tasks Table**
- id, user_id, title, description, deadline, status, created_at

Includes:
- Foreign key relationships
- Proper data types and constraints
- Efficient queries with indexing

### 3. ✅ User Authentication
- Secure registration with email validation
- Login with credential verification
- Password hashing using PBKDF2 algorithm
- Session management
- Logout functionality
- Protected routes requiring authentication

### 4. ✅ PDF Reporting
ReportLab-based report generation featuring:
- Professional formatting with headers and tables
- Student progress statistics
- Task summaries
- Study recommendations
- Download capability

### 5. ✅ LLM Integration
Google Generative AI (Gemini) integration providing:
- AI-powered study recommendations
- Contextual responses based on student tasks
- Personalized study planning
- Real-time assistance

---

## 7. Project Architecture

```
                    ┌─────────────────┐
                    │   User Requests  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Flask App      │
                    │  (app.py)        │
                    └────────┬─────────┘
                    ┌────────┴──────────────┬──────────┐
                    │                       │          │
          ┌─────────▼──────┐   ┌───────────▼───┐  ┌──▼─────────┐
          │  SQLite Database│   │ AI Integration│  │PDF Generator│
          │  (database.py)  │   │  (ai.py)      │  │(report.py)  │
          └─────────────────┘   └───────────────┘  └──────────────┘
                    │                        │
          ┌─────────▼──────────────────────────────────┐
          │      Static Files & Templates             │
          │  (HTML, CSS, JavaScript)                  │
          └──────────────────────────────────────────┘
```

---

## 8. How It Satisfies the 5 Concepts

| Required Concept | Implementation |
|---|---|
| **API Endpoints** | 7 REST endpoints for full CRUD operations on tasks, authentication, and report generation |
| **Database** | SQLite with users and tasks tables, proper schema and relationships |
| **Authentication** | Secure registration, login, password hashing, session management |
| **PDF Reporting** | ReportLab implementation generating professional progress reports with statistics |
| **LLM Integration** | Google Generative AI integration for personalized study recommendations |

---

## 9. Setup Instructions

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set API Key (Optional but Recommended)
```bash
export GOOGLE_API_KEY="your-api-key-here"
```

### Run Application
```bash
python app.py
```

### Access Application
Open browser and go to: `http://localhost:5000`

---

## 10. Future Enhancements

- **Collaboration Features**: Share tasks with classmates
- **Calendar Integration**: Sync with Google Calendar
- **Mobile App**: Native iOS/Android applications
- **Advanced Analytics**: Detailed performance tracking
- **Study Groups**: Find and join study groups
- **Exam Preparation**: AI-powered exam prep modules
- **Notifications**: Email/SMS task reminders

---

## 11. Conclusion

Student Study Planner demonstrates a complete full-stack web application that:

✅ Solves a real student problem  
✅ Implements all 5 required capstone concepts  
✅ Uses modern web technologies  
✅ Follows best practices in security and database design  
✅ Provides professional UI/UX  
✅ Integrates cutting-edge AI technology  
✅ Includes comprehensive documentation  

This project is production-ready and can be deployed to platforms like Render.com or Railway with minimal configuration.

---

**Project Status**: ✅ Complete and Ready for Evaluation

**GitHub Repository**: https://github.com/asmahussain48/student-study-planner.git

**Live Demo**: [Link to deployed application if available]
