from django.test import TestCase, Client, SimpleTestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from .models import Note
from .forms import NoteForm, UserRegistrationForm
from .views import (
    note_list,
    note_create,
    note_update,
    note_delete,
    update_position,
    signup,
    login_view,
    logout_view
)


class NoteModelTest(TestCase):
    """
    Tests the functionality of the Note model in the sticky notes application.
    Verifies that the Note model correctly creates instances, applies default
    values, and provides an appropriate string representation. Uses Django's
    TestCase to simulate database interactions with a test user.

    Attributes:
        user (User): A test User instance created in setUp, used as the owner
            of all test notes.

    Methods:
        setUp: Prepares a test user before each test method.
        test_note_creation: Tests full note creation with all fields.
        test_note_str: Tests the __str__ method of the Note model.
        test_default_values: Tests application of default field values.
    """

    def setUp(self):
        """
        Sets up test data by creating a test user.
        Creates a User instance that will be associated with all test Note
        instances, ensuring consistent ownership across tests.
        """

        self.user = User.objects.create_user(
            username='user_3',
            password='asdf8520'
        )

    def test_note_creation(self):
        """
        Tests creating a Note instance with all fields specified.
        Creates a Note with explicit values for title, content, user, color,
        and position coordinates, then verifies that all attributes are saved
        correctly, including auto-generated timestamps.
        """

        note = Note.objects.create(
            title='Test Note Title',
            content='This is a test note',
            user=self.user,
            color='#FF0000',
            x_position=10,
            y_position=20
        )
        self.assertEqual(note.title, 'Test Note Title')
        self.assertEqual(note.content, 'This is a test note')
        self.assertEqual(note.user, self.user)
        self.assertEqual(note.color, '#FF0000')
        self.assertEqual(note.x_position, 10)
        self.assertEqual(note.y_position, 20)
        self.assertTrue(note.created_at)
        self.assertTrue(note.updated_at)

    def test_note_str(self):
        """
        Tests the __str__ method of the Note model.
        Creates a minimal Note instance and checks that its string
        representation matches its title, as defined in the model's __str__
        method.
        """

        note = Note.objects.create(title='Test Note Title', user=self.user)
        self.assertEqual(str(note), 'Test Note Title')

    def test_default_values(self):
        """
        Tests that default values are applied to optional Note fields.
        Creates a Note with only required fields (title and user), then
        verifies that color, x_position, and y_position use their default
        values as defined in the model.
        """

        note = Note.objects.create(title='Default Note', user=self.user)
        self.assertEqual(note.color, '#FFD700')     # Default gold color
        self.assertEqual(note.x_position, 0)
        self.assertEqual(note.y_position, 0)


class NoteFormTest(TestCase):
    """
    Tests the validation behavior of the NoteForm in the sticky notes app.
    Ensures that the NoteForm correctly validates data for creating or editing
    Note instances, accepting valid data and rejecting invalid data such as
    overly long titles. Uses Django's TestCase for form validation testing.

    Methods:
        test_note_form_valid: Tests validation with fully valid form data.
        test_note_form_invalid: Tests validation with an invalid title length.
    """

    def test_note_form_valid(self):
        """
        Tests valid form data for NoteForm.
        Provides a complete set of valid data for all NoteForm fields and
        verifies that the form validates successfully.
        """

        form_data = {
            'title': 'Test Note',
            'content': 'Test content',
            'color': '#FF0000',
            'x_position': 10,
            'y_position': 20
        }
        form = NoteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_note_form_invalid(self):
        """
        Tests invalid form data with a title exceeding max length.
        Supplies form data where the title is too long (over 100 characters)
        and checks that the form correctly fails validation.
        """

        form_data = {
            'title': 'x' * 101,  # Exceeds max_length of 100
            'content': 'Test content',
            'color': '#FF0000',
            'x_position': 0,
            'y_position': 0
        }
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())


class UserRegistrationFormTest(TestCase):
    """
    Tests the validation behavior of the UserRegistrationForm.
    Verifies that the UserRegistrationForm, used for registering new users,
    accepts valid registration data and rejects invalid data such as bad
    emails or mismatched passwords. Uses Django's TestCase for testing.

    Methods:
        test_user_registration_form_valid: Tests validation with valid data.
        test_user_registration_form_invalid_email: Tests with an invalid email.
        test_user_registration_form_password_mismatch: Tests with mismatched
            passwords.
    """

    def test_user_registration_form_valid(self):
        """
        Tests valid registration data for UserRegistrationForm.
        Provides a complete set of valid user registration data, including
        matching passwords and a proper email, and checks that the form
        validates successfully.
        """

        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_registration_form_invalid_email(self):
        """
        Tests invalid email in UserRegistrationForm data.
        Supplies form data with an improperly formatted email address and
        verifies that the form fails validation.
        """

        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_registration_form_password_mismatch(self):
        """
        Tests password mismatch in UserRegistrationForm data.
        Provides form data where the two password fields do not match and
        checks that the form correctly fails validation.
        """

        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())


class NoteViewsTest(TestCase):
    """
    Tests the views of the sticky notes application.
    Verifies the behavior of views for listing, creating, updating, deleting,
    and positioning notes, as well as user signup, login, and logout
    functionality. Uses Django's TestCase and Client to simulate HTTP requests
    and database interactions with a test user and note.

    Attributes:
        client (Client): A Django test client instance for simulating HTTP
            requests.
        user (User): A test User instance created in setUp, used for
            authentication.
        note (Note): A test Note instance created in setUp, owned by the test
            user.

    Methods:
        setUp: Prepares test client, user, and note before each test.
        test_note_list_view_authenticated: Tests note list view when logged in.
        test_note_list_view_unauthenticated: Tests redirect when not logged in.
        test_note_create_view: Tests creating a note.
        test_note_update_view: Tests updating a note.
        test_note_delete_view: Tests deleting a note.
        test_update_position_view: Tests updating note position via AJAX.
        test_signup_view: Tests user signup.
        test_login_view: Tests login.
        test_logout_view: Tests logout.
    """

    def setUp(self):
        """
        Sets up test data by creating a client, user, and note.
        Initializes a test client for HTTP requests, a test user for
        authentication, and a test note owned by the user, providing a
        consistent starting point for all tests.
        """

        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        self.note = Note.objects.create(
            title='Test Note',
            content='Test content',
            user=self.user
        )

    def test_note_list_view_authenticated(self):
        """
        Tests note list view when logged in.
        Logs in the test user and requests the note list, verifying a
        successful response, correct template usage, and presence of the test
        note's title.
        """

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sticky_notes_app/note_list.html')
        self.assertContains(response, 'Test Note')

    def test_note_list_view_unauthenticated(self):
        """
        Tests redirect to login when not authenticated.
        Requests the note list without logging in and checks that it redirects
        to the login page with the appropriate 'next' parameter.
        """

        response = self.client.get(reverse('note_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/?next=/')

    def test_note_create_view(self):
        """
        Tests creating a note.
        Logs in the test user, submits a POST request with new note data, and
        verifies a redirect to the note list and the note's existence in the
        database.
        """

        self.client.login(username='testuser', password='12345')
        form_data = {
            'title': 'New Note',
            'content': 'New content',
            'color': '#FF0000',
            'x_position': 50,
            'y_position': 60
        }
        response = self.client.post(reverse('note_create'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('note_list'))
        self.assertTrue(Note.objects.filter(title='New Note').exists())

    def test_note_update_view(self):
        """
        Tests updating a note.
        Logs in the test user, submits a POST request with updated note data,
        and checks for a redirect and that the note's title is updated in the
        database.
        """

        self.client.login(username='testuser', password='12345')
        form_data = {
            'title': 'Updated Note',
            'content': 'Updated content',
            'color': '#00FF00',
            'x_position': self.note.x_position,
            'y_position': self.note.y_position
        }
        response = self.client.post(
            reverse('note_update', args=[self.note.pk]), form_data
        )
        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Note')

    def test_note_delete_view(self):
        """
        Tests deleting a note.
        Logs in the test user, submits a POST request to delete the test note,
        and verifies a redirect and that the note no longer exists in the
        database.
        """

        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('note_delete', args=[self.note.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_update_position_view(self):
        """
        Tests updating note position via AJAX.
        Logs in the test user, submits a POST request with new position data,
        and checks for a successful response and updated position values in
        the database.
        """

        self.client.login(username='testuser', password='12345')
        data = {
            'note_id': self.note.pk,
            'x': 100,
            'y': 200
        }
        response = self.client.post(reverse('update_position'), data)
        self.assertEqual(response.status_code, 200)
        self.note.refresh_from_db()
        self.assertEqual(self.note.x_position, 100)
        self.assertEqual(self.note.y_position, 200)

    def test_signup_view(self):
        """Tests user signup.
        Submits a POST request with new user data and verifies a redirect and
        that the new user exists in the database.
        """

        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(reverse('signup'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view(self):
        """
        Tests login.
        Submits a POST request with test user credentials and checks for a
        redirect to the note list.
        """

        form_data = {
            'username': 'testuser',
            'password': '12345'
        }
        response = self.client.post(reverse('login'), form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('note_list'))

    def test_logout_view(self):
        """
        Tests logout.
        Logs in the test user, sends a GET request to logout, and verifies a
        redirect to the login page.
        """

        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class UrlTest(SimpleTestCase):
    """
    Tests the URL patterns of the sticky notes application.
    Verifies that each URL name in the application's URL configuration resolves
    to the correct view function, ensuring proper routing. Uses Django's
    SimpleTestCase for lightweight testing without database setup.

    Methods:
        test_note_list_url: Tests the 'note_list' URL resolution.
        test_note_create_url: Tests the 'note_create' URL resolution.
        test_note_update_url: Tests the 'note_update' URL resolution with a pk.
        test_note_delete_url: Tests the 'note_delete' URL resolution with a pk.
        test_update_position_url: Tests the 'update_position' URL resolution.
        test_signup_url: Tests the 'signup' URL resolution.
        test_login_url: Tests the 'login' URL resolution.
        test_logout_url: Tests the 'logout' URL resolution.
    """

    def test_note_list_url(self):
        """
        Tests the resolution of the 'note_list' URL.
        Generates the URL for 'note_list' and verifies that it resolves to the
        note_list view function.
        """

        url = reverse('note_list')
        self.assertEqual(resolve(url).func, note_list)

    def test_note_create_url(self):
        """
        Tests the resolution of the 'note_create' URL.
        Generates the URL for 'note_create' and checks that it resolves to the
        note_create view function.
        """

        url = reverse('note_create')
        self.assertEqual(resolve(url).func, note_create)

    def test_note_update_url(self):
        """
        Tests the resolution of the 'note_update' URL with a primary key.
        Generates the URL for 'note_update' with a sample pk and verifies that
        it resolves to the note_update view function.
        """

        url = reverse('note_update', args=[1])
        self.assertEqual(resolve(url).func, note_update)

    def test_note_delete_url(self):
        """
        Tests the resolution of the 'note_delete' URL with a primary key.
        Generates the URL for 'note_delete' with a sample pk and checks that it
        resolves to the note_delete view function.
        """

        url = reverse('note_delete', args=[1])
        self.assertEqual(resolve(url).func, note_delete)

    def test_update_position_url(self):
        """
        Tests the resolution of the 'update_position' URL.
        Generates the URL for 'update_position' and verifies that it resolves
        to the update_position view function.
        """

        url = reverse('update_position')
        self.assertEqual(resolve(url).func, update_position)

    def test_signup_url(self):
        """
        Tests the resolution of the 'signup' URL.
        Generates the URL for 'signup' and checks that it resolves to the
        signup view function.
        """

        url = reverse('signup')
        self.assertEqual(resolve(url).func, signup)

    def test_login_url(self):
        """
        Tests the resolution of the 'login' URL.
        Generates the URL for 'login' and verifies that it resolves to the
        login_view function.
        """

        url = reverse('login')
        self.assertEqual(resolve(url).func, login_view)

    def test_logout_url(self):
        """
        Tests the resolution of the 'logout' URL.
        Generates the URL for 'logout' and checks that it resolves to the
        logout_view function.
        """

        url = reverse('logout')
        self.assertEqual(resolve(url).func, logout_view)
