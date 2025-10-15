# Configuration Guide

This guide helps you configure the IT Support System for your environment.

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database Settings
DB_NAME=it_support_db
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=IT Support <your-email@gmail.com>
```

## Database Configuration

### PostgreSQL Setup

1. Install PostgreSQL on your system
2. Create a database:
   ```sql
   CREATE DATABASE it_support_db;
   CREATE USER postgres WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE it_support_db TO postgres;
   ```

3. Update `it_support_system/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'it_support_db',
           'USER': 'postgres',
           'PASSWORD': 'password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

## Email Configuration

### Gmail Setup

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. Update settings.py with your credentials

### Other Email Providers

Update the EMAIL_* settings in `settings.py` for your provider:

```python
# For Outlook/Hotmail
EMAIL_HOST = 'smtp-mail.outlook.com'
EMAIL_PORT = 587

# For Yahoo
EMAIL_HOST = 'smtp.mail.yahoo.com'
EMAIL_PORT = 587

# For custom SMTP
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
```

## Security Configuration

### Production Settings

For production deployment, update these settings:

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Use environment variables for sensitive data
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASE_PASSWORD = os.environ.get('DB_PASSWORD')
```

### HTTPS Configuration

```python
# Force HTTPS in production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

## Static Files Configuration

### Development
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

### Production
```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## File Upload Configuration

### File Size Limits
```python
# In settings.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
```

### Allowed File Types
Update the `AttachmentForm` in `tickets/forms.py` to modify allowed file types.

## Logging Configuration

Add to `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Performance Optimization

### Database Optimization
```python
# Use connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'it_support_db',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 60,
    }
}
```

### Caching
```python
# Redis cache (install django-redis)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Monitoring and Analytics

### Error Tracking
Add Sentry for error tracking:

```python
# Install: pip install sentry-sdk
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

## Backup Configuration

### Database Backup
Create a backup script:

```bash
#!/bin/bash
# backup.sh
pg_dump -h localhost -U postgres it_support_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Media Files Backup
```bash
#!/bin/bash
# backup_media.sh
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify credentials in settings.py
   - Ensure database exists

2. **Email Not Sending**
   - Check email credentials
   - Verify SMTP settings
   - Check firewall/network restrictions

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check STATIC_URL and STATIC_ROOT settings
   - Verify web server configuration

4. **File Upload Issues**
   - Check file size limits
   - Verify MEDIA_ROOT permissions
   - Check allowed file types

### Debug Mode

Enable debug mode for development:
```python
DEBUG = True
```

Add debug toolbar for development:
```python
# Install: pip install django-debug-toolbar
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    # ...
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']
```

## Support

For additional help:
- Check the README.md file
- Review Django documentation
- Create an issue in the project repository
