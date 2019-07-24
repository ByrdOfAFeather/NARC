from django.contrib import admin
from API.models import Queuer


@admin.register(Queuer)
class QueuerAdmin(admin.ModelAdmin):
	model = Queuer
