from django.contrib import admin

from API.models import Queuer, Report, UserToReport


@admin.register(Queuer)
class QueuerAdmin(admin.ModelAdmin):
	model = Queuer


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
	model = Report
	readonly_fields = ('report_created',)


@admin.register(UserToReport)
class UserToReportAdmin(admin.ModelAdmin):
	model = UserToReport


