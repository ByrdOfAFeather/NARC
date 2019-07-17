from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)


class APIKey(models.Model):
	url = models.CharField(max_length=65, unique=True)
	client_id = models.CharField(max_length=15)
	client_secret = models.CharField(max_length=65)
	state = models.CharField(max_length=10)
	dev = models.BooleanField(default=False)
