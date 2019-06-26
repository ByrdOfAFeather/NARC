from django.contrib import admin
from Main.models import APIKey

# Register your models here.
@admin.register(APIKey)
class UserAdmin(admin.ModelAdmin):
	model = APIKey

