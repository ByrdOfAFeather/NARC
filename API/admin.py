from django.contrib import admin
from API.models import NotificationToken

# Register your models here.
@admin.register(NotificationToken)
class NotificationTokenAdmin(admin.ModelAdmin):
	model = NotificationToken
