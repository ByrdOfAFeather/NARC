import requests
import json
import hashlib
from django.http import QueryDict
from django.shortcuts import render
from django.http import JsonResponse
from CanvasWrapper.models import AuthorizedUser, Dataset, UserToDataset
from math import floor


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


# TODO CHECK GETS FOR IF A USER IS NOT LOGGED IN & Get URL When it Expires
def get_courses(request):
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	url = request.COOKIES.get("url", False)
	print(url)
	if header:
		courses = requests.get(
			"https://{}/api/v1/courses?per_page=50".format(url),
			headers=header, verify=False)
		return content_helper(courses)

	else:
		return error_generator("invalid session, unauthorized", 401)


def get_modules(request):
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	url = request.COOKIES.get("url", False)
	course_id = request.GET.get("course_id")
	if header:
		modules = requests.get(
			"https://{}/api/v1/courses/{}/modules?per_page=50".format(url, course_id),
			headers=header, verify=False)

		return content_helper(modules)

	else:
		return error_generator("invalid session, unauthorized", 401)


def get_quizzes(request):
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	url = request.COOKIES.get("url", False)
	course_id = request.GET.get("course_id")
	module_id = request.GET.get("module_id")
	if header:
		quizzes = requests.get(
			"https://{}/api/v1/courses/{}/modules/{}/items".format(url, course_id, module_id),
			headers=header, verify=False)
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
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	url = request.COOKIES.get("url", False)
	course_id = request.GET.get("course_id")
	if header:
		quiz_info = requests.get(
			"https://{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
			headers=header, verify=False)
		return content_helper(quiz_info)

	else:
		return error_generator("invalid session, unauthorized", 401)


def find_std_count(std, scores, start_index):
	# TODO: Fix (Dict is not ordered so this does not work
	unique_scores = list(scores.keys())
	print(scores)
	try:
		test_score = unique_scores[start_index]
	except IndexError:
		return {"users": None, "no_above_2_std": 0}
	if float(test_score) >= std:
		total_scores_above = 0
		for score in unique_scores[start_index:]:
			total_scores_above += scores[score]
		return total_scores_above
	else:
		start_index += 1
		find_std_count(std, scores, start_index)


def get_quiz_stats(request):
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	course_id = request.GET.get("course_id", "")
	quiz_id = request.GET.get("quiz_id", "")
	if header:

		url = request.COOKIES.get("url", False)
		if not url:
			return error_generator("Could not find url!", 404)

		quiz_stats = requests.get(
			"https://{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
			headers=header,
			verify=False
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

	else:
		return error_generator("invalid session, unauthorized", 401)


def get_quiz_submissions(request):
	header = {"Authorization": f"Bearer {request.user.canvas_oauth2_token.access_token}"}
	if header:
		url = request.COOKIES.get("url", False)
		course_id, quiz_id = request.GET.get("course_id"), request.GET.get("quiz_id")
		link = "https://{}/api/v1/courses/{}/quizzes/{}/submissions".format(url, course_id, quiz_id)
		submissions = requests.get(
			link,
			headers=header,
			verify=False
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
			events = requests.get(link + "/{}/events?per_page=50000".format(submission_id),
			                      headers=header)
			if events.status_code == 200:
				events_json = events.json()
				for event in events_json["quiz_submission_events"]:
					if event["event_type"] == 'page_blurred':
						total_page_leaves += 1
						local_page_leaves += 1

				users_to_page_leaves[user_id] = {}
				users_to_page_leaves[user_id]["page_leaves"] = local_page_leaves
				if local_page_leaves > 0:
					unique_page_leavers += 1
				users_to_events[user_id] = events.json()

			else:
				return error_generator("invalid session, unauthorized", 401)

		response = JsonResponse({"success": {"data": {"page_leaves": total_page_leaves,
		                                              "user_to_events": users_to_events,
		                                              "user_to_page_leaves": users_to_page_leaves,
		                                              "unique_page_leavers": unique_page_leavers,
		                                              'user_to_submissions': users_to_submissions}}})
		response.status_code = 200
		return response
	else:
		return error_generator("invalid session, unauthorized", 401)


def anonymize_data(json_data):
	# Technically, the original ID isn't that revealing as long as the users are in separate instructure domains.
	# However, in my experience, users in the same domain (even students!) can look up users based on ID. So
	# it's better to just go ahead and assign incrementing numbers to the ids.
	json_data = json.loads(json_data)
	for index, items in enumerate(json_data):
		items["id"] = index
	return json.dumps(json_data)


def save_data(request):
	# TODO: Remake to work with user model
	json_data = request.POST.get("data", "")
	token = request.COOKIES.get("header", False)
	token = token[26:-2]
	print(token)
	token = hashlib.sha3_256(token.encode("utf-8")).hexdigest()
	print(token)
	# TODO: Create Fail Conditions
	current_user = AuthorizedUser.objects.get(hashed_token=token)
	json_data = anonymize_data(json_data)

	current_data = Dataset.objects.create(
		data=json_data
	)

	UserToDataset.objects.create(
		user=current_user,
		dataset=current_data
	)
	response = JsonResponse({"success": "data saved"})
	response.status_code = 200
	return response


def saved_data(request):
	load = False
	datasets = ""
	token = request.COOKIES.get("header", "")
	print("I got here")
	if token:
		token = token[26:-2]
		token = hashlib.sha3_256(token.encode("utf-8")).hexdigest()
		user = AuthorizedUser.objects.get(
			hashed_token=token
		)
		if user:
			datasets = UserToDataset.objects.filter(
				user=user
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


# TODO: Fail condition (in particular check for the url to be valid)
def oauth_url(request):
	response = JsonResponse({"success": "none"})
	response.set_cookie("url", request.GET.get("url", ""))
	response.status_code = 200
	return response
