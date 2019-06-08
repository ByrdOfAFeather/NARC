from django.urls import path
from . import views

app_name = "mainpages"
urlpatterns = [
	path("", view=views.index, name="index"),
	path("courses", view=views.courses, name="courses-view"),
	path("course/<int:course_id>/", view=views.course, name="course"),
]
