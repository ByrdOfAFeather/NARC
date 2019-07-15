from django.urls import path
from . import views

app_name = "canvaswrapper"
urlpatterns = [
	path("get_courses/", view=views.get_courses, name="courses-get"),
	path("get_modules/", view=views.get_modules, name="modules-get"),
	path("get_quizzes/", view=views.get_quizzes, name="quizzes-get"),
	path("get_quiz_info/<int:quiz_id>/", view=views.get_quiz_info, name="quiz-get-info"),
	path("get_quiz_stats/", view=views.get_quiz_stats, name="quiz-get-stats"),
	path("get_quiz_submissions/", view=views.get_quiz_submissions, name="quiz-get-submissions"),
	path("save_data/", view=views.save_data, name="save-data"),
	path("saved_data/", view=views.saved_data, name="saved-data"),
	path("delete_data/", view=views.delete_data, name="delete-local-data"),
	path("oauth_url/", view=views.set_oauth_url_cookie, name="oauth-url"),
	path("post_mobile/", view=views.mobile_endpoint, name="mobile-endpoint"),
]
