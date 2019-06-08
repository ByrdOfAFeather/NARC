from django.urls import path
from . import views

app_name = "canvaswrapper"
urlpatterns = [
	path("testtoken", view=views.test_token, name="test-token"),
	path("getcourses", view=views.get_courses, name="courses-get")
]
