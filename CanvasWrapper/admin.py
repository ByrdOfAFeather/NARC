from django.contrib import admin
from CanvasWrapper.models import AuthorizedUser, Dataset, UserToDataset

# Register your models here.
@admin.register(AuthorizedUser)
class UserAdmin(admin.ModelAdmin):
	model = AuthorizedUser


@admin.register(Dataset)
class DataSetAdmin(admin.ModelAdmin):
	model = Dataset


@admin.register(UserToDataset)
class UserToDatasetAdmin(admin.ModelAdmin):
	model = UserToDataset
