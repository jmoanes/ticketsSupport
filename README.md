# IT Support System

A comprehensive Django-based IT Support System with ticket management, user authentication, real-time chat, calendar integration, and analytics dashboard.

## 🚀 Features

### 👤 User Features
- **User Authentication**: Register, Login, Logout with Django Auth
- **Submit Support Tickets** with:
  - Auto-generated Ticket ID (e.g., JIAI-12345)
  - Title, Category, Description, Priority
  - Optional Attachments (screenshots, documents, etc.)
  - Optional Deadlines
- **View My Tickets** with filtering by status
- **Add Comments** to tickets for discussion
- **Dark Mode Toggle** with persistent user preference
- **Calendar View** showing ticket deadlines
- **Chat Room** for messaging with IT staff

### 🧑‍💼 IT Staff / Admin Features
- **View All Tickets** with advanced filtering and search
- **Update Ticket Status** and assign to staff members
- **Escalate Tickets** to other IT staff with email notifications
- **Manage Users** and roles through Django Admin
- **Analytics Dashboard** with comprehensive statistics
- **Calendar Overview** of all tickets and deadlines

### 🎨 UI/UX Features
- **Responsive Design** with Bootstrap 5
- **Dark Mode Support** with smooth transitions
- **Modern Interface** with clean, professional design
- **Real-time Chat** functionality
- **File Upload** with drag-and-drop support
- **Search and Filter** capabilities

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7 (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Database**: PostgreSQL
- **Template Engine**: Django Templates
- **Icons**: Bootstrap Icons

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package installer)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd it_support_system
```

### 2. Create Virtual Environment
```bash
python -m venv env
```

### 3. Activate Virtual Environment

**Windows:**
```bash
env\Scripts\activate
```

**macOS/Linux:**
```bash
source env/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Database Setup

#### Create PostgreSQL Database
```sql
CREATE DATABASE it_support_db;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE it_support_db TO postgres;
```

#### Update Database Settings
Edit `it_support_system/settings.py` and update the database configuration:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'it_support_db',
        'USER': 'postgres',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Collect Static Files
```bash
python manage.py collectstatic
```

### 9. Run Development Server
```bash
python manage.py runserver
```

## 📧 Email Configuration

To enable email notifications, update the email settings in `it_support_system/settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'IT Support <your-email@gmail.com>'
```

## 🎯 Usage

### 1. Access the System
- Open your browser and go to `http://localhost:8000`
- Register a new account or login with existing credentials

### 2. Create Your First Ticket
- Click "New Ticket" in the navigation
- Fill in the ticket details (title, description, category, priority)
- Optionally add attachments and set a deadline
- Submit the ticket

### 3. IT Staff Features
- Login as an IT staff member (set `is_it_staff=True` in user profile)
- View all tickets in the dashboard
- Update ticket status and assign to team members
- Escalate tickets when needed
- View analytics and performance metrics

### 4. Chat System
- Navigate to the Chat section
- Select a user to start chatting
- Send real-time messages

### 5. Calendar View
- View tickets organized by deadline
- Track upcoming deadlines and priorities

## 🗂️ Database Models

### UserProfile
- Extends Django's User model
- Fields: dark_mode, department, is_it_staff, phone_number

### Ticket
- Main ticket model with auto-generated ID (JIAI-XXXXX)
- Fields: title, description, category, priority, status, deadline
- Relationships: created_by, assigned_to, escalated_to

### Comment
- Ticket comments with internal/external visibility
- Fields: message, is_internal, author, created_at

### Attachment
- File attachments for tickets
- Fields: file, original_filename, file_size, uploaded_by

### ChatMessage
- Real-time chat messages
- Fields: sender, receiver, message, is_read, timestamp

## 🔐 Security Features

- CSRF protection on all forms
- User authentication and authorization
- Role-based access control (Users vs IT Staff)
- File upload validation and size limits
- SQL injection protection through Django ORM

## 🎨 Customization

### Dark Mode
- Toggle dark mode in user dropdown menu
- Preference is saved per user
- Smooth transitions between themes

### Styling
- Custom CSS in `static/css/style.css`
- Bootstrap 5 for responsive design
- Custom color scheme and animations

## 📱 Responsive Design

The system is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes

## 🚀 Deployment

### Production Settings
1. Set `DEBUG = False` in settings.py
2. Configure proper database credentials
3. Set up static file serving
4. Configure email settings
5. Use a production WSGI server (e.g., Gunicorn)

### Environment Variables
Consider using environment variables for sensitive settings:
```python
import os
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
DATABASE_URL = config('DATABASE_URL')
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create a ticket in the system
- Contact the IT support team
- Check the documentation

## 🔄 Version History

- **v1.0.0** - Initial release with core features
  - User authentication
  - Ticket management
  - Chat system
  - Analytics dashboard
  - Dark mode support

---

**Built with ❤️ using Django and Bootstrap**
