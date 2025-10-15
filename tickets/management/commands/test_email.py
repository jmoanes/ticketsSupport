from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email configuration for escalation notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            default='johnjaymoanes009@gmail.com',
            help='Email address to send test email to',
        )

    def handle(self, *args, **options):
        test_email = options['email']
        
        self.stdout.write('Testing email configuration...')
        
        try:
            # Test email content
            subject = "🧪 IT Support System - Email Test"
            message = """
            <html>
            <body>
                <h2>🧪 Email Configuration Test</h2>
                <p>This is a test email to verify that the IT Support System email configuration is working correctly.</p>
                
                <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                    <h4>✅ Email Settings:</h4>
                    <ul>
                        <li><strong>SMTP Host:</strong> {}</li>
                        <li><strong>Port:</strong> {}</li>
                        <li><strong>TLS:</strong> {}</li>
                        <li><strong>From Email:</strong> {}</li>
                    </ul>
                </div>
                
                <p>If you received this email, the escalation notification system is ready to use!</p>
                
                <hr>
                <p><small>This is a test email from the IT Support System.</small></p>
            </body>
            </html>
            """.format(
                settings.EMAIL_HOST,
                settings.EMAIL_PORT,
                settings.EMAIL_USE_TLS,
                settings.DEFAULT_FROM_EMAIL
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[test_email],
                fail_silently=False,
                html_message=message,
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Test email sent successfully to {test_email}!'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'Email configuration is working correctly!'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Failed to send test email: {e}'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    'Please check your email configuration in settings.py'
                )
            )
