from django.contrib.auth.models import User
from django.db import models


class Queuer(models.Model):
	unique_name = models.TextField(unique=True)
	currently_running = models.BooleanField(default=False)


class Report(models.Model):
	report_desc = models.TextField()
	report_created = models.DateTimeField(auto_now_add=True)
	report_addressed = models.DateTimeField(null=True)


class UserToReport(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	report = models.ForeignKey(Report, on_delete=models.CASCADE)

