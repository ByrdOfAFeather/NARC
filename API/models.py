from django.db import models
from django.contrib.auth.models import User


class NotificationToken(models.Model):
	user = models.OneToOneField(User,
	                            on_delete=models.CASCADE,
	                            related_name="notification_target")
	notification_key = models.TextField()


class Queuer(models.Model):
	unique_name = models.TextField(unique=True)
	currently_running = models.BooleanField(default=False)
