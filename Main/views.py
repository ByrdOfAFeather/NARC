from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from Main.models import APIKey
from CanvasWrapper.models import User
import requests
import hashlib


def index(request):
	return render(request, "home.html")


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


def get_client_id(url):
	key = APIKey.objects.filter(url=url)
	if key:
		return key
	else:
		return None


def oauth_authorization(request):
	url = request.session.get("url", False)
	if not url:
		return render(request, "home.html", {"error": "Could not find the URL! Are you sure you provided one?"})

	client = get_client_id(url)
	if not client:
		return render(request, "home.html", {"error": "We do not support this version of Canvas!"})
	client_id = client.client_id

	code = request.GET.get("code", "")
	if not request.GET.get("error", "") and code:
		state = request.GET.get("state", "")
		if state == client.state:
			final_code = requests.post(f"https://{url}/login/oauth2/token", {
				"grant_type": "authorization_code",
				"client_id": client_id,
				"client_secret": client.client_secret,
				"redirect_uri": "http://127.0.0.1:8000/oauth_confirm",
				"code": code,
				}, verify=False  # TODO: Remeber to make this True in production!
			)
			if final_code.status_code != 200:
				return render(request, "home.html", {"error": "There was a problem authorizing your request."})

			response = final_code.json()
			User.objects.create(
				hashed_name_id=hashlib.sha3_256(f"{response['user']['name']} {response['user']['id']}"),
				auth_token=response["access_token"]
			)
			request.session["header"] = str({"Authorization": f"Bearer {response['access_token']}"})
			request.session["refresh_token"] = str({response['refresh_token']})
			return render(request, "courses.html")
	else:
		return render(request, "home.html", {"error": "There was a problem authorizing your request."})

	return HttpResponseRedirect(f"https://{url}/login/oauth2/auth?client_id={client_id}&response_type=code&state={client.state}&redirect_uri=http://127.0.0.1:8000/oauth_confirm")
