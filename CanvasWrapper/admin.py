from django.contrib import admin
from CanvasWrapper.models import User, Dataset, UserToDataset

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	model = User


@admin.register(Dataset)
class DataSetAdmin(admin.ModelAdmin):
	model = Dataset


@admin.register(UserToDataset)
class UserToDatasetAdmin(admin.ModelAdmin):
	model = UserToDataset
