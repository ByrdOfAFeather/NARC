from django.urls import path
from . import views

app_name = "mainpages"
urlpatterns = [
	path("", view=views.index, name="index"),
	path("courses/", view=views.courses, name="courses-view"),
	path("course/<int:course_id>/", view=views.course, name="course"),
	path("course/<int:course_id>/<int:module_id>/", view=views.module, name="module"),
	path("course/<int:course_id>/<int:module_id>/<int:quiz_id>", view=views.quiz, name="quiz"),
	path("about/", view=views.about, name="about"),
	path("contact/", view=views.contact, name="contact"),
	path("oauth_confirm/", view=views.oauth_authorization, name="oauth-authorization")

]
