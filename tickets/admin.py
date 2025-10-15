from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Ticket, Comment, Attachment, ChatMessage, TicketNotification


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile to extend User admin
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('department', 'is_it_staff', 'phone_number', 'dark_mode')


class CustomUserAdmin(UserAdmin):
    """
    Custom User admin with UserProfile inline
    """
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_department', 'get_is_it_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__is_it_staff', 'profile__department')

    def get_department(self, obj):
        return obj.profile.department if hasattr(obj, 'profile') else 'N/A'
    get_department.short_description = 'Department'

    def get_is_it_staff(self, obj):
        return obj.profile.is_it_staff if hasattr(obj, 'profile') else False
    get_is_it_staff.short_description = 'IT Staff'
    get_is_it_staff.boolean = True


class CommentInline(admin.TabularInline):
    """
    Inline admin for ticket comments
    """
    model = Comment
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'message', 'is_internal', 'created_at')


class AttachmentInline(admin.TabularInline):
    """
    Inline admin for ticket attachments
    """
    model = Attachment
    extra = 0
    readonly_fields = ('original_filename', 'file_size', 'uploaded_by', 'uploaded_at')
    fields = ('file', 'original_filename', 'file_size', 'uploaded_by', 'uploaded_at')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """
    Admin interface for Ticket model
    """
    list_display = ('ticket_id', 'title', 'created_by', 'assigned_to', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at', 'assigned_to')
    search_fields = ('ticket_id', 'title', 'description', 'created_by__username', 'assigned_to__username')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at', 'resolved_at')
    inlines = [CommentInline, AttachmentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('ticket_id', 'title', 'description', 'category', 'priority', 'status')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to', 'escalated_to')
        }),
        ('Timeline', {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'deadline'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """
        Optimize queryset with select_related
        """
        return super().get_queryset(request).select_related('created_by', 'assigned_to', 'escalated_to')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model
    """
    list_display = ('ticket', 'author', 'is_internal', 'created_at')
    list_filter = ('is_internal', 'created_at', 'ticket__status')
    search_fields = ('message', 'author__username', 'ticket__ticket_id')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    """
    Admin interface for Attachment model
    """
    list_display = ('original_filename', 'ticket', 'uploaded_by', 'get_file_size_display', 'uploaded_at')
    list_filter = ('uploaded_at', 'ticket__status')
    search_fields = ('original_filename', 'ticket__ticket_id', 'uploaded_by__username')
    readonly_fields = ('original_filename', 'file_size', 'uploaded_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Admin interface for ChatMessage model
    """
    list_display = ('sender', 'receiver', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('message', 'sender__username', 'receiver__username')
    readonly_fields = ('timestamp',)


@admin.register(TicketNotification)
class TicketNotificationAdmin(admin.ModelAdmin):
    """
    Admin interface for TicketNotification model
    """
    list_display = ('ticket', 'user', 'notification_type', 'is_read', 'sent_at')
    list_filter = ('notification_type', 'is_read', 'sent_at')
    search_fields = ('ticket__ticket_id', 'user__username')
    readonly_fields = ('sent_at',)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
