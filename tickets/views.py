from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from datetime import datetime, timedelta
import json
import os

from .models import UserProfile, Ticket, Comment, Attachment, ChatMessage, TicketNotification
from .forms import TicketForm, CommentForm, AttachmentForm, UserRegistrationForm, UserProfileForm


def home_view(request):
    """
    Home view that redirects to dashboard if logged in, or login if not
    """
    if request.user.is_authenticated:
        return redirect('tickets:dashboard')
    else:
        return redirect('login')


def register_view(request):
    """
    User registration view
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                department=form.cleaned_data.get('department'),
                phone_number=form.cleaned_data.get('phone_number')
            )
            
            # Send welcome email to new user
            try:
                welcome_subject = "🎉 Welcome to IT Support System!"
                welcome_message = f"""
                <html>
                <body>
                    <h2>🎉 Welcome to the IT Support System!</h2>
                    
                    <p>Hello <strong>{user.get_full_name() or user.username}</strong>,</p>
                    
                    <p>Your account has been successfully created! You can now access the IT Support System to:</p>
                    
                    <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                        <h4>🚀 What you can do:</h4>
                        <ul>
                            <li>📝 Create and submit support tickets</li>
                            <li>📊 Track your ticket status</li>
                            <li>💬 Chat with IT staff</li>
                            <li>📅 View ticket deadlines</li>
                            <li>🔍 Search and filter tickets</li>
                        </ul>
                    </div>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #6c757d; margin: 15px 0;">
                        <h4>👤 Account Details:</h4>
                        <ul>
                            <li><strong>Username:</strong> {user.username}</li>
                            <li><strong>Email:</strong> {user.email}</li>
                            <li><strong>Department:</strong> {form.cleaned_data.get('department', 'Not specified')}</li>
                            <li><strong>Registration Date:</strong> {user.date_joined.strftime('%Y-%m-%d %H:%M')}</li>
                        </ul>
                    </div>
                    
                    <div style="background-color: #d4edda; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0;">
                        <h4>🔗 Quick Access:</h4>
                        <p>
                            <a href="http://localhost:8000/login/" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Login to System
                            </a>
                        </p>
                        <p>
                            <a href="http://localhost:8000/tickets/create/" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Create Your First Ticket
                            </a>
                        </p>
                    </div>
                    
                    <hr>
                    <p><small>If you have any questions or need assistance, please don't hesitate to contact the IT Support Team.</small></p>
                    <p><small>This is an automated message from the IT Support System.</small></p>
                </body>
                </html>
                """
                
                send_mail(
                    subject=welcome_subject,
                    message=welcome_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                    html_message=welcome_message,
                )
                print(f"Welcome email sent to {user.email}")
            except Exception as e:
                print(f"Failed to send welcome email to {user.email}: {e}")
            
            # Send notification to IT staff about new user registration
            try:
                it_staff = User.objects.filter(profile__is_it_staff=True)
                if it_staff.exists():
                    notification_subject = f"👤 New User Registered: {user.username}"
                    notification_message = f"""
                    <html>
                    <body>
                        <h2>👤 New User Registration</h2>
                        
                        <p>A new user has registered in the IT Support System:</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                            <h4>User Details:</h4>
                            <ul>
                                <li><strong>Username:</strong> {user.username}</li>
                                <li><strong>Full Name:</strong> {user.get_full_name() or 'Not provided'}</li>
                                <li><strong>Email:</strong> {user.email}</li>
                                <li><strong>Department:</strong> {form.cleaned_data.get('department', 'Not specified')}</li>
                                <li><strong>Phone:</strong> {form.cleaned_data.get('phone_number', 'Not provided')}</li>
                                <li><strong>Registration Date:</strong> {user.date_joined.strftime('%Y-%m-%d %H:%M')}</li>
                            </ul>
                        </div>
                        
                        <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                            <h4>🔗 Quick Actions:</h4>
                            <p>
                                <a href="http://localhost:8000/admin/auth/user/" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                    View in Admin Panel
                                </a>
                            </p>
                            <p>
                                <a href="http://localhost:8000/dashboard/" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                    Go to Dashboard
                                </a>
                            </p>
                        </div>
                        
                        <hr>
                        <p><small>This is an automated notification from the IT Support System.</small></p>
                    </body>
                    </html>
                    """
                    
                    staff_emails = [staff.email for staff in it_staff if staff.email]
                    if staff_emails:
                        send_mail(
                            subject=notification_subject,
                            message=notification_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=staff_emails,
                            fail_silently=False,
                            html_message=notification_message,
                        )
                        print(f"New user notification sent to IT staff: {staff_emails}")
            except Exception as e:
                print(f"Failed to send new user notification to IT staff: {e}")
            
            messages.success(request, 'Registration successful! Please log in. A welcome email has been sent to your email address.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'tickets/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """
    Main dashboard view showing tickets and analytics
    """
    user = request.user
    profile = user.profile
    
    # Get tickets based on user role
    if profile.is_it_staff:
        # IT staff can see all tickets
        tickets = Ticket.objects.all().select_related('created_by', 'assigned_to')
    else:
        # Regular users see only their tickets
        tickets = Ticket.objects.filter(created_by=user).select_related('assigned_to')
    
    # Apply filters
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    if search_query:
        tickets = tickets.filter(
            Q(ticket_id__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Analytics data
    analytics = {
        'total_tickets': tickets.count(),
        'open_tickets': tickets.filter(status='open').count(),
        'in_progress_tickets': tickets.filter(status='in_progress').count(),
        'resolved_tickets': tickets.filter(status='resolved').count(),
        'escalated_tickets': tickets.filter(status='escalated').count(),
        'high_priority_tickets': tickets.filter(priority='high').count(),
        'urgent_tickets': tickets.filter(priority='urgent').count(),
    }
    
    # Recent activity
    recent_comments = Comment.objects.filter(
        ticket__in=tickets
    ).select_related('author', 'ticket').order_by('-created_at')[:5]
    
    context = {
        'page_obj': page_obj,
        'analytics': analytics,
        'recent_comments': recent_comments,
        'status_choices': Ticket.STATUS_CHOICES,
        'priority_choices': Ticket.PRIORITY_CHOICES,
        'category_choices': Ticket.CATEGORY_CHOICES,
        'current_filters': {
            'status': status_filter,
            'priority': priority_filter,
            'category': category_filter,
            'search': search_query,
        },
        'is_it_staff': profile.is_it_staff,
    }
    
    return render(request, 'tickets/dashboard.html', context)


@login_required
def create_ticket_view(request):
    """
    Create new support ticket
    """
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            for file in files:
                Attachment.objects.create(
                    ticket=ticket,
                    file=file,
                    uploaded_by=request.user
                )
            
            # Send email notification to ticket creator
            try:
                ticket_url = f"http://localhost:8000/tickets/{ticket.ticket_id}/"
                creator_subject = f"✅ Ticket Created: {ticket.ticket_id} - {ticket.title}"
                creator_message = f"""
                <html>
                <body>
                    <h2>✅ Ticket Created Successfully!</h2>
                    
                    <p>Hello <strong>{ticket.created_by.get_full_name() or ticket.created_by.username}</strong>,</p>
                    
                    <p>Your support ticket has been created successfully. Here are the details:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                        <h3>Ticket Details:</h3>
                        <ul>
                            <li><strong>Ticket ID:</strong> {ticket.ticket_id}</li>
                            <li><strong>Title:</strong> {ticket.title}</li>
                            <li><strong>Priority:</strong> <span style="color: #dc3545;">{ticket.get_priority_display()}</span></li>
                            <li><strong>Category:</strong> {ticket.get_category_display()}</li>
                            <li><strong>Status:</strong> <span style="color: #28a745;">{ticket.get_status_display()}</span></li>
                            <li><strong>Created:</strong> {ticket.created_at.strftime('%Y-%m-%d %H:%M')}</li>
                            {f'<li><strong>Deadline:</strong> {ticket.deadline.strftime("%Y-%m-%d")}</li>' if ticket.deadline else ''}
                        </ul>
                    </div>
                    
                    <div style="background-color: #e9ecef; padding: 15px; margin: 15px 0;">
                        <h4>Description:</h4>
                        <p>{ticket.description}</p>
                    </div>
                    
                    <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                        <h4>🔗 Quick Actions:</h4>
                        <p>
                            <a href="{ticket_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                View Ticket Details
                            </a>
                        </p>
                        <p>
                            <a href="http://localhost:8000/dashboard/" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Go to Dashboard
                            </a>
                        </p>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
                        <h4>📋 Next Steps:</h4>
                        <ul>
                            <li>Your ticket has been submitted and is now in the queue</li>
                            <li>IT staff will review and assign it to the appropriate team member</li>
                            <li>You will receive email updates when the status changes</li>
                            <li>You can add comments or attachments to provide more information</li>
                        </ul>
                    </div>
                    
                    <hr>
                    <p><small>This is an automated notification from the IT Support System. Please do not reply to this email.</small></p>
                </body>
                </html>
                """
                
                send_mail(
                    subject=creator_subject,
                    message=creator_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ticket.created_by.email],
                    fail_silently=False,
                    html_message=creator_message,
                )
                print(f"Ticket creation confirmation sent to {ticket.created_by.email}")
            except Exception as e:
                print(f"Failed to send ticket creation email to {ticket.created_by.email}: {e}")
            
            # Send notification to IT staff about new ticket
            try:
                it_staff = User.objects.filter(profile__is_it_staff=True)
                if it_staff.exists():
                    staff_subject = f"🎫 New Ticket Created: {ticket.ticket_id} - {ticket.title}"
                    staff_message = f"""
                    <html>
                    <body>
                        <h2>🎫 New Support Ticket Created</h2>
                        
                        <p>A new support ticket has been created and requires attention:</p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                            <h3>Ticket Details:</h3>
                            <ul>
                                <li><strong>Ticket ID:</strong> {ticket.ticket_id}</li>
                                <li><strong>Title:</strong> {ticket.title}</li>
                                <li><strong>Priority:</strong> <span style="color: #dc3545;">{ticket.get_priority_display()}</span></li>
                                <li><strong>Category:</strong> {ticket.get_category_display()}</li>
                                <li><strong>Status:</strong> <span style="color: #28a745;">{ticket.get_status_display()}</span></li>
                                <li><strong>Created by:</strong> {ticket.created_by.get_full_name() or ticket.created_by.username}</li>
                                <li><strong>User Email:</strong> {ticket.created_by.email}</li>
                                <li><strong>Department:</strong> {ticket.created_by.profile.department or 'Not specified'}</li>
                                <li><strong>Created:</strong> {ticket.created_at.strftime('%Y-%m-%d %H:%M')}</li>
                                {f'<li><strong>Deadline:</strong> {ticket.deadline.strftime("%Y-%m-%d")}</li>' if ticket.deadline else ''}
                            </ul>
                        </div>
                        
                        <div style="background-color: #e9ecef; padding: 15px; margin: 15px 0;">
                            <h4>Description:</h4>
                            <p>{ticket.description}</p>
                        </div>
                        
                        <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                            <h4>🔗 Quick Actions:</h4>
                            <p>
                                <a href="{ticket_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                    View & Assign Ticket
                                </a>
                            </p>
                            <p>
                                <a href="http://localhost:8000/dashboard/" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                    Go to Dashboard
                                </a>
                            </p>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
                            <h4>⚠️ Action Required:</h4>
                            <ul>
                                <li>Review the ticket details and description</li>
                                <li>Assign the ticket to an appropriate IT staff member</li>
                                <li>Update the ticket status to "In Progress" when work begins</li>
                                <li>Communicate with the user if additional information is needed</li>
                            </ul>
                        </div>
                        
                        <hr>
                        <p><small>This is an automated notification from the IT Support System.</small></p>
                    </body>
                    </html>
                    """
                    
                    staff_emails = [staff.email for staff in it_staff if staff.email]
                    if staff_emails:
                        send_mail(
                            subject=staff_subject,
                            message=staff_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=staff_emails,
                            fail_silently=False,
                            html_message=staff_message,
                        )
                        print(f"New ticket notification sent to IT staff: {staff_emails}")
            except Exception as e:
                print(f"Failed to send new ticket notification to IT staff: {e}")
            
            messages.success(request, f'Ticket {ticket.ticket_id} created successfully! Confirmation email sent to your email address.')
            return redirect('tickets:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = TicketForm()
    
    return render(request, 'tickets/create_ticket.html', {'form': form})


@login_required
def ticket_detail_view(request, ticket_id):
    """
    View ticket details with comments and attachments
    """
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    user = request.user
    profile = user.profile
    
    # Check if user has permission to view this ticket
    if not profile.is_it_staff and ticket.created_by != user:
        messages.error(request, 'You do not have permission to view this ticket.')
        return redirect('tickets:dashboard')
    
    # Get comments (filter internal comments for non-IT staff)
    comments = ticket.comments.all()
    if not profile.is_it_staff:
        comments = comments.filter(is_internal=False)
    
    # Get attachments
    attachments = ticket.attachments.all()
    
    # Handle new comment
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = user
            comment.is_internal = profile.is_it_staff and comment_form.cleaned_data.get('is_internal', False)
            comment.save()
            
            # Send notification to ticket creator if comment is from IT staff
            if profile.is_it_staff and ticket.created_by != user:
                try:
                    send_mail(
                        subject=f'New Comment on Ticket {ticket.ticket_id}',
                        message=f'A new comment has been added to your ticket "{ticket.title}".\n\nComment: {comment.message}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[ticket.created_by.email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Failed to send comment notification: {e}")
            
            messages.success(request, 'Comment added successfully!')
            return redirect('tickets:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        comment_form = CommentForm()
    
    # Handle file upload
    if request.method == 'POST' and 'attachment' in request.FILES:
        attachment_form = AttachmentForm(request.POST, request.FILES)
        if attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.ticket = ticket
            attachment.uploaded_by = user
            attachment.save()
            messages.success(request, 'File uploaded successfully!')
            return redirect('tickets:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        attachment_form = AttachmentForm()
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'is_it_staff': profile.is_it_staff,
        'can_escalate': profile.is_it_staff and ticket.status not in ['resolved', 'closed'],
    }
    
    return render(request, 'tickets/ticket_detail.html', context)


@login_required
def update_ticket_status_view(request, ticket_id):
    """
    Update ticket status (IT staff only)
    """
    if not request.user.profile.is_it_staff:
        messages.error(request, 'You do not have permission to update ticket status.')
        return redirect('tickets:dashboard')
    
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')
        
        if new_status in dict(Ticket.STATUS_CHOICES):
            ticket.status = new_status
            if assigned_to_id:
                try:
                    assigned_user = User.objects.get(id=assigned_to_id)
                    ticket.assigned_to = assigned_user
                except User.DoesNotExist:
                    pass
            
            ticket.save()
            
            # Send notification to ticket creator
            try:
                ticket_url = f"http://localhost:8000/tickets/{ticket.ticket_id}/"
                status_subject = f"📋 Ticket Status Updated: {ticket.ticket_id} - {ticket.title}"
                status_message = f"""
                <html>
                <body>
                    <h2>📋 Ticket Status Update</h2>
                    
                    <p>Hello <strong>{ticket.created_by.get_full_name() or ticket.created_by.username}</strong>,</p>
                    
                    <p>Your support ticket status has been updated:</p>
                    
                    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                        <h3>Ticket Details:</h3>
                        <ul>
                            <li><strong>Ticket ID:</strong> {ticket.ticket_id}</li>
                            <li><strong>Title:</strong> {ticket.title}</li>
                            <li><strong>New Status:</strong> <span style="color: #28a745; font-weight: bold;">{ticket.get_status_display()}</span></li>
                            <li><strong>Priority:</strong> <span style="color: #dc3545;">{ticket.get_priority_display()}</span></li>
                            <li><strong>Category:</strong> {ticket.get_category_display()}</li>
                            <li><strong>Assigned to:</strong> {ticket.assigned_to.get_full_name() if ticket.assigned_to else 'Not assigned'}</li>
                            <li><strong>Updated by:</strong> {request.user.get_full_name() or request.user.username}</li>
                            <li><strong>Updated:</strong> {timezone.now().strftime('%Y-%m-%d %H:%M')}</li>
                        </ul>
                    </div>
                    
                    <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                        <h4>🔗 Quick Actions:</h4>
                        <p>
                            <a href="{ticket_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                View Ticket Details
                            </a>
                        </p>
                        <p>
                            <a href="http://localhost:8000/dashboard/" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                Go to Dashboard
                            </a>
                        </p>
                    </div>
                    
                    <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
                        <h4>📋 What this means:</h4>
                        <ul>
                            <li>Your ticket is being actively worked on by our IT team</li>
                            <li>You will receive updates as progress is made</li>
                            <li>Feel free to add comments if you have additional information</li>
                            <li>Contact the assigned staff member if you have urgent questions</li>
                        </ul>
                    </div>
                    
                    <hr>
                    <p><small>This is an automated notification from the IT Support System. Please do not reply to this email.</small></p>
                </body>
                </html>
                """
                
                send_mail(
                    subject=status_subject,
                    message=status_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ticket.created_by.email],
                    fail_silently=False,
                    html_message=status_message,
                )
                print(f"Status update notification sent to {ticket.created_by.email}")
            except Exception as e:
                print(f"Failed to send status update notification: {e}")
            
            messages.success(request, f'Ticket status updated to {ticket.get_status_display()}')
        
        return redirect('tickets:ticket_detail', ticket_id=ticket.ticket_id)
    
    # Get IT staff for assignment dropdown
    it_staff = User.objects.filter(profile__is_it_staff=True)
    
    context = {
        'ticket': ticket,
        'status_choices': Ticket.STATUS_CHOICES,
        'it_staff': it_staff,
    }
    
    return render(request, 'tickets/update_ticket_status.html', context)


@login_required
def escalate_ticket_view(request, ticket_id):
    """
    Escalate ticket to another user (IT staff only)
    """
    if not request.user.profile.is_it_staff:
        messages.error(request, 'You do not have permission to escalate tickets.')
        return redirect('tickets:dashboard')
    
    ticket = get_object_or_404(Ticket, ticket_id=ticket_id)
    
    if request.method == 'POST':
        escalated_to_id = request.POST.get('escalated_to')
        escalation_reason = request.POST.get('escalation_reason', '')
        
        if escalated_to_id:
            try:
                # Handle primary escalation contact
                if escalated_to_id == 'primary_escalation':
                    # Create a special escalation without assigning to a specific user
                    ticket.status = "escalated"
                    ticket.save()
                    
                    # Add escalation reason as a comment if provided
                    if escalation_reason.strip():
                        Comment.objects.create(
                            ticket=ticket,
                            author=request.user,
                            message=f"🚨 ESCALATION TO PRIMARY CONTACT: {escalation_reason}",
                            is_internal=True
                        )
                    
                    # Send email directly to primary escalation contact
                    from django.core.mail import send_mail
                    from django.conf import settings
                    
                    primary_escalation_email = "johnjaymoanes009@gmail.com"
                    ticket_url = f"http://localhost:8000/tickets/{ticket.ticket_id}/"
                    
                    email_subject = f"🚨 URGENT: Ticket {ticket.ticket_id} Escalated to Primary Contact - {ticket.title}"
                    email_message = f"""
                    <html>
                    <body>
                        <h2>🚨 Primary Escalation Alert</h2>
                        
                        <p><strong>This ticket has been escalated directly to the primary escalation contact:</strong></p>
                        
                        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #dc3545; margin: 15px 0;">
                            <h3>Ticket Details:</h3>
                            <ul>
                                <li><strong>Ticket ID:</strong> {ticket.ticket_id}</li>
                                <li><strong>Title:</strong> {ticket.title}</li>
                                <li><strong>Priority:</strong> <span style="color: #dc3545;">{ticket.get_priority_display()}</span></li>
                                <li><strong>Category:</strong> {ticket.get_category_display()}</li>
                                <li><strong>Status:</strong> <span style="color: #ffc107;">{ticket.get_status_display()}</span></li>
                                <li><strong>Created by:</strong> {ticket.created_by.get_full_name() or ticket.created_by.username}</li>
                                <li><strong>Escalated by:</strong> {request.user.get_full_name() or request.user.username}</li>
                                <li><strong>Created:</strong> {ticket.created_at.strftime('%Y-%m-%d %H:%M')}</li>
                            </ul>
                        </div>
                        
                        <div style="background-color: #e9ecef; padding: 15px; margin: 15px 0;">
                            <h4>Description:</h4>
                            <p>{ticket.description}</p>
                        </div>
                        
                        <div style="background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;">
                            <h4>Escalation Reason:</h4>
                            <p>{escalation_reason if escalation_reason.strip() else 'No specific reason provided.'}</p>
                        </div>
                        
                        <div style="background-color: #d1ecf1; padding: 15px; border-left: 4px solid #17a2b8; margin: 15px 0;">
                            <h4>🔗 Quick Actions:</h4>
                            <p>
                                <a href="{ticket_url}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                    View Ticket Details
                                </a>
                            </p>
                            <p>
                                <a href="http://localhost:8000/dashboard/" 
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
                    
                    send_mail(
                        subject=email_subject,
                        message=email_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[primary_escalation_email],
                        fail_silently=False,
                        html_message=email_message,
                    )
                    
                    messages.success(request, f'Ticket escalated to primary contact (johnjaymoanes009@gmail.com). Email notification sent!')
                    return redirect('tickets:ticket_detail', ticket_id=ticket.ticket_id)
                
                else:
                    # Handle regular user escalation
                    escalated_user = User.objects.get(id=escalated_to_id)
                    
                    # Add escalation reason as a comment if provided
                    if escalation_reason.strip():
                        Comment.objects.create(
                            ticket=ticket,
                            author=request.user,
                            message=f"🚨 ESCALATION REASON: {escalation_reason}",
                            is_internal=True
                        )
                    
                    ticket.escalate_ticket(escalated_user)
                    messages.success(request, f'Ticket escalated to {escalated_user.username}. Email notifications sent!')
                    return redirect('tickets:ticket_detail', ticket_id=ticket.ticket_id)
                    
            except User.DoesNotExist:
                messages.error(request, 'Selected user does not exist.')
    
    # Get IT staff for escalation dropdown
    it_staff = User.objects.filter(profile__is_it_staff=True).exclude(id=request.user.id)
    
    context = {
        'ticket': ticket,
        'it_staff': it_staff,
    }
    
    return render(request, 'tickets/escalate_ticket.html', context)


@login_required
def calendar_view(request):
    """
    Calendar view showing tickets by deadline
    """
    user = request.user
    profile = user.profile
    
    # Get tickets with deadlines
    if profile.is_it_staff:
        tickets = Ticket.objects.filter(deadline__isnull=False).select_related('created_by', 'assigned_to')
    else:
        tickets = Ticket.objects.filter(created_by=user, deadline__isnull=False).select_related('assigned_to')
    
    # Group tickets by deadline
    calendar_data = {}
    for ticket in tickets:
        deadline_str = ticket.deadline.strftime('%Y-%m-%d')
        if deadline_str not in calendar_data:
            calendar_data[deadline_str] = []
        calendar_data[deadline_str].append(ticket)
    
    context = {
        'calendar_data': calendar_data,
        'is_it_staff': profile.is_it_staff,
    }
    
    return render(request, 'tickets/calendar.html', context)


@login_required
def chat_view(request):
    """
    Chat room view
    """
    user = request.user
    
    # Get recent messages
    recent_messages = ChatMessage.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).select_related('sender', 'receiver').order_by('-timestamp')[:50]
    
    # Get users for chat (IT staff can chat with anyone, regular users with IT staff)
    if user.profile.is_it_staff:
        chat_users = User.objects.filter(is_active=True).exclude(id=user.id)
    else:
        chat_users = User.objects.filter(profile__is_it_staff=True, is_active=True)
    
    context = {
        'recent_messages': recent_messages,
        'chat_users': chat_users,
        'is_it_staff': user.profile.is_it_staff,
    }
    
    return render(request, 'tickets/chat.html', context)


@login_required
@require_POST
def send_message_view(request):
    """
    Send chat message (AJAX)
    """
    try:
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        message_text = data.get('message')
        
        if not receiver_id or not message_text:
            return JsonResponse({'success': False, 'error': 'Missing required fields'})
        
        receiver = get_object_or_404(User, id=receiver_id)
        
        # Create chat message
        chat_message = ChatMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            message=message_text
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': chat_message.id,
                'sender': chat_message.sender.username,
                'receiver': chat_message.receiver.username,
                'message': chat_message.message,
                'timestamp': chat_message.timestamp.isoformat(),
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_messages_view(request, user_id):
    """
    Get messages between current user and specified user (AJAX)
    """
    try:
        other_user = get_object_or_404(User, id=user_id)
        
        messages = ChatMessage.objects.filter(
            Q(sender=request.user, receiver=other_user) |
            Q(sender=other_user, receiver=request.user)
        ).select_related('sender', 'receiver').order_by('timestamp')
        
        # Mark messages as read
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'sender': msg.sender.username,
                'receiver': msg.receiver.username,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read,
                'is_sender': msg.sender == request.user,
            })
        
        return JsonResponse({'success': True, 'messages': messages_data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def toggle_dark_mode_view(request):
    """
    Toggle dark mode preference (AJAX)
    """
    if request.method == 'POST':
        try:
            profile = request.user.profile
            profile.dark_mode = not profile.dark_mode
            profile.save()
            
            return JsonResponse({
                'success': True,
                'dark_mode': profile.dark_mode
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def analytics_view(request):
    """
    Analytics dashboard (IT staff only)
    """
    if not request.user.profile.is_it_staff:
        messages.error(request, 'You do not have permission to view analytics.')
        return redirect('tickets:dashboard')
    
    # Get analytics data
    total_tickets = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
    resolved_tickets = Ticket.objects.filter(status='resolved').count()
    closed_tickets = Ticket.objects.filter(status='closed').count()
    escalated_tickets = Ticket.objects.filter(status='escalated').count()
    
    # Tickets by category
    category_stats = Ticket.objects.values('category').annotate(count=Count('id')).order_by('-count')
    
    # Tickets by priority
    priority_stats = Ticket.objects.values('priority').annotate(count=Count('id')).order_by('-count')
    
    # Tickets by status
    status_stats = Ticket.objects.values('status').annotate(count=Count('id')).order_by('-count')
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_tickets = Ticket.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_resolved = Ticket.objects.filter(resolved_at__gte=thirty_days_ago).count()
    
    # Average resolution time
    resolved_tickets_with_time = Ticket.objects.filter(
        resolved_at__isnull=False,
        created_at__isnull=False
    )
    
    if resolved_tickets_with_time.exists():
        total_time = sum([
            (ticket.resolved_at - ticket.created_at).total_seconds()
            for ticket in resolved_tickets_with_time
        ])
        avg_resolution_hours = total_time / (resolved_tickets_with_time.count() * 3600)
    else:
        avg_resolution_hours = 0
    
    context = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'escalated_tickets': escalated_tickets,
        'category_stats': category_stats,
        'priority_stats': priority_stats,
        'status_stats': status_stats,
        'recent_tickets': recent_tickets,
        'recent_resolved': recent_resolved,
        'avg_resolution_hours': round(avg_resolution_hours, 2),
    }
    
    return render(request, 'tickets/analytics.html', context)
