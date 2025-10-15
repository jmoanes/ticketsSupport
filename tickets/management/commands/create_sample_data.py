from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from tickets.models import UserProfile, Ticket, Comment, ChatMessage


class Command(BaseCommand):
    help = 'Create sample data for testing the IT Support System'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='Number of regular users to create',
        )
        parser.add_argument(
            '--staff',
            type=int,
            default=3,
            help='Number of IT staff to create',
        )
        parser.add_argument(
            '--tickets',
            type=int,
            default=25,
            help='Number of tickets to create',
        )

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create regular users
        regular_users = self.create_regular_users(options['users'])
        
        # Create IT staff
        it_staff = self.create_it_staff(options['staff'])
        
        # Create tickets
        tickets = self.create_tickets(options['tickets'], regular_users, it_staff)
        
        # Create comments
        self.create_comments(tickets, regular_users + it_staff)
        
        # Create chat messages
        self.create_chat_messages(regular_users, it_staff)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(regular_users)} regular users\n'
                f'- {len(it_staff)} IT staff members\n'
                f'- {len(tickets)} tickets\n'
                f'- Sample comments and chat messages'
            )
        )

    def create_regular_users(self, count):
        """Create regular users with profiles"""
        users = []
        departments = ['HR', 'Finance', 'Marketing', 'Sales', 'Operations', 'Legal']
        
        for i in range(count):
            username = f'user{i+1}'
            email = f'user{i+1}@company.com'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=f'User{i+1}',
                    last_name='Test'
                )
                
                UserProfile.objects.create(
                    user=user,
                    department=random.choice(departments),
                    phone_number=f'555-{random.randint(1000, 9999)}',
                    dark_mode=random.choice([True, False])
                )
                
                users.append(user)
                self.stdout.write(f'Created user: {username}')
        
        return users

    def create_it_staff(self, count):
        """Create IT staff members"""
        staff = []
        departments = ['IT Support', 'Network Admin', 'System Admin', 'Help Desk']
        
        for i in range(count):
            username = f'staff{i+1}'
            email = f'staff{i+1}@company.com'
            
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password='password123',
                    first_name=f'Staff{i+1}',
                    last_name='IT'
                )
                
                UserProfile.objects.create(
                    user=user,
                    department=random.choice(departments),
                    phone_number=f'555-{random.randint(1000, 9999)}',
                    is_it_staff=True,
                    dark_mode=random.choice([True, False])
                )
                
                staff.append(user)
                self.stdout.write(f'Created IT staff: {username}')
        
        return staff

    def create_tickets(self, count, regular_users, it_staff):
        """Create sample tickets"""
        tickets = []
        categories = ['hardware', 'software', 'network', 'access', 'other']
        priorities = ['low', 'medium', 'high', 'urgent']
        statuses = ['open', 'in_progress', 'resolved', 'closed', 'escalated']
        
        ticket_titles = [
            'Computer not starting',
            'Email access issues',
            'Printer not working',
            'Software installation needed',
            'Network connectivity problems',
            'Password reset required',
            'Monitor display issues',
            'Keyboard not responding',
            'Internet connection slow',
            'Application crashes frequently',
            'File sharing problems',
            'VPN connection issues',
            'Database access denied',
            'Server performance issues',
            'Backup system failure'
        ]
        
        ticket_descriptions = [
            'The computer shows a black screen when I try to start it.',
            'I cannot access my email account. Getting authentication error.',
            'The printer is showing error messages and not printing documents.',
            'I need to install new software for my project work.',
            'Internet connection is very slow and keeps disconnecting.',
            'I forgot my password and need it reset.',
            'The monitor shows distorted colors and flickering.',
            'Some keys on the keyboard are not working properly.',
            'Web pages are loading very slowly.',
            'The application keeps crashing when I try to save files.',
            'I cannot access shared files on the network drive.',
            'VPN connection fails with timeout error.',
            'Getting access denied when trying to connect to database.',
            'The server is running very slowly.',
            'Backup system is not working and showing errors.'
        ]
        
        for i in range(count):
            created_by = random.choice(regular_users)
            assigned_to = random.choice(it_staff) if random.choice([True, False]) else None
            escalated_to = random.choice(it_staff) if random.choice([True, False]) else None
            
            # Random creation date within last 30 days
            created_at = timezone.now() - timedelta(days=random.randint(0, 30))
            
            # Random deadline (some tickets have deadlines)
            deadline = None
            if random.choice([True, False]):
                deadline = (timezone.now() + timedelta(days=random.randint(1, 14))).date()
            
            ticket = Ticket.objects.create(
                title=random.choice(ticket_titles),
                description=random.choice(ticket_descriptions),
                category=random.choice(categories),
                priority=random.choice(priorities),
                status=random.choice(statuses),
                created_by=created_by,
                assigned_to=assigned_to,
                escalated_to=escalated_to,
                deadline=deadline,
                created_at=created_at
            )
            
            tickets.append(ticket)
            self.stdout.write(f'Created ticket: {ticket.ticket_id}')
        
        return tickets

    def create_comments(self, tickets, all_users):
        """Create sample comments for tickets"""
        comment_messages = [
            'Thanks for reporting this issue. I will look into it.',
            'Can you provide more details about when this happens?',
            'I have assigned this ticket to our technical team.',
            'The issue has been resolved. Please test and confirm.',
            'This requires escalation to senior staff.',
            'I need additional information to proceed.',
            'Working on this issue. Will update soon.',
            'Please try restarting your computer.',
            'The fix has been applied. Please check.',
            'This is a known issue. We are working on a permanent solution.'
        ]
        
        for ticket in tickets:
            # Create 1-3 comments per ticket
            comment_count = random.randint(1, 3)
            
            for _ in range(comment_count):
                author = random.choice(all_users)
                is_internal = author.profile.is_it_staff and random.choice([True, False])
                
                Comment.objects.create(
                    ticket=ticket,
                    author=author,
                    message=random.choice(comment_messages),
                    is_internal=is_internal,
                    created_at=ticket.created_at + timedelta(hours=random.randint(1, 48))
                )

    def create_chat_messages(self, regular_users, it_staff):
        """Create sample chat messages"""
        chat_messages = [
            'Hello, I need help with my computer.',
            'Sure, I can help you with that.',
            'What seems to be the problem?',
            'My computer is running very slowly.',
            'Have you tried restarting it?',
            'Yes, but the problem persists.',
            'I will create a ticket for this issue.',
            'Thank you for your help.',
            'You are welcome. I will keep you updated.',
            'Is there anything else I can help you with?'
        ]
        
        # Create conversations between regular users and IT staff
        for user in regular_users[:5]:  # Only first 5 users
            for staff in it_staff[:2]:  # Only first 2 staff
                # Create 3-5 messages per conversation
                message_count = random.randint(3, 5)
                
                for i in range(message_count):
                    sender = user if i % 2 == 0 else staff
                    receiver = staff if i % 2 == 0 else user
                    
                    ChatMessage.objects.create(
                        sender=sender,
                        receiver=receiver,
                        message=random.choice(chat_messages),
                        timestamp=timezone.now() - timedelta(hours=random.randint(1, 72))
                    )
