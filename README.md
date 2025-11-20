# Smart Task Manager

A comprehensive task management and project tracking system built with Django and modern web technologies.

## 🎯 Overview

Smart Task Manager is a full-stack web application designed to help teams efficiently manage projects, tasks, and team collaboration. It features role-based access control, real-time notifications, advanced analytics, and seamless team communication.

## ✨ Core Features

### 🔐 Authentication & Authorization
- Email-based authentication with JWT tokens
- Role-based access control (RBAC) with 6 roles
- Remember me functionality
- Password reset with OTP
- Secure session management

### 📊 Project Management
- Create, update, and manage projects
- Team member assignment
- Project status tracking
- Real-time collaboration

### ✅ Task Management
- Advanced task creation and editing
- Task prioritization and status tracking
- Task dependencies and recurring tasks
- Attachment support
- Task comments and discussions
- Pagination and advanced filtering

### 👥 Team Collaboration
- Direct messaging between team members
- Real-time notifications
- Activity tracking and audit logs
- Team management dashboard

### 📈 Analytics & Reporting
- Productivity metrics
- Performance indicators
- Time tracking
- Custom reports with export (CSV/JSON)
- Data caching for performance

### 🛡️ Security
- CSRF protection
- SQL injection prevention
- Password hashing with Django's secure algorithms
- Role-based permissions
- Request validation and sanitization

## 🏗️ Architecture

### Backend Stack
- **Framework**: Django 5.2.7
- **API**: Django REST Framework
- **Authentication**: Simple JWT
- **Database**: SQLite (development), PostgreSQL ready
- **Caching**: Django cache framework

### Frontend Stack
- **Languages**: HTML5, CSS3, JavaScript
- **Styling**: Dark theme with modern animations
- **API Communication**: Fetch API
- **Real-time Updates**: Auto-refresh mechanisms

## 📁 Project Structure

```
smart_task_manager/
├── manage.py                    # Django management script
├── db.sqlite3                   # SQLite database
├── requirements.txt             # Python dependencies
│
├── smart_task_manager/          # Main project settings
│   ├── settings.py              # Configuration
│   ├── urls.py                  # URL routing
│   ├── html_views.py            # Template views
│   └── wsgi.py                  # WSGI configuration
│
├── users/                       # User management app
│   ├── models.py                # CustomUser, UserProfile
│   ├── views.py                 # Auth endpoints
│   ├── serializers.py           # Data serialization
│   ├── permissions.py           # RBAC permissions
│   └── urls.py                  # User URLs
│
├── tasks/                       # Task management app
│   ├── models.py                # Task, Comment, Attachment
│   ├── views.py                 # Task API endpoints
│   ├── serializers.py           # Task serialization
│   └── urls.py                  # Task URLs
│
├── projects/                    # Project management app
│   ├── models.py                # Project model
│   ├── views.py                 # Project API endpoints
│   ├── serializers.py           # Project serialization
│   └── urls.py                  # Project URLs
│
├── analytics/                   # Analytics & reporting
│   ├── models.py                # Analytics models
│   ├── views.py                 # Analytics endpoints
│   ├── reports_generator.py     # Report generation
│   └── reports_export.py        # Export functionality
│
├── chat/                        # Team messaging
│   ├── models.py                # ChatRoom, ChatMessage
│   ├── views.py                 # Chat endpoints
│   ├── consumers.py             # WebSocket consumers
│   └── routing.py               # WebSocket routing
│
├── notifications/              # Real-time notifications
│   ├── models.py                # Notification model
│   ├── views.py                 # Notification endpoints
│   └── utils.py                 # Notification utilities
│
├── frontend/                    # Frontend application
│   ├── templates/               # HTML templates
│   ├── static/                  # CSS, JS, assets
│   ├── views.py                 # Template rendering
│   └── urls.py                  # Frontend URLs
│
└── templates/                   # Base templates

```

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip or poetry
- Virtual environment

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd smart_task_manager
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Run development server**
```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

## 🔐 User Roles

1. **Admin** - Full system access and administration
2. **Manager** - Project and team management
3. **Developer** - Task development and execution
4. **Designer** - Design-related tasks
5. **Analyst** - Data analysis and reporting
6. **Client** - Read-only access to assigned projects

## 📚 API Endpoints

### Authentication
- `POST /api/users/register/` - User registration
- `POST /api/users/login/` - User login
- `POST /api/users/logout/` - User logout
- `POST /api/users/token/refresh/` - Refresh JWT token

### Users
- `GET /api/users/profile/` - Get user profile
- `PUT /api/users/profile/` - Update user profile
- `POST /api/users/change-password/` - Change password

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Get project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Analytics
- `GET /api/analytics/productivity-report/` - Get productivity report
- `GET /api/analytics/export-csv/` - Export as CSV
- `GET /api/analytics/export-json/` - Export as JSON

## 🔧 Configuration

### Environment Variables
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Settings
- `settings.py` - Main Django configuration
- `ALLOWED_HOSTS` - Configured from environment variables
- `JWT_AUTH` - Token expiration and refresh settings

## 📊 Key Features in Detail

### Pagination
- Tasks: 20 items per page
- Projects: 10 items per page
- Configurable via query parameters

### Search & Filtering
- Full-text search on tasks and projects
- Filter by status, priority, assigned user
- Order by creation date, due date, or priority

### Caching
- 5-minute cache for analytics reports
- In-memory caching for performance optimization
- Redis-ready for production scaling

### Error Handling
- Comprehensive validation
- User-friendly error messages
- Proper HTTP status codes
- Exception logging

## 🧪 Testing

Run tests with:
```bash
python manage.py test
```

## 📝 Database Models

### CustomUser
Email-based authentication with extended user fields.

### UserProfile
Role and permission management for RBAC.

### Task
Task management with dependencies, recurrence, and attachments.

### Project
Project grouping and team member management.

### ChatRoom & ChatMessage
Team messaging and communication.

### AnalyticsReport
Analytics data aggregation and reporting.

## 🔒 Security Measures

- Password hashing with PBKDF2
- CSRF token validation
- SQL injection prevention
- XSS protection
- Rate limiting on authentication endpoints
- Secure session management
- Role-based access control
- Permission-based API access

## 📦 Dependencies

Key packages:
- Django 5.2.7
- djangorestframework
- simple-jwt
- django-cors-headers
- python-dotenv

See `requirements.txt` for complete list.

## 🤝 Contributing

This is a closed project. For issues or suggestions, please contact the development team.

## 📄 License

Proprietary - All rights reserved

## 📧 Support

For support, contact: support@smarttaskmanager.com

---

**Built with ❤️ by the Smart Task Manager Team**

