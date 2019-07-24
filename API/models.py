from django.db import models
from django.contrib.auth.models import User


class Queuer(models.Model):
	unique_name = models.TextField(unique=True)
	currently_running = models.BooleanField(default=False)
