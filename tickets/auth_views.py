from django.contrib.auth import logout, login
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.views import LoginView


class CustomLoginView(LoginView):
    """
    Custom login view that shows a success message
    """
    template_name = 'tickets/login.html'
    
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        login(self.request, form.get_user())
        
        # Show success message
        messages.success(self.request, f'Welcome back, {form.get_user().username}!')
        
        return redirect(self.get_success_url())


def custom_logout_view(request):
    """
    Custom logout view that shows a success message
    """
    if request.user.is_authenticated:
        username = request.user.username
        messages.success(request, f'You have been successfully logged out, {username}.')
    
    logout(request)
    return redirect('login')
