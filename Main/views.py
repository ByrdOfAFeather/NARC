from django.shortcuts import render
from django.http import HttpResponse


def index(request):
	header = request.COOKIES.get("header", "")
	logged_in = True if header else False
	return render(request, "home.html", {"logged_in": logged_in})


def courses(request):
	header = request.COOKIES.get('header')
	return render(request, "courses.html", {"header": header})
