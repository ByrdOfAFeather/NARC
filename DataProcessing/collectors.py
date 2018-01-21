"""Collects json Data
"""
# Created on Mon. October 16 2:18:00 2017 
# Used to call Canvas API for quick and easy data collection 
# @author: ByrdOfAFeather


import requests 
import json 
import re
import os

if not os.path.exists(r"..\.\temp"):
	os.makedirs(r"..\.\temp")

if not os.path.exists(r"..\.\temp/data"):
	os.makedirs(r"..\.\temp/data")

temp_dir = r"..\.\temp/data"


class UserCollector:
	def __init__(self, url, header, verify):
		self.url = url
		self.header = header
		self.verify = verify

	def get_associated_courses(self):
		api_target = r"{}/api/v1/courses?enrollment_state=active&per_page=50"
		courses = requests.put(api_target.format(self.url), headers=self.header, verify=self.verify)
		course_dict = {}

		for courses in courses.json():
			course_name = courses['name']
			course_id = courses['id']
			course_dict[course_name] = course_id

		return course_dict


class Collector:
	"""Collects data from the Canvas API
	"""
	def __init__(self, url, header, class_id, verify=True):
		"""
		:param url: The URL used for Canvas ex. http://stanford.instructure.com
		:param header: The authorization information for the canvas API
		:param class_id: The ID for the canvas course
		"""
		self.header = header
		self.url = url
		self.class_id = class_id
		self.verify = verify

	def get_class_users(self, output_folder, output_file_name):
		"""Gets all users in a specific class
		:param output_folder: Folder to save the json data
		:param output_file_name: Name for the file containing json data
		:return: A dictionary containing user ids linked to user names
		"""
		api_target = r'{}/api/v1/courses/{}/enrollments?per_page=50'
		enrollment = requests.put(api_target.format(self.url, self.class_id), headers=self.header, verify=self.verify)

		with open('{}/{}.json'.format(output_folder, output_file_name), 'w') as f:
			json.dump(enrollment.json(), f)

		with open('{}/{}.json'.format(output_folder, output_file_name)) as enrollment_json:
			enrollment_json = json.load(enrollment_json)

		user_dict = {}
		for users in enrollment_json:
			user_dict[users['user']['id']] = users['user']['name']
		return user_dict

	def get_course_modules(self):
		api_target = "{}/api/v1/courses/{}/modules?per_page=50"
		module = requests.put(api_target.format(self.url, self.class_id), headers=self.header, verify=self.verify)
		module_dict = {}
		for modules in module.json():
			if modules['published']:
				module_name = modules['name']
				module_id = modules['id']
				module_dict[module_name] = module_id

		return module_dict


class Module(Collector):
	"""Represents and collects data from a single module
	"""
	def __init__(self, module_id, url, header, class_id, verify=True):
		self.module_id = module_id
		super(Module, self).__init__(url=url, header=header, class_id=class_id, verify=verify)

	@staticmethod
	def _get_module_quizzes(module_items):
		"""Returns items from a module that are designated as quizzes
		:param module_items: A json file containing all the items from a module
				:func:`~collectors.Module.get_module_items`
		:return:
		"""
		quiz_dict = {}
		for items in module_items:
			if items['type'] == 'Quiz':
				quiz_dict[items['title']] = items['content_id']
		return quiz_dict

	@staticmethod
	def _get_module_notes(module_items):
		"""Returns items from a module that are designated as notes (Files or Google Doc Links)
		:param module_items: A json file containing all the items from a module
				:func:`~collectors.Module.get_module_items`
		:return: A Dictionary linking the item id to its title
		"""
		notes_list = {}
		for items in module_items:
			if items['type'] == 'File':
				notes_list[items['id']] = items['title']

			elif items['type'] == 'ExternalUrl':
				notes_list[items['id']] = items['title']

		return notes_list

	def get_module_items(self):
		"""Retrieves items from a module
		:return: A Dictionary containing specific references to notes and quiz sections as well as overall results
		"""
		api_target = r"{}/api/v1/courses/{}/modules/{}/items"
		module = requests.put(api_target.format(self.url, self.class_id, self.module_id),
			headers=self.header, verify=self.verify)
		notes = self._get_module_notes(module.json())
		quizzes = self._get_module_quizzes(module.json())
		module_dict = {'Subsections': {'Notes': notes, 'Quizzes': quizzes}, 'Overall': module.json()}
		return module_dict

	def module_times(self):
		"""Gets the amount of time a user spent on module items in a quizzes module
		TO BE IMPLEMENTED
		"""
		for students in self.get_class_users('temp', 'temp'):
			# url = r'{}/api/v1/courses/{}/analytics/users/{}/activity'
			api_target = r'{}/api/v1/users/{}/page_views'
			response = requests.put(api_target.format(self.url, students), headers=self.header, verify=self.verify)
			# print(response.json())


class Quiz(Collector):
	"""Represents a single quiz
	"""
	def __init__(self, quiz_id, class_id, header, url, verify=True):
		self.quiz_id = quiz_id
		super(Quiz, self).__init__(class_id=class_id, header=header, url=url, verify=verify)
		self.submissions = self._get_quiz_submissions()

	def get_quiz_question_ids(self):
		"""Builds a dictionary of questions linked to their respective ids
		:return: dictionary {question: question_text, question order, question answers}
		"""
		api_target = r'{}/api/v1/courses/{}/quizzes/{}/questions?per_page=100'
		quiz_response = requests.put(api_target.format(self.url, self.class_id, self.quiz_id),
			headers=self.header, verify=self.verify)

		quiz_question_id_dict = {}
		for questions in quiz_response.json():
			raw_text = questions['question_text']
			first_expression = re.compile('<.*?>')
			questions['question_text'] = re.sub(first_expression, '', raw_text)
			quiz_question_id_dict[questions['id']] = (questions['question_text'],
			                                          questions['position'],
			                                          questions['answers'])

		return quiz_question_id_dict

	def _get_quiz_submissions(self):
		"""Gets all submission objects of a quiz
		:return: list [(submission id, user id)]
		"""
		api_target = r'{}/api/v1/courses/{}/quizzes/{}/submissions?per_page=100'
		quiz = requests.put(url=api_target.format(self.url, self.class_id, self.quiz_id),
			headers=self.header, verify=self.verify)

		submission_list = []
		submission_dict = []
		for submissions in quiz.json()['quiz_submissions']:
			submission_dict.append(submissions)
			submission_list.append((submissions['id'], submissions['user_id']))

		return submission_list, submission_dict

	def get_questions_answered(self):
		"""Gets a dictionary of users linked to their question answered event for this particular quiz
		:return:
		{ user id:
			[
				{
					"id": id,
					"event_type": "question_answered",
					"event_data": [
				        {
				            "quiz_question_id" : question id ,
				            "answer" : answer id of user-given answer
				        }
					],
		            "created_at": date and time of even creation
		            "answer_text": the actual question in text form
		            "order": the question number relative to the quiz
		        }
			]
		}
		"""
		# Checks if data already exists
		if os.path.exists(r"{}/questions_answered_{}.json".format(temp_dir, self.quiz_id)):
			quiz_submissions = json.load(open(r"{}/questions_answered_{}.json".format(temp_dir, self.quiz_id)))

			if len(quiz_submissions.keys()) == len(self._get_quiz_submissions()[0]):  # Needs to check for updates
				print("Getting Already Made Quiz Questions Json")
				return quiz_submissions

		# Checks if pre-req data already exists
		print("Rebuilding Quiz Questions Json")
		event_dict = self.get_quiz_events()

		# Builds a list of event_type = question_answered
		questions_answered_dict = {}
		key_list = self.get_quiz_question_ids()
		for user_id, event_dict in event_dict.items():
			current_questions_answered = []

			for items in event_dict['quiz_submission_events']:
				if items['event_type'] == 'question_answered':
					current_questions_answered.append(items)

			questions_answered_dict[user_id] = current_questions_answered

			# Adds readability information to the output json file
			for questions in questions_answered_dict[user_id]:
				current_id = int(questions['event_data'][0]['quiz_question_id'])
				quiz_text = key_list[current_id][0]
				quiz_order = key_list[current_id][1]
				questions['question_text'] = quiz_text
				questions['order'] = quiz_order

			del questions_answered_dict[user_id][0]

		with open('{}/{}.json'.format(temp_dir, 'questions_answered_{}'.format(self.quiz_id)), 'w') as f:
			json.dump(questions_answered_dict, f)

		return questions_answered_dict

	def get_correct_answers(self):
		"""
		TODO: Finish Implementation
		:return:
		"""
		event_dict = self.get_quiz_events()
		user_specific_correct_answer_dict = {}
		cur_correct_answer_dict = {}
		for students, event_dict in event_dict.items():

			cur_quiz_data = list(event_dict.values())[0][0]['event_data']['quiz_data']

			for questions in cur_quiz_data:
				cur_correct_answer_dict[questions["id"]] = [i["id"] for i in questions["answers"] if i["weight"] > 0]

			user_specific_correct_answer_dict[students] = cur_correct_answer_dict

		return user_specific_correct_answer_dict

	def get_page_leaves(self):
		"""
		Gets the amount of times a user left the page during the quiz * 2 (times left + times returned)
		:return: Dictionary linking user page leaves to user id
		"""
		if os.path.exists(r"{}/page_leaves_{}.json".format(temp_dir, self.quiz_id)):
			page_leaves_dict = json.load(open(r"{}/page_leaves_{}.json".format(temp_dir, self.quiz_id)))

			if len(page_leaves_dict.keys()) == len(self._get_quiz_submissions()[0]):  # Needs to check for updates
				print("Getting Already Made Page Leaves Json")
				return page_leaves_dict

		# Checks if pre-req data already exists
		print("Building Page Leaves Json")
		event_dict = self.get_quiz_events()

		page_leaves_dict = {}
		for user_id, event_dict in event_dict.items():

			current_list = []
			for items in event_dict['quiz_submission_events']:
				if items['event_type'] == 'page_blurred' or items['event_type'] == 'page_focused':
					current_list.append(items)

			page_leaves_dict[user_id] = current_list

		with open('{}/{}.json'.format(temp_dir, 'page_leaves_{}'.format(self.quiz_id)), 'w') as f:
			json.dump(page_leaves_dict, f)

		return page_leaves_dict

	def get_quiz_events(self):
		"""Gets the events of a quiz
		:return: Dictionary {user_id: events for user}
		"""
		if os.path.exists(r"{}/events_{}.json".format(temp_dir, self.quiz_id)):
			events = json.load(open(r"{}/events_{}.json".format(temp_dir, self.quiz_id)))

			if len(events.keys()) == len(self._get_quiz_submissions()[0]):  # Needs to check for changes
				print("Getting Already Made Events Json")
				return events

		print("Rebuilding Quiz Events Json")
		api_target = '{}/api/v1/courses/{}/quizzes/{}/submissions/{}/events?per_page=10000'

		# Builds a dictionary containing events linked to student canvas ids
		quiz_events = {}
		for submission_id, user_id in self.submissions[0]:
			events = requests.put(api_target.format(self.url, self.class_id, self.quiz_id, submission_id),
			                      headers=self.header, verify=self.verify)
			quiz_events[user_id] = events.json()

		with open('{}/{}.json'.format(temp_dir, 'events_{}'.format(self.quiz_id)), 'w') as f:
			json.dump(quiz_events, f)

		return quiz_events


class Discussion(Collector):
	"""Represents and collects a single canvas discussion
	"""
	def __init__(self, class_id, header, url, discussion_id):
		self.discussion_id = discussion_id
		super(Discussion, self).__init__(class_id, header, url)

	def get_discussion(self, output_folder='Discussions', output_file_name='discussiontest.json', anonymous=False):
		"""Returns a id/name dictionary and a name/posts dictionary
		:param output_folder: The folder for output
		:param output_file_name: The file name of the output
		:param anonymous: Should names be included in output
		:return: A tuple containing A dictionary file containing participants linked to their ids and
				users linked to their posts
		"""
		api_target = '{}/api/v1/courses/{}/discussion_topics/{}/view'
		r = requests.put(api_target.format(self.url, self.class_id, self.discussion_id),
			headers=self.header, verify=self.verify)

		with open('{}/{}.json'.format(output_folder, output_file_name), 'w') as f:
			json.dump(r.json(), f)

		with open('{}/{}.json'.format(output_folder, output_file_name)) as discussion:
			discussion = json.load(discussion)

		participant_dict = {}
		for participants in discussion['participants']:
			participant_dict[participants['id']] = participants['display_name']

		if anonymous:
			index = 0
			participant_posts = []
			for posts in discussion['view']:
				participant_posts.append(("User {}".format(index), posts['message']))
				index += 1

		else:
			participant_posts = []
			for posts in discussion['view']:
				participant_posts.append((participant_dict[posts['user_id']], posts['message']))

		return participant_dict, participant_posts

	@staticmethod
	def clean_discussion(posts):
		"""Cleans a Canvas Discussion either from a downloaded JSON form or a get_discussion() form
		:param posts:
		:return: A dictionary indexed numerically of cleaned survey data (HTML Tags removed as well as image tags)
		"""
		second_expression = re.compile("data-mathml='.*?'", re.DOTALL)
		first_expression = re.compile('<.*?>')
		special = re.compile(r"\xa0")

		index = 0
		for participant, raw_post in posts:
			final = re.sub(first_expression, '', raw_post)
			final = re.sub(second_expression, '', final)
			final = re.sub(first_expression, '', final)
			final = re.sub(special, '', final)
			posts[index] = (participant, final)
			index += 1
		return posts
