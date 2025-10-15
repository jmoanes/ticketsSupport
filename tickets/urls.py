from django.urls import path
from . import views
from . import export_views

app_name = 'tickets'

urlpatterns = [
    # Authentication
    path('register/', views.register_view, name='register'),
    
    # Main views
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Ticket management
    path('tickets/create/', views.create_ticket_view, name='create_ticket'),
    path('tickets/<str:ticket_id>/', views.ticket_detail_view, name='ticket_detail'),
    path('tickets/<str:ticket_id>/update-status/', views.update_ticket_status_view, name='update_ticket_status'),
    path('tickets/<str:ticket_id>/escalate/', views.escalate_ticket_view, name='escalate_ticket'),
    
    # Calendar and chat
    path('calendar/', views.calendar_view, name='calendar'),
    path('chat/', views.chat_view, name='chat'),
    
    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    
    # AJAX endpoints
    path('api/send-message/', views.send_message_view, name='send_message'),
    path('api/get-messages/<int:user_id>/', views.get_messages_view, name='get_messages'),
    path('api/toggle-dark-mode/', views.toggle_dark_mode_view, name='toggle_dark_mode'),
    
    # Export endpoints
    path('export/tickets/pdf/', export_views.export_tickets_pdf, name='export_tickets_pdf'),
    path('export/tickets/excel/', export_views.export_tickets_excel, name='export_tickets_excel'),
    path('export/analytics/pdf/', export_views.export_analytics_pdf, name='export_analytics_pdf'),
    path('export/ticket/<str:ticket_id>/pdf/', export_views.export_single_ticket_pdf, name='export_single_ticket_pdf'),
]
