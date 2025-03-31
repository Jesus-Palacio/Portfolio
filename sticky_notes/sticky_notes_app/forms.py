from django import forms
from .models import Note
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NoteForm(forms.ModelForm):
    """
    A form for creating and editing Note model instances.
    Provides fields for sticky note title, content, color, and position
    coordinates, with customized widgets for user input. Tied to the Note model
    for automatic validation and saving. Used in views for note creation and
    updates, with position fields hidden for client-side management.

    Attributes:
        title (CharField): A text input for the note title, styled with
            'form-control' class.
        content (Textarea): A textarea for the note content, styled with
            'form-control' class.
        color (CharField): A color picker input for selecting note color,
            styled with 'form-control' class.
        x_position (IntegerField): A hidden input for the note's x-coordinate.
        y_position (IntegerField): A hidden input for the note's y-coordinate.
    """

    class Meta:
        """
        Configures metadata for the NoteForm ModelForm.
        Defines the model, fields, and widget customizations for the NoteForm.
        Links the form to the Note model and specifies which fields to include,
        along with their HTML widget representations for rendering in templates

        Attributes:
            model (Model): The Note model class that the form is based on.
            fields (list): A list of field names from the Note model to include
                in the form: ['title', 'content', 'color', 'x_position',
                'y_position'].
            widgets (dict): A dictionary mapping field names to widget
                instances with custom attributes for HTML rendering:
                - 'title': TextInput with 'form-control' class.
                - 'content': Textarea with 'form-control' class.
                - 'color': TextInput as color picker with 'form-control' class.
                - 'x_position': HiddenInput.
                - 'y_position': HiddenInput.
        """

        model = Note
        fields = ['title', 'content', 'color', 'x_position', 'y_position']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={
                'type': 'color', 'class': 'form-control'}),
            'x_position': forms.HiddenInput(),
            'y_position': forms.HiddenInput(),
        }


class UserRegistrationForm(UserCreationForm):
    """
    A form for registering new users with email, extending UserCreationForm.
    Enhances Django's built-in UserCreationForm by adding a required email
    field alongside the standard username and password fields. Used for
    creating new User instances with username, email, and password data,
    validated and saved through inherited functionality.

    Attributes:
        email (EmailField): A required field for the user's email address,
            validated for proper email format.
        username (CharField): Inherited field for the user's username, with
            uniqueness validation (from UserCreationForm).
        password1 (CharField): Inherited password field for initial password
            entry, rendered as a password input (from UserCreationForm).
        password2 (CharField): Inherited password confirmation field, ensures
            match with password1 (from UserCreationForm).
    """

    email = forms.EmailField(required=True)

    class Meta:
        """
        Configures metadata for the UserRegistrationForm.
        Specifies the User model and the fields to include in the form for user
        registration. Links the form to Django's User model and defines the
        subset of fields (username, email, passwords) to be used, ensuring the
        form creates User instances with these attributes.

        Attributes:
            model (Model): The User model class from django.contrib.auth.models
                defining the target model for the form.
            fields (list): A list of field names to include in the form:
                ['username', 'email', 'password1', 'password2'].
        """

        model = User
        fields = ['username', 'email', 'password1', 'password2']
