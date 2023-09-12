from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator

from PIL import Image

from datetime import date


class User(AbstractUser):
    """user model"""

    WIDTH = 200

    # related names added to avoid conflicts with auth.User.groups and auth.User.user_permissions
    groups = models.ManyToManyField(Group, related_name="custom_user_set")
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_set"
    )

    birthdate = models.DateField(
        verbose_name="Date de naissance", null=True, blank=True
    )
    can_be_contacted = models.BooleanField(null=True, blank=True)
    # can_data_be_shared is True only if age > 15
    can_data_be_shared = models.BooleanField(null=True, blank=True)
    image = models.ImageField(verbose_name="Photo de profil", blank=True, null=True)

    def __str__(self):
        return f"{str(self.username).capitalize()}"

    def resize_image(self):
        """Resize the image while maintaining the original height/width aspect ratio
        width == 200px"""

        if self.image:
            image = Image.open(self.image)

            # get the original height/width aspect ratio
            width, height = image.size

            # get the new height/width aspect ratio
            new_width = self.WIDTH
            new_height = int(height * (new_width / width))

            # resize the image
            image = image.resize((new_width, new_height), Image.LANCZOS)

            # Save
            image.save(self.image.path)

    def age(self) -> int:
        """return the user age"""
        today = date.today()
        age = (
            today.year
            - self.birthdate.year
            - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
        )

        return age

    def save(self, *args, **kwargs):
        """Override the save method with the resize_image"""

        super().save(*args, **kwargs)
        self.resize_image()