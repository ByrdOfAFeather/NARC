from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class AuthorizedUser(models.Model):
	"""
	Taken from https://github.com/Harvard-University-iCommons/django-canvas-oauth/blob/831fd7c472351b8af1e34a4c7754d2348c1dd107/canvas_oauth/models.py#L8
	"""
	user = models.OneToOneField(
		User,
		on_delete=models.CASCADE,
		related_name='canvas_oauth2_token',
	)
	access_token = models.TextField()
	refresh_token = models.TextField()
	expires = models.DateTimeField()
	created_on = models.DateTimeField(auto_now_add=True)
	updated_on = models.DateTimeField(auto_now=True)
	url = models.URLField()

	def expires_within(self, delta):
		if not self.expires:
			return False

		return self.expires - timezone.now() <= delta


class Dataset(models.Model):
	data = models.TextField()
	date_created = models.DateTimeField(auto_now_add=True)


class UserToDataset(models.Model):
	user = models.ForeignKey(AuthorizedUser, on_delete=models.CASCADE)
	dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
