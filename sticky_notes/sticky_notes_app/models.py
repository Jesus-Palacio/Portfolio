from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    """
    Represents a sticky note associated with a user. Stores information about
    a sticky note including its title, content, timestamps, user ownership,
    color, and position coordinates. Used in the sticky note application where
    users can create, view, edit, organize and delete notes.

    Attributes:
        title (CharField): The note's title, max length 100 characters.
        content (TextField): The main content of the note.
        created_at (DateTimeField): Timestamp of note creation, auto-set on
            creation.
        updated_at (DateTimeField): Timestamp of last update, auto-updated on
            save.
        user (ForeignKey): Reference to the User who owns the note, cascades
            on delete.
        color (CharField): Hex color code for the note, max length 7, defaults
            to Gold color ('#FFD700').
        x_position (IntegerField): X-coordinate for note position, defaults
            to 0.
        y_position (IntegerField): Y-coordinate for note position, defaults
            to 0.

    Methods:
        __str__: Returns the note's title as its string representation.
    """

    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=7, default="#FFD700")
    x_position = models.IntegerField(default=0)
    y_position = models.IntegerField(default=0)

    def __str__(self):
        """
        Returns the note's title as its string representation.

        Returns:
            str: Note's title
        """

        return self.title
