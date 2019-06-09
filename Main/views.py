from django.shortcuts import render


def index(request):
	header = request.COOKIES.get("header", "")
	logged_in = True if header else False
	return render(request, "home.html", {"logged_in": logged_in})


def courses(request):
	return render(request, "courses.html")


def course(request, course_id):
	return render(request, "course.html", {"course_id": course_id})


def module(request, course_id, module_id):
	return render(request, "course.html", {"course_id": course_id})
