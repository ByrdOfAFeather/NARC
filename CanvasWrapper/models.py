from django.db import models


class User(models.Model):
	hashed_name_id = models.CharField(max_length=65, unique=True)
	auth_token = models.CharField(max_length=65)


class Dataset(models.Model):
	data = models.TextField()
	date_created = models.DateTimeField(auto_now_add=True)


class UserToDataset(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)

