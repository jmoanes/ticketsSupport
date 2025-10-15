from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ticket, Comment, Attachment, UserProfile


class UserRegistrationForm(UserCreationForm):
    """
    Extended user registration form with additional fields
    """
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")
    first_name = forms.CharField(max_length=30, required=True, help_text="Required. Enter your first name.")
    last_name = forms.CharField(max_length=30, required=True, help_text="Required. Enter your last name.")
    department = forms.CharField(max_length=100, required=False, help_text="Optional. Enter your department.")
    phone_number = forms.CharField(max_length=20, required=False, help_text="Optional. Enter your phone number.")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'department', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes for styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = True

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile
    """
    class Meta:
        model = UserProfile
        fields = ['department', 'phone_number', 'dark_mode']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TicketForm(forms.ModelForm):
    """
    Form for creating and editing tickets
    """
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief description of the issue'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Detailed description of the problem'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make deadline optional
        self.fields['deadline'].required = False
        # Add help text
        self.fields['title'].help_text = "Provide a clear, concise title for your issue"
        self.fields['description'].help_text = "Include as much detail as possible to help us resolve your issue quickly"
        self.fields['category'].help_text = "Select the category that best describes your issue"
        self.fields['priority'].help_text = "How urgent is this issue?"
        self.fields['deadline'].help_text = "Optional: When do you need this resolved by?"


class CommentForm(forms.ModelForm):
    """
    Form for adding comments to tickets
    """
    class Meta:
        model = Comment
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a comment...'
            }),
            'is_internal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Only show internal checkbox for IT staff
        if not user or not hasattr(user, 'profile') or not user.profile.is_it_staff:
            self.fields.pop('is_internal', None)
        else:
            self.fields['is_internal'].help_text = "Check this box to make this comment visible only to IT staff"


class AttachmentForm(forms.ModelForm):
    """
    Form for uploading file attachments
    """
    class Meta:
        model = Attachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.zip,.rar'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].help_text = "Upload files (PDF, DOC, images, etc.) - Max 10MB per file"
        self.fields['file'].required = True

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size cannot exceed 10MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar']
            file_extension = file.name.lower().split('.')[-1]
            if f'.{file_extension}' not in allowed_extensions:
                raise forms.ValidationError(f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}")
        
        return file


class TicketSearchForm(forms.Form):
    """
    Form for searching and filtering tickets
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by ticket ID, title, or description...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(Ticket.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + list(Ticket.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + list(Ticket.CATEGORY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class TicketStatusUpdateForm(forms.ModelForm):
    """
    Form for updating ticket status (IT staff only)
    """
    class Meta:
        model = Ticket
        fields = ['status', 'assigned_to']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show IT staff in assigned_to field
        self.fields['assigned_to'].queryset = User.objects.filter(profile__is_it_staff=True)
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = "Unassigned"


class EscalationForm(forms.Form):
    """
    Form for escalating tickets
    """
    escalated_to = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Will be set in view
        empty_label="Select IT staff member",
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select the IT staff member to escalate this ticket to"
    )
    escalation_reason = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional: Explain why this ticket needs to be escalated...'
        }),
        help_text="Optional: Provide a reason for the escalation"
    )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Set queryset to IT staff excluding current user
        if current_user:
            self.fields['escalated_to'].queryset = User.objects.filter(
                profile__is_it_staff=True
            ).exclude(id=current_user.id)
