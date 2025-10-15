#!/usr/bin/env python
"""
Setup script for IT Support System
This script helps with initial setup and configuration
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_database():
    """Setup database and run migrations"""
    print("\n📊 Setting up database...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'it_support_system.settings')
    django.setup()
    
    # Run migrations
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed")
        return True
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def create_superuser():
    """Create a superuser account"""
    print("\n👤 Creating superuser account...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser'])
        print("✅ Superuser created successfully")
        return True
    except Exception as e:
        print(f"❌ Superuser creation failed: {e}")
        return False

def create_sample_data():
    """Create sample data for testing"""
    print("\n📝 Creating sample data...")
    try:
        execute_from_command_line(['manage.py', 'create_sample_data'])
        print("✅ Sample data created successfully")
        return True
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def collect_static_files():
    """Collect static files"""
    print("\n📁 Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully")
        return True
    except Exception as e:
        print(f"❌ Static files collection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 IT Support System Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("❌ Error: manage.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Setup database
    if not setup_database():
        print("❌ Database setup failed. Please check your database configuration.")
        sys.exit(1)
    
    # Collect static files
    collect_static_files()
    
    # Ask if user wants to create superuser
    create_super = input("\n❓ Do you want to create a superuser account? (y/n): ").lower().strip()
    if create_super in ['y', 'yes']:
        create_superuser()
    
    # Ask if user wants to create sample data
    create_sample = input("\n❓ Do you want to create sample data for testing? (y/n): ").lower().strip()
    if create_sample in ['y', 'yes']:
        create_sample_data()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update email settings in it_support_system/settings.py")
    print("2. Run the development server: python manage.py runserver")
    print("3. Open http://localhost:8000 in your browser")
    print("4. Login with your superuser account or create a new account")
    
    print("\n🔧 Configuration reminders:")
    print("- Update database credentials in settings.py")
    print("- Configure email settings for notifications")
    print("- Set DEBUG=False for production")
    print("- Configure static file serving for production")

if __name__ == '__main__':
    main()
