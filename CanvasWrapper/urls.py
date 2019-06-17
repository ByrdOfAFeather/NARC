from django.urls import path
from . import views

app_name = "canvaswrapper"
urlpatterns = [
	path("testtoken", view=views.test_token, name="test-token"),
	path("getcourses", view=views.get_courses, name="courses-get"),
	path("getmodules", view=views.get_modules, name="modules-get"),
	path("getquizzes", view=views.get_quizzes, name="quizzes-get"),
	path("getquizinfo/<int:quiz_id>", view=views.get_quiz_info, name="quiz-get-info"),
	path("getquizstats", view=views.get_quiz_stats, name="quiz-get-stats"),
	path("getquizsubmissions", view=views.get_quiz_submissions, name="quiz-get-submissions"),
	path("allowsavedata", view=views.save_data, name="allow-save"),
	path("denysavedata", view=views.deny_save_data, name="deny-save"),
]
