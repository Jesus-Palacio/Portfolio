from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Note
from .forms import NoteForm
from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.http import HttpResponse, HttpRequest


@login_required
def note_list(request: HttpRequest) -> HttpResponse:
    """
    Displays a list of notes from an authenticated user.
    Retrieves notes from the database filtered by the current user and renders
    them in a template. Requires user authentication via the login_required
    decorator to ensure only the user's own notes are shown.

    Args:
        request (HttpRequest): The HTTP request object containing metadata,
            including the authenticated user.

    Returns:
        HttpResponse: A rendered HTML response displaying the user's notes in
            the template that displays the list of notes.
    """

    notes = Note.objects.filter(user=request.user)
    return render(request, 'sticky_notes_app/note_list.html', {'notes': notes})


@login_required
def note_create(request: HttpRequest) -> HttpResponse:
    """
    Handles the creation of a sticky note for authenticated users. Presents an
    empty form, and upon form submission, validates and saves the sticky note
    before redirecting to the template displaying the list of sticky notes.
    Requires user authentication.

    Args:
        request (HttpRequest): The HTTP request object containing metadata
            about the request.

    Returns:
        HttpResponse: Renders the template with the form to create a note.
            Redirects to the URL that displays the list of notes on successful
            POST creation.
    """

    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('note_list')
    else:
        form = NoteForm()
    return render(request, 'sticky_notes_app/note_form.html', {'form': form})


@login_required
def note_update(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Handles updating an existing sticky note for the authenticated user.

    Retrieves a specific sticky note by primary key (ID of the note to update),
    ensuring it belongs to the current user. Displays a pre-populated form with
    the existing note's data, and upon form submission, processes updates. If
    the form is valid, saves the changes and redirects to the note list.
    Requires user authentication and ownership of the note.

    Args:
        request (HttpRequest): The HTTP request object containing metadata,
            including the authenticated user.
        pk (int): The primary key (ID) of the note to update.

    Returns:
        HttpResponse: Renders the template with the form context to edit a
            note.
            Redirects to the URL that displays the list of notes on successful
            POST update.
    """

    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('note_list')
    else:
        form = NoteForm(instance=note)
    return render(request, 'sticky_notes_app/note_form.html', {'form': form})


@login_required
def note_delete(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Handles the deletion of a specific sticky note for the authenticated user.
    Retrieves a note by primary key (ID of the note to delete), ensuring it
    belongs to the current user. Displays a confirmation page for GET requests
    and deletes the note for POST requests, then redirects to the note list.
    Requires user authentication and ownership of the note to proceed.

    Args:
        request (HttpRequest): The HTTP request object containing metadata,
            including the authenticated user.
        pk (int): The primary key (ID) of the note to delete.

    Returns:
        HttpResponse: Renders the delete confirmation template for GET requests
            with the note context.
            Redirects to the URL that displays the list of notes on successful
            POST deletion.
    """

    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('note_list')
    return render(
        request, 'sticky_notes_app/note_confirm_delete.html', {'note': note})


@login_required
def update_position(request: HttpRequest) -> JsonResponse:
    """
    Updates the position of a sticky note for the authenticated user via POST
    request. Expects a POST request with note ID and new x, y coordinates.
    Retrieves the note by ID, ensures it belongs to the current user, updates
    its position, and saves the changes. Returns a JSON response indicating
    success or error. Designed for AJAX usage and requires user authentication.

    Args:
        request (HttpRequest): The HTTP request object containing metadata,
            including the authenticated user and POST data with 'note_id', 'x',
            and 'y' keys.

    Returns:
        JsonResponse: A JSON response with {'status': 'success'} on successful
            POST update, or {'status': 'error'} with status 400 for non-POST
            requests.
    """

    if request.method == 'POST':
        note_id = request.POST.get('note_id')
        x = request.POST.get('x')
        y = request.POST.get('y')
        note = get_object_or_404(Note, pk=note_id, user=request.user)
        note.x_position = x
        note.y_position = y
        note.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


def signup(request: HttpRequest) -> HttpResponse:
    """
    Handles user registration with automatic login and success messaging.
    Displays a signup form for GET requests using UserRegistrationForm. For
    POST requests, validates the form, creates a new user, logs them in, adds a
    success message, and redirects to the note list. If the form is invalid,
    displays it again with errors. Requires no authentication, intended for new
    users.

    Args:
        request (HttpRequest): The HTTP request object containing metadata,
            including method and POST data with signup details (username,
            email, passwords).

    Returns:
        HttpResponse: Renders 'registration/signup.html' with the form context
            for GET requests or invalid POST submissions. Redirects to
            'note_list' URL on successful POST registration.
    """

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('note_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/signup.html', {'form': form})


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Handles user login with authentication and feedback messaging.
    Displays a login form for GET requests using AuthenticationForm. For POST
    requests, validates credentials, logs the user in, adds a success message,
    and redirects to the note list on success. If invalid, adds an error
    message and displays again the form. Requires no authentication, intended
    for user login.

    Args:
        request (HttpRequest): The HTTP request object containing metadata,
            including method and POST data with login details (username,
            password).

    Returns:
        HttpResponse: Renders 'registration/login.html' with the form context
            for GET requests or invalid POST submissions. Redirects to
            'note_list' URL on successful POST login.
    """

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.info(request, f'You are now logged in as {user.username}')
            return redirect('note_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Handles user logout with confirmation messaging.
    Logs out the current user, adds a success message, and redirects to the
    login page. Does not check request method, as it is triggered by a POST
    form submission from the template. Requires no specific authentication
    state, but assumes a session exists to clear.

    Args:
        request (HttpRequest): The HTTP request object containing session data
            to be cleared during logout.

    Returns:
        HttpResponse: Redirects to the 'login' URL after logging out the user
            and adding a success message.
    """

    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('login')
