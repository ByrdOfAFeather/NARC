import requests
import json
from django.shortcuts import render
from django.http import JsonResponse


def test_token(request):
	token = request.GET.get("token", "")
	if token:
		header = {"Authorization": "Bearer {}".format(token)}
		test = requests.get("http://canvas.instructure.com/api/v1/courses",
		                    headers=header)
		if test.status_code == 200:
			response = JsonResponse({"success": "Token Test Succeeded!"})
			response.status_code = 200
			response.set_cookie("header", header)
			return response
		else:
			response = JsonResponse({"error": "Provided token is not valid!"})
			response.status_code = 401
			return response


def content_helper(request):
	if request.status_code == 200:
		response = JsonResponse({"success": {"data": str(request.content)}})
		response.status_code = 200
		return response
	else:
		response = JsonResponse({"error": "unknown error occured! (Maybe token expired?)"})
		response.status_code = request.status_code
		return response


def get_courses(request):
	header = request.COOKIES.get("header", "")
	url = request.COOKIES.get("url", "canvas.instructure.com")
	if header:
		header = header.replace("'", "\"")
		header = json.loads(header)
		courses = requests.get(
			"https://{}/api/v1/courses?per_page=50".format(url),
			headers=header)

		return content_helper(courses)

	else:
		response = JsonResponse({"error": "could not find cookie"})
		response.status_code = 401
		return response


def get_modules(request):
	header = request.COOKIES.get("header", "")
	url = request.COOKIES.get("url", "canvas.instructure.com")
	course_id = request.GET.get("course_id")
	if header:
		header = header.replace("'", "\"")
		header = json.loads(header)

		modules = requests.get(
			"https://{}/api/v1/courses/{}/modules?per_page=50".format(url, course_id),
			headers=header)

		return content_helper(modules)

	else:
		response = JsonResponse({"error": "could not find cookie"})
		response.status_code = 401
		return response
