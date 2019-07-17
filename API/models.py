from django.db import models


class Queuer(models.Model):
	unique_name = models.TextField(unique=True)
	currently_running = models.BooleanField(default=False)
