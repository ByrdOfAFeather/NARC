"""
Container for view functions related to retrieving data from the Canvas API as well as processing & saving data on the
server
"""

import json
import requests
import random as rand
from django.views.decorators.http import require_GET, require_POST
from django.http import QueryDict
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from Main.models import APIKey
from CanvasWrapper.models import Dataset, UserToDataset
from math import floor
from datetime import timedelta
from typing import Optional


def test_token(token: str, url: str, dev: bool) -> bool:
	"""Tests the OAuth2 token currently stored for the active user.
	:param token: Token for the current user
	:param url: The URL for the canvas installation of the current user
	:param dev: If the developer token provided to NARC is on a secure server or unsecured
	:return: If the request returned a positive result
	"""
	simple_request = requests.get(f"https://{url}/api/v1/courses", headers={"Authorization": f"Bearer {token}"},
	                              verify=False is dev)
	return simple_request.status_code == 200


def content_helper(response: requests.models.Response) -> JsonResponse:
	"""A simple helper function for similar Canvas LMS requests to process the data based on the status code
	:param response: The response from a call to the canvas API
	:return: A Django JsonResponse, either providing a generic error or a success with the data associated
	"""
	if response.status_code == 200:  # Checks the status of the response
		response = JsonResponse({"success": {"data": json.dumps(response.json())}})  # Returns the data in a standard format
		response.status_code = 200  # Mimics the original status code
		return response
	else:
		response = JsonResponse({"error": "unknown error occurred! (Maybe token expired?)"})  # Returns a generic error
		response.status_code = response.status_code  # mimics status code
		return response


def error_generator(error: str, error_code: int) -> JsonResponse:
	"""A simple helper function to build non-generic error responses
	:param error: A short message describing the error
	:param error_code: The code for the error
	:return: A response containing the code and error
	"""
	response = JsonResponse({"error": error})
	response.status_code = error_code
	return response


def get_dev_key(url: str) -> Optional[APIKey]:
	"""Gets the dev key based on the url provided
	:param url: The url for the canvas installation the user is trying to login from
	:return: Either an object representing the APIKey or none if we do not have a developer key yet
	"""
	key = APIKey.objects.filter(url=url)
	if key:
		return key[0]
	else:
		return None


def expire_checker(request: HttpRequest) -> tuple:
	"""Checks if a users token is expired before sending a request to the canvas API
	:param request: The current request as provided by django
	:return: A tuple containing either None, Client (being the APIKey) if successful or
	JsonResponse, None if unrecoverable error
	"""
	if not request.user.is_authenticated:  # Checks if the user is already logged in and if not returns an error
		return error_generator("You aren't logged in!", 401), None

	url = request.user.canvas_oauth2_token.url  # Gets the url from the user's associated oauth2 token

	client = get_dev_key(url)  # Gets the canvas dev key associated with the provided url
	if not client:
		return error_generator("We do not support this version of Canvas!", 401), None  # Developer key can't be found

	if request.user.canvas_oauth2_token.expires_within(timedelta(seconds=60)):  # If expiration in a minute
		new_token = requests.post(f"{url}/login/oauth2/token", {  # Builds a post request to get a new token
			"grant_type": "refresh_token",
			"client_id": client.client_id,
			"client_secret": client.client_secret,
			# TODO: Change this!!!!!!!!!!!!!!!!!!
			"redirect_uri": "http://127.0.0.1:8000/oauth_confirm",
			"refresh_token": request.user.canvas_oauth2_token.refresh_token,
		}, verify=False is client.dev)
		if new_token.status_code == 200:  # If the token is validated
			# Save the token to the database
			new_token_data = new_token.json()
			request.user.canvas_oauth2_token.access_token = new_token_data["access_token"]
			request.user.canvas_oauth2_token.expires = timezone.now() + timedelta(seconds=new_token_data["expires_in"])
			request.user.canvas_oauth2_token.save()
			return None, client
		else:
			return error_generator("Error getting new token! Please login again!", 401), None  # Error getting token
	else: return None, client


def get_courses(request: HttpRequest) -> JsonResponse:
	"""Gets a list of courses from the Canvas API based on current user
	:param request: The current request as provided by django
	:return: A JSONResponse containing either an error or the data provided by Canvas
	"""
	error = expire_checker(request)  # First check if the token is going to expire soon
	url = request.user.canvas_oauth2_token.url  # Get the URL from the oauth2 object associated with user
	if error[0] is not None:  # checks if the expire check had a non-null value in the first position
		return error[0]
	client = error[1]  # if not then the second position should contain the APIKey
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}  # Creates header
	courses = requests.get(
		"{}/api/v1/courses?per_page=50".format(url),
		headers=header, verify=False is client.dev)
	return content_helper(courses)  # returns from the generic helper (see content_helper)


@require_GET
def get_modules(request: HttpRequest) -> JsonResponse:
	"""Gets a list of modules for the provided course from the Canvas API based on current user
	A module ID has to be provided in order to access the correct course
	:param request: The current request as provided by django
	:return: A JSONResponse containing either an error or the data provided by Canvas
	"""
	# Note: For functionality documentation, see get_courses, as much of it is the same
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id", "")

	if not course_id: return error_generator("There was no provided course ID!", 404) # Returns without module ID

	modules = requests.get(
		"{}/api/v1/courses/{}/modules?per_page=50".format(url, course_id),
		headers=header, verify=False is client.dev)
	return content_helper(modules)


@require_GET
def get_quizzes(request: HttpRequest) -> JsonResponse:
	"""Returns a list of quizzes inside of a provided module
	A course ID and module ID have to be provided in order to find the module properly.
	:param request: The current request as provided by django
	:return: A JSONResponse containing either an error or the data provided by Canvas
	"""
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id", "")
	module_id = request.GET.get("module_id", "")

	if not course_id: return error_generator("No Course ID was provided!", 404)
	if not module_id: return error_generator("No Module ID was provided!", 404)

	quizzes = requests.get(
		"{}/api/v1/courses/{}/modules/{}/items".format(url, course_id, module_id),
		headers=header, verify=False is client.dev)
	if quizzes.status_code == 200:
		quizzes = [
			{"name": items["title"], "id": items["content_id"]}
			for items in quizzes.json() if items['type'] == "Quiz"
		]
		response = JsonResponse({"success": {"data": str(quizzes)}})
		response.status_code = 200
		return response

	else:
		response = JsonResponse({"error": "unknown error occurred! (Maybe token expired?)"})
		response.status_code = quizzes.status_code
		return response


@require_GET
def get_quiz_info(request, quiz_id):
	"""Retrieves basic information about a quiz
	:param request: The current request as provided by django
	:param quiz_id: The ID for the quiz
	:return: A JSONResponse containing either an error or the data provided by Canvas
	"""
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id", "")

	if not course_id: return error_generator("A course ID must be provided!", 404)

	if header:
		quiz_info = requests.get(
			"{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
			headers=header, verify=False is client.dev)
		return content_helper(quiz_info)

	else:
		return error_generator("Invalid session, unauthorized", 401)


def find_std_count(std, scores, start_index):
	# TODO: Fix (Dict is not ordered so this does not work
	unique_scores = list(scores.keys())
	unique_scores.sort()
	try:
		test_score = unique_scores[start_index]
	except IndexError:
		return 0
	if float(test_score) >= std:
		total_scores_above = 0
		for score in unique_scores[start_index:]:
			total_scores_above += scores[score]
		return total_scores_above
	else:
		start_index += 1
		return find_std_count(std, scores, start_index)


@require_GET
def get_quiz_stats(request):
	"""Gets basic information about a particular quiz's statistics
	:param request: The current request as provided by django
	:return: A Json response either containing an error or the standard deviation and number of students above 2 stds.
	"""
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id", "")
	quiz_id = request.GET.get("quiz_id", "")

	if not course_id: return error_generator("A course ID must be provided!", 404)
	if not quiz_id: return error_generator("A quiz ID must be provided!", 401)

	quiz_stats = requests.get(
		"{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
		headers=header,
		verify=False is client.dev
	)

	return_json = {}
	if quiz_stats.status_code == 200:
		quiz_stats = quiz_stats.json()["quiz_statistics"][0]

		# Finds the standard deviation
		return_json["std"] = quiz_stats["submission_statistics"]["score_stdev"]
		return_json["std"] = return_json["std"] / quiz_stats["points_possible"]
		# Finds the number of students scoring two standard deviations above the mean
		scores = quiz_stats["submission_statistics"]["scores"]
		return_json["no_above_2_std"] = find_std_count(return_json["std"] * 200, scores, floor(len(scores)/2) - 1)

		response = JsonResponse({"success": {"data": json.dumps(return_json)}})
		response.status_code = 200
		return response

	else:
		return error_generator("invalid session, unauthorized", 401)


@require_GET
def get_quiz_submissions(request):
	# TODO: Remake to user only one user dict
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id, quiz_id = request.GET.get("course_id"), request.GET.get("quiz_id")
	link = "{}/api/v1/courses/{}/quizzes/{}/submissions".format(url, course_id, quiz_id)
	submissions = requests.get(
		link,
		headers=header,
		verify=False is client.dev
	)

	users_to_events = {}
	users_to_page_leaves = {}
	total_page_leaves = 0
	unique_page_leavers = 0
	for submissions in submissions.json()["quiz_submissions"]:
		user_id = submissions["user_id"]
		submission_id = submissions["id"]
		local_page_leaves = 0
		events = requests.get(link + f"/{submission_id}/events?per_page=50000",
		                      headers=header, verify=False is client.dev)
		if events.status_code == 200:
			events_json = events.json()
			for event in events_json["quiz_submission_events"]:
				if event["event_type"] == 'page_blurred':
					total_page_leaves += 1
					local_page_leaves += 1

				users_to_page_leaves[user_id] = {}
				users_to_page_leaves[user_id]["page_leaves"] = local_page_leaves
				users_to_page_leaves[user_id]["time_taken"] = submissions["time_spent"]
				profile = requests.get(f"{url}/api/v1/users/{user_id}/profile", headers=header, verify=False is client.dev)
				users_to_page_leaves[user_id]["name"] = profile.json()["name"]
				if local_page_leaves > 0:
					unique_page_leavers += 1
				users_to_events[user_id] = events.json()
		elif events.status_code == 400 and "quiz log auditing must be enabled" in events.json()["message"]:
			return error_generator("Quiz log auditing it not enabled! This isn't going to work until you enable that!", 400)
		else:
			return error_generator("invalid session, unauthorized", 401)

	response = JsonResponse({"success": {"data": {"page_leaves": total_page_leaves,
	                                              "user_to_events": users_to_events,
	                                              "user_to_page_leaves": users_to_page_leaves,
	                                              "unique_page_leavers": unique_page_leavers}}})
	response.status_code = 200
	return response


def anonymize_data(json_data: str) -> Optional[str]:
	"""
	A function to save the data in a style anonymized in order to be in compliance with FERPA. For more information
	see: https://studentprivacy.ed.gov/sites/default/files/resource_document/file/data_deidentification_terms.pdf
	:param json_data: The data that is going to be saved in string form
	:return: A stringifyed version of the anonymized data or none if the data format is invalid
	"""
	json_data = json.loads(json_data)  # convert the data to a dict for easy indexing
	for index, items in enumerate(json_data):
		try:
			items["id"] = rand.randint(0, 100000000)
			items["name"] = "null"
		except KeyError:
			return None

	return json.dumps(json_data)  # return the data in str form


@require_POST
def save_data(request: HttpRequest) -> JsonResponse:
	"""A endpoint to save the POST data
	:param request: The current request as provided by django
	:return: A JSONResponse containing either an error or a message saying the data was saved
	"""
	if not request.user.is_authenticated:
		return error_generator("User is not logged in!", 401)

	json_data = request.POST.get("data", "")

	json_data = anonymize_data(json_data)
	# TODO: Fix error code
	if json_data is None: return error_generator("Improper data format detected!", 401)
	current_data = Dataset.objects.create(
		data=json_data
	)

	UserToDataset.objects.create(
		user=request.user.canvas_oauth2_token,
		dataset=current_data
	)
	response = JsonResponse({"success": "data saved"})
	response.status_code = 200
	return response


def saved_data(request):
	# This is an endpoint on the API that actually renders something, this may need to be changed.
	if not request.user.is_authenticated:
		return error_generator("User is not logged in!", 401)
	load = False
	datasets = UserToDataset.objects.filter(
		user=request.user.canvas_oauth2_token
	)
	if datasets: load = True

	return render(request, 'saved_data.html', {"datasets": datasets, "load": load})


# TODO: Require PUT
def delete_data(request: HttpRequest) -> JsonResponse:
	"""
	:param request: The current request as provided by django
	:return: A Jsonresponse containing the result of the delete request
	"""
	put = QueryDict(request.body)  # Get the PUT request information
	item_id = put.get("id")
	Dataset.objects.get(id=item_id).delete()  # Delete the object from the database
	response = JsonResponse({"success": "none"})  # No important information is returned
	response.status_code = 200
	return response


@require_GET
def set_oauth_url_cookie(request: HttpRequest) -> JsonResponse:
	"""Sets the oauth cookie if needed
	:param request: The current request as provided by django
	:return: JSONResponse containing the cookie for the URL or a error
	"""
	url = request.GET.get("url", "")
	client = get_dev_key(f"https://{url}")
	if client is not None:  # This checks if a dev key exists for the canvas installation
		# if request.user.is_authenticated:  # This checks if the user is recognized as logged in
		# 	# Checks if the token is not expired and the user is logging in on the same domain
		# 	if test_token(request.user.canvas_oauth2_token.access_token, url, client.dev) and \
		# 			f"https://{url}" in request.user.canvas_oauth2_token.url:
		# 		return error_generator("User already logged in on this domain!", 406)
		response = JsonResponse({"success": "none"})
		response.set_cookie("url", request.GET.get("url", ""))
		response.status_code = 200
		return response  # Otherwise set the cookie for the current url to continue the OAuth2 process
	else:
		return error_generator("Unsupported version of canvas", 404)
