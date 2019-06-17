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
	return render(request, "module.html", {"course_id": course_id, "module_id": module_id})


def quiz(request, course_id, module_id, quiz_id):
	return render(request, "quiz.html", {"course_id": course_id, "module_id": module_id, "quiz_id": quiz_id})


def about(request):
	return render(request, "about.html")


def contact(request):
	return render(request, "contact.html")


def testing(request):
	return render(request, "model_training.html")

