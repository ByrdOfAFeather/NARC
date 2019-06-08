from django.urls import path
from . import views

app_name = "main"
urlpatterns = [
	path("", view=views.index, name="index"),
	path("courses", view=views.courses, name="courses-view")
]
