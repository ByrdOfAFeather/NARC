from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from CanvasWrapper.models import AuthorizedUser
from Main.models import APIKey
from datetime import timedelta
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
	key = APIKey.objects.filter(url=url)[0]
	if key:
		return key
	else:
		return None


def oauth_authorization(request):
	url = request.COOKIES.get("url", False)
	if not url:
		return render(request, "home.html", {"error": "Could not find the URL! Are you sure you provided one?"})

	client = get_client_id(url)
	if not client:
		return render(request, "home.html", {"error": "We do not support this version of Canvas!"})

	if request.GET.get("error", ""):
		return render(request, "home.html", {"error": "There was a problem authorizing with canvas."})

	code = request.GET.get("code", "")
	if code:
		state = request.GET.get("state", "")
		if state == client.state:
			final_code = requests.post(f"https://{url}/login/oauth2/token", {
				"grant_type": "authorization_code",
				"client_id": client.client_id,
				"client_secret": client.client_secret,
				"redirect_uri": "http://127.0.0.1:8000/oauth_confirm",
				"code": code,
				}, verify=False  # TODO: Remember to make this True in production!
			)
			print(final_code.content)
			if final_code.status_code != 200:
				print("This is the issue")
				return render(request, "home.html", {"error": "There was a problem authorizing your request."})

			response = final_code.json()

			username = hashlib.sha3_256((str(response['user']['id']) + url).encode("utf-8")).hexdigest()
			if User.objects.filter(username=username):
				return render(request, "home.html", {"error:": "user already logged in!"})

			new_user = User.objects.create_user(
				username=username,
				password=response["refresh_token"]
			)

			AuthorizedUser.objects.create(
				user=new_user,
				access_token=response["access_token"],
				refresh_token=response["refresh_token"],
				expires=timezone.now() + timedelta(seconds=response["expires_in"]),
			)

			user = authenticate(request, username=username, password=response["refresh_token"])
			login(request, user)
			return render(request, "courses.html")
	else:
		return HttpResponseRedirect(f"https://{url}/login/oauth2/auth?client_id={client.client_id}&response_type=code&state={client.state}&redirect_uri=http://127.0.0.1:8000/oauth_confirm")

