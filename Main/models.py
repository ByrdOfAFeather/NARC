from django.db import models


class APIKey(models.Model):
	url = models.CharField(max_length=65, unique=True)
	client_id = models.CharField(max_length=15)
	client_secret = models.CharField(max_length=65)
	state = models.CharField(max_length=10)
