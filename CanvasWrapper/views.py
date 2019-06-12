import requests
import json
from django.shortcuts import render
from django.http import JsonResponse
from math import floor

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
		response = JsonResponse({"success": {"data": json.dumps(request.json())}})
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


def get_quizzes(request):
	header = request.COOKIES.get("header", "")
	url = request.COOKIES.get("url", "canvas.instructure.com")
	course_id = request.GET.get("course_id")
	module_id = request.GET.get("module_id")
	if header:
		header = header.replace("'", "\"")
		header = json.loads(header)
		quizzes = requests.get(
			"https://{}/api/v1/courses/{}/modules/{}/items".format(url, course_id, module_id),
			headers=header)
		if quizzes.status_code == 200:
			quizzes = [
				{"name": items["title"], "id": items["content_id"]}
				for items in quizzes.json() if items['type'] == "Quiz"
			]
			response = JsonResponse({"success": {"data": str(quizzes)}})
			response.status_code = 200
			return response

		else:
			response = JsonResponse({"error": "unknown error occured! (Maybe token expired?)"})
			response.status_code = request.status_code
			return response

	else:
		response = JsonResponse({"error": "could not find cookie"})
		response.status_code = 401
		return response


def get_quiz_info(request, quiz_id):
	header = request.COOKIES.get("header", "")
	url = request.COOKIES.get("url", "canvas.instructure.com")
	course_id = request.GET.get("course_id")
	if header:
		header = header.replace("'", "\"")
		header = json.loads(header)
		quiz_info = requests.get(
			"https://{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
			headers=header)
		return content_helper(quiz_info)

	else:
		response = JsonResponse({"error": "could not find cookie"})
		response.status_code = 401
		return response


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
	header = request.COOKIES.get("header", "")
	course_id = request.GET.get("course_id", "")
	quiz_id = request.GET.get("quiz_id", "")
	if header:
		header = header.replace("'", "\"")
		header = json.loads(header)
		url = request.COOKIES.get("url", "canvas.instructure.com")
		quiz_stats = requests.get(
			"https://{}/api/v1/courses/{}/quizzes/{}/statistics".format(url, course_id, quiz_id),
			headers=header
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
			# TODO: Fail Case
			pass

	else:
		# TODO: Fail Case
		pass


def get_quiz_submissions(request):
	header = request.COOKIES.get("header", "")
	if header:
		header = header.replace("'", "\"")
		header = json.loads(header)
		url = request.COOKIES.get("url", "canvas.instructure.com")
		course_id, quiz_id = request.GET.get("course_id"), request.GET.get("quiz_id")
		link = "https://{}/api/v1/courses/{}/quizzes/{}/submissions".format(url, course_id, quiz_id)
		submissions = requests.get(
			link,
			headers=header
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
				# TODO: Fail Condition
				pass

		response = JsonResponse({"success": {"data": {"page_leaves": total_page_leaves,
		                                              "user_to_events": users_to_events,
		                                              "user_to_page_leaves": users_to_page_leaves,
		                                              "unique_page_leavers": unique_page_leavers,
		                                              'user_to_submissions': users_to_submissions}}})
		response.status_code = 200
		return response
	else:
		# TODO: Fail Condition
		pass
