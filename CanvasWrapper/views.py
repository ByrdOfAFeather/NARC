from datetime import timedelta

import requests
import json
import random as rand
import os
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.http import QueryDict, HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse
from Main.models import APIKey
from CanvasWrapper.predictors import classify
from CanvasWrapper.models import Dataset, UserToDataset
from math import floor


def test_token(token, url, dev):
	simple_request = requests.get(f"https://{url}/api/v1/courses", headers={"Authorization": f"Bearer {token}"},
	                              verify=False is dev)
	return simple_request.status_code == 200


def content_helper(request):
	if request.status_code == 200:
		response = JsonResponse({"success": {"data": json.dumps(request.json())}})
		response.status_code = 200
		return response
	else:
		response = JsonResponse({"error": "unknown error occured! (Maybe token expired?)"})
		response.status_code = request.status_code
		return response


def error_generator(error, error_code):
	response = JsonResponse({"error": error})
	response.status_code = error_code
	return response


def get_client_id(url):
	key = APIKey.objects.filter(url=url)
	if key:
		return key[0]
	else:
		return None


def expire_checker(request):
	if not request.user.is_authenticated:
		return error_generator("You aren't logged in!", 401)

	url = request.user.canvas_oauth2_token.url

	client = get_client_id(url)
	if not client:
		return error_generator("We do not support this version of Canvas!", 401)

	if request.user.canvas_oauth2_token.expires_within(timedelta(seconds=60)):
		print("I'M WORKING ON GETTING A NEW TOKEN")
		new_token = requests.post(f"{url}/login/oauth2/token", {
			"grant_type": "refresh_token",
			"client_id": client.client_id,
			"client_secret": client.client_secret,
			"redirect_uri": "http://127.0.0.1:8000/oauth_confirm",
			"refresh_token": request.user.canvas_oauth2_token.refresh_token,
		}, verify=False is client.dev)  # TODO: Remember to make this True in production!
		if new_token.status_code == 200:
			new_token_data = new_token.json()
			request.user.canvas_oauth2_token.access_token = new_token_data["access_token"]
			request.user.canvas_oauth2_token.expires = timezone.now() + timedelta(seconds=new_token_data["expires_in"])
			request.user.canvas_oauth2_token.save()
		else:
			return error_generator("Error getting new token! Please login again!", 401), None
	else: return None, client


def get_courses(request):
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	courses = requests.get(
		"{}/api/v1/courses?per_page=50".format(url),
		headers=header, verify=False is client.dev)
	return content_helper(courses)


def get_modules(request):
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id")
	if header:
		modules = requests.get(
			"{}/api/v1/courses/{}/modules?per_page=50".format(url, course_id),
			headers=header, verify=False is client.dev)

		return content_helper(modules)

	else:
		return error_generator("invalid session, unauthorized", 401)


def get_quizzes(request):
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id")
	module_id = request.GET.get("module_id")
	if header:
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
			response.status_code = request.status_code
			return response

	else:
		return error_generator("invalid session, unauthorized", 401)


def get_quiz_info(request, quiz_id):
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id")
	if header:
		quiz_info = requests.get(
			"{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
			headers=header, verify=False is client.dev)
		return content_helper(quiz_info)

	else:
		return error_generator("invalid session, unauthorized", 401)


def find_std_count(std, scores, start_index):
	# TODO: Fix (Dict is not ordered so this does not work
	unique_scores = list(scores.keys())
	unique_scores.sort()
	print(unique_scores)
	print(std)
	try:
		test_score = unique_scores[start_index]
		print(test_score)
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


def get_quiz_stats(request):
	error = expire_checker(request)
	url = request.user.canvas_oauth2_token.url
	if error[0] is not None:
		return error[0]
	client = error[1]
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id", "")
	quiz_id = request.GET.get("quiz_id", "")

	quiz_stats = requests.get(
		"{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
		headers=header,
		verify=False is client.dev
	)

	return_json = {}
	if quiz_stats.status_code == 200:
		quiz_stats = quiz_stats.json()["quiz_statistics"][0]

		# Fins the standard deviation
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
	users_to_submissions = {}
	users_to_page_leaves = {}
	total_page_leaves = 0
	unique_page_leavers = 0
	for submissions in submissions.json()["quiz_submissions"]:
		user_id = submissions["user_id"]
		submission_id = submissions["id"]
		users_to_submissions[user_id] = submissions
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
	                                              "unique_page_leavers": unique_page_leavers,
	                                              'user_to_submissions': users_to_submissions}}})
	response.status_code = 200
	return response


def anonymize_data(json_data):
	"""
	A function to save the data in a style anonymized in order to be in compliance with FERPA. For more information
	see: https://studentprivacy.ed.gov/sites/default/files/resource_document/file/data_deidentification_terms.pdf
	:param json_data:
	:return:
	"""
	json_data = json.loads(json_data)
	for index, items in enumerate(json_data):
		items["id"] = rand.randint(0, 100000000)
		items["name"] = "null"
	return json.dumps(json_data)


def save_data(request):
	if not request.user.is_authenticated:
		return error_generator("User is not logged in!", 401)

	json_data = request.POST.get("data", "")

	json_data = anonymize_data(json_data)
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
	if not request.user.is_authenticated:
		return error_generator("User is not logged in!", 401)
	load = False
	datasets = UserToDataset.objects.filter(
		user=request.user.canvas_oauth2_token
	)
	if datasets: load = True

	return render(request, 'saved_data.html', {"datasets": datasets, "load": load})


def delete_data(request):
	put = QueryDict(request.body)
	item_id = put.get("id")
	Dataset.objects.get(id=item_id).delete()
	response = JsonResponse({"success": "none"})
	response.status_code = 200
	return response


def set_oauth_url_cookie(request):
	url = request.GET.get("url", "")
	client = get_client_id(f"https://{url}")
	if client is not None:
		if request.user.is_authenticated:
			if test_token(request.user.canvas_oauth2_token.access_token, url, client.dev) and \
					f"https://{url}" in request.user.canvas_oauth2_token.url:
				return error_generator("User already logged in on this domain!", 406)
		response = JsonResponse({"success": "none"})
		response.set_cookie("url", request.GET.get("url", ""))
		response.status_code = 200
		return response
	else:
		return error_generator("Unsupported version of canvas", 404)


def parse_data(data):
	frame = pd.DataFrame.from_dict(data, orient="index")
	return frame

# TODO: More research is required into potential security flaws of this endpoint
@csrf_exempt
def mobile_endpoint(request):
	data = request.POST.get("data", "")
	data = json.loads(data)
	print(data)
	try:
		# Temp security solution for mobile app while in development
		if data["secret"] == os.environ.get("MOBILESECRET", ""):
			del data["secret"]
			data = parse_data(data)
			cheaters, non_cheaters = classify(data)
			response = JsonResponse({"success": {"data":
				                                     {
					                                     "cheaters": cheaters,
					                                     "non_cheaters": non_cheaters
				                                     }}})
			response.status_code = 200
			return response
		else:
			response = JsonResponse({"error": "shoot!"})
			response.status_code = 402
			return response

	except KeyError:
		error_generator("Invalid JSON!", 400)

