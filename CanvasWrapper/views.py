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


def get_courses(request):
	header = request.COOKIES.get("header", "")
	if header:
		header = header.replace("'", "\"")
		header = json.loads(header)
		courses = requests.get("http://canvas.instructure.com/api/v1/courses",
		                       headers=header)
		if courses.status_code == 200:
			response = JsonResponse({"success": {"data": str(courses.content)}})
			response.status_code = 200
			return response
		else:
			response = JsonResponse({"error": "unknown error occured! (Maybe token expired?)"})
			response.status_code = courses.status_code
			return response
	else:
		response = JsonResponse({"error": "could not find cookie"})
		response.status_code = 401
		return response