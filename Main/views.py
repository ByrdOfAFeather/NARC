from django.shortcuts import render
from django.http.response import HttpResponseRedirect
import requests


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


def testing(request):
	return render(request, "model_training.html")


def get_client_id(url):
	# TODO: Implement getting client id based on URL
	return 10000000000003


def oauth_authorization(request):
	url = request.session["url"]
	if not url:
		# TODO: Implement error feature in home page
		return render(request, "home.html", {"error": True})

	client_id = get_client_id(url)
	if not client_id:
		# TODO: Implement error feature in home page
		return render(request, "home.html", {"error": True})

	code = request.GET.get("code", "")
	if not request.GET.get("error", "") and code:
		print(code)
		state = request.GET.get("state", "")
		print(state)
		# TODO: Make State secret & Error Condition
		if state == "NAMB":
			final_code = requests.post("https://192.168.1.240/login/oauth2/token", {
				"grant_type": "authorization_code",
				"client_id": 3,
				"client_secret": "IaKqi1heupkW4Cxv8AjhcaxycpkAtQDl4QySgwy5jviJs6BJ7k3UgrFRL3TqLMKN",
				"redirect_uri": "http://127.0.0.1:8000/oauth_confirm",
				"code": code,
				}, verify=False  # TODO: Remeber to make this True in production!
			)
			response = final_code.json()

			request.session["header"] = str({"Authorization": f"Bearer {response['access_token']}"})
			request.session["refresh_token"] = str({response['refresh_token']})
			return render(request, "courses.html")

	return HttpResponseRedirect(f"https://{url}/login/oauth2/auth?client_id={client_id}&response_type=code&state=NAMB&redirect_uri=http://127.0.0.1:8000/oauth_confirm")