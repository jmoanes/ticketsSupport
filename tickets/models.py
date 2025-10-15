from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
import os


class UserProfile(models.Model):
    """
    Extended user profile with additional fields for IT support system
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    dark_mode = models.BooleanField(default=False, help_text="User's dark mode preference")
    department = models.CharField(max_length=100, blank=True, null=True, help_text="User's department")
    is_it_staff = models.BooleanField(default=False, help_text="Whether user is IT staff member")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.department or 'No Department'}"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class Ticket(models.Model):
    """
    Main ticket model for IT support requests
    """
    CATEGORY_CHOICES = [
        ('hardware', 'Hardware'),
        ('software', 'Software'),
        ('network', 'Network'),
        ('access', 'Access Issue'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
    ]

    # Auto-generated ticket ID (e.g., JIAI-12345)
    ticket_id = models.CharField(max_length=20, unique=True, blank=True, help_text="Auto-generated ticket ID")
    title = models.CharField(max_length=200, help_text="Brief description of the issue")
    description = models.TextField(help_text="Detailed description of the problem")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # User relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_tickets', help_text="IT staff member assigned to this ticket")
    escalated_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='escalated_tickets', help_text="User this ticket was escalated to")
    
    # Timestamps and deadlines
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField(null=True, blank=True, help_text="Optional deadline for ticket resolution")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When the ticket was resolved")

    def __str__(self):
        return f"{self.ticket_id} - {self.title}"

    def save(self, *args, **kwargs):
        """
        Auto-generate ticket ID if not provided
        """
        if not self.ticket_id:
            last_ticket = Ticket.objects.all().order_by('id').last()
            next_id = (last_ticket.id + 1) if last_ticket else 1
            self.ticket_id = f"JIAI-{next_id:05d}"
        
        # Set resolved_at when status changes to resolved
        if self.status == 'resolved' and not self.resolved_at:
            self.resolved_at = timezone.now()
        elif self.status != 'resolved':
            self.resolved_at = None
            
        super().save(*args, **kwargs)

    def escalate_ticket(self, new_user):
        """
        Escalate ticket to another user and send email notification
        """
        self.status = "escalated"
        self.escalated_to = new_user
        self.assigned_to = new_user
        self.save()
        
        # Primary escalation contact email
        primary_escalation_email = "johnjaymoanes009@gmail.com"
        
        # Prepare email content
        ticket_url = f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'}/tickets/{self.ticket_id}/"
        if not ticket_url.startswith('http'):
            ticket_url = f"http://{ticket_url}"
        
        email_subject = f"🚨 URGENT: Ticket {self.ticket_id} Escalated - {self.title}"
        email_message = f"""
        <html>
        <body>
            <h2>🚨 Ticket Escalation Alert</h2>
            
            <p><strong>The following ticket has been escalated and requires immediate attention:</strong></p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 15px 0;">
                <h3>Ticket Details:</h3>
                <ul>
                    <li><strong>Ticket ID:</strong> {self.ticket_id}</li>
                    <li><strong>Title:</strong> {self.title}</li>
                    <li><strong>Priority:</strong> <span style="color: #dc3545;">{self.get_priority_display()}</span></li>
                    <li><strong>Category:</strong> {self.get_category_display()}</li>
                    <li><strong>Status:</strong> <span style="color: #ffc107;">{self.get_status_display()}</span></li>
                    <li><strong>Created by:</strong> {self.created_by.get_full_name() or self.created_by.username}</li>
                    <li><strong>Assigned to:</strong> {new_user.get_full_name() or new_user.username}</li>
                    <li><strong>Created:</strong> {self.created_at.strftime('%Y-%m-%d %H:%M')}</li>
                </ul>
            </div>
            
            <div style="background-color: #e9ecef; padding: 15px; margin: 15px 0;">
                <h4>Description:</h4>
                <p>{self.description}</p>
            </div>
            
            <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                <h4>🔗 Quick Actions:</h4>
                <p>
                    <a href="{ticket_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Ticket Details
                    </a>
                </p>
                <p>
                    <a href="http://{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'}/dashboard/" 
                       style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Go to Dashboard
                    </a>
                </p>
            </div>
            
            <hr>
            <p><small>This is an automated notification from the IT Support System. Please do not reply to this email.</small></p>
            <p><small>If you have any questions, please contact the IT Support Team.</small></p>
        </body>
        </html>
        """
        
        # Send email to assigned user
        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[new_user.email],
                fail_silently=False,
                html_message=email_message,
            )
            print(f"Escalation email sent to {new_user.email}")
        except Exception as e:
            print(f"Failed to send escalation email to {new_user.email}: {e}")
        
        # Send email to primary escalation contact
        try:
            send_mail(
                subject=f"📧 COPY: {email_subject}",
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[primary_escalation_email],
                fail_silently=False,
                html_message=email_message,
            )
            print(f"Escalation notification sent to primary contact: {primary_escalation_email}")
        except Exception as e:
            print(f"Failed to send escalation email to primary contact {primary_escalation_email}: {e}")

    def get_priority_color(self):
        """
        Return CSS color class for priority level
        """
        colors = {
            'low': 'success',
            'medium': 'warning', 
            'high': 'danger',
            'urgent': 'dark'
        }
        return colors.get(self.priority, 'secondary')

    def get_status_color(self):
        """
        Return CSS color class for status
        """
        colors = {
            'open': 'primary',
            'in_progress': 'info',
            'resolved': 'success',
            'closed': 'secondary',
            'escalated': 'warning'
        }
        return colors.get(self.status, 'secondary')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"


class Comment(models.Model):
    """
    Comments on tickets for discussion and updates
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_comments')
    message = models.TextField(help_text="Comment message")
    is_internal = models.BooleanField(default=False, help_text="Internal comment visible only to IT staff")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.ticket.ticket_id}"

    class Meta:
        ordering = ['created_at']
        verbose_name = "Ticket Comment"
        verbose_name_plural = "Ticket Comments"


class Attachment(models.Model):
    """
    File attachments for tickets
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/%d/', help_text="Upload file attachment")
    original_filename = models.CharField(max_length=255, help_text="Original filename")
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_attachments')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.original_filename} - {self.ticket.ticket_id}"

    def save(self, *args, **kwargs):
        """
        Store original filename and file size
        """
        if self.file:
            self.original_filename = os.path.basename(self.file.name)
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def get_file_size_display(self):
        """
        Return human-readable file size
        """
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Ticket Attachment"
        verbose_name_plural = "Ticket Attachments"


class ChatMessage(models.Model):
    """
    Chat messages between users and staff
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(help_text="Chat message content")
    is_read = models.BooleanField(default=False, help_text="Whether message has been read")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"


class TicketNotification(models.Model):
    """
    Track email notifications sent for tickets
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ticket_notifications')
    notification_type = models.CharField(max_length=50, help_text="Type of notification (status_change, escalation, etc.)")
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.ticket.ticket_id} to {self.user.username}"

    class Meta:
        ordering = ['-sent_at']
        verbose_name = "Ticket Notification"
        verbose_name_plural = "Ticket Notifications"
