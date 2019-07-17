"""Views representing the main front end of the website
"""
# TODO: COPPA Compliance is best achieved by asking a user if the dataset contains users below or at the age of 13
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils import timezone
from CanvasWrapper.models import AuthorizedUser
from CanvasWrapper.views import get_dev_key
from datetime import timedelta
import requests
import hashlib


def index(request: HttpRequest) -> HttpResponse:
	return render(request, "home.html")


def courses(request: HttpRequest) -> HttpResponse:
	return render(request, "courses.html")


def course(request: HttpRequest, course_id: int) -> HttpResponse:
	return render(request, "course.html", {"course_id": course_id})


def module(request: HttpRequest, course_id: int, module_id: int) -> HttpResponse:
	return render(request, "module.html", {"course_id": course_id, "module_id": module_id})


def quiz(request: HttpRequest, course_id: int, module_id: int, quiz_id: int) -> HttpResponse:
	return render(request, "quiz.html", {"course_id": course_id, "module_id": module_id, "quiz_id": quiz_id})


def about(request: HttpRequest) -> HttpResponse:
	return render(request, "about.html")


def contact(request: HttpRequest) -> HttpResponse:
	return render(request, "contact.html")


def oauth_authorization(request: HttpRequest) -> HttpResponse:
	"""
	:param request: Request provided by Canvas redirect or by Django
	:return: A redirect to the courses page or a error message on the home page
	"""
	url = request.COOKIES.get("url", False)
	if not url:  # A URL somehow didn't make it into the cookie
		return render(request, "home.html", {"error": "Could not find the URL! Are you sure you provided one?"})

	client = get_dev_key(f"https://{url}")
	if not client:  # The development key is not supported
		return render(request, "home.html", {"error": "We do not support this version of Canvas!"})

	if request.GET.get("error", ""):  # There was some sort of issue authorizing with Canvas
		return render(request, "home.html", {"error": "There was a problem authorizing with canvas."})

	code = request.GET.get("code", "")
	if code:
		state = request.GET.get("state", "")
		if state == client.state:
			final_code = requests.post(f"https://{url}/login/oauth2/token", {  # Post to get the token
				"grant_type": "authorization_code",
				"client_id": client.client_id,
				"client_secret": client.client_secret,
				# TODO: CHANGE!!!!!
				"redirect_uri": "http://127.0.0.1:8000/oauth_confirm",
				"code": code,
				}, verify=False is client.dev
			)
			if final_code.status_code != 200:  # Error with the request to canvas (possibly a broken dev key)
				return render(request, "home.html", {"error": "There was a problem authorizing your request."})

			response = final_code.json()

			# The username is saved as the id and url hashed together, this is due to user ID only being unique per url
			username = hashlib.sha3_256((str(response['user']['id']) + url).encode("utf-8")).hexdigest()
			test_user = User.objects.filter(username=username)
			if test_user:
				# Automatically logs the user in if they are already detected in the database
				oauth = AuthorizedUser.objects.get(user=test_user[0])
				oauth.access_token = response["access_token"]
				oauth.refresh_token = response["refresh_token"]
				oauth.expires = timezone.now() + timedelta(seconds=response["expires_in"])
				oauth.save()
				user = authenticate(request, username=username, password=username)
				login(request, user)
				return HttpResponseRedirect(request.build_absolute_uri("/courses/"))

			# TODO: This needs to change to accommodate for the mobile app.
			# This takes some explaining. The user model is simply so that Django knows how to link up everything
			# there's no way to actually login to this from the user's perspective, only in this particular view.
			# The url & id allow us to have a unique key and also serve as the password, since the password is required.
			# Bonus: since the urls have to exist in the database for the canvas installation, there's no way to cheese
			# this request and login, even if you know the user's id and password!
			new_user = User.objects.create_user(  # Create a user based on hashed username
				username=username,
				password=username
			)

			AuthorizedUser.objects.create(  # Create a oauth token based on retrieved information
				user=new_user,
				access_token=response["access_token"],
				refresh_token=response["refresh_token"],
				expires=timezone.now() + timedelta(seconds=response["expires_in"]),
				url=f"https://{url}"
			)

			user = authenticate(request, username=username, password=username)
			login(request, user)
			return render(request, "courses.html")
	else:
		# TODO: Changed URL!!!
		return HttpResponseRedirect(f"https://{url}/login/oauth2/auth?client_id={client.client_id}&response_type=code&state={client.state}&redirect_uri=http://127.0.0.1:8000/oauth_confirm")

