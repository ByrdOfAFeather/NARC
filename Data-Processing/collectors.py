"""Collects json Data
"""
# Created on Mon. October 16 2:18:00 2017 
# Used to call Canvas API for quick and easy data collection 
# @author: ByrdOfAFeather


import requests 
import json 
import re


class Collector:
	"""Collects data from the Canvas API
	"""
	def __init__(self, url=None, header=None, class_id=None):
		"""
		:param url:
		:param header: The authorization information for the canvas API
		:param class_id: The ID for the canvas course
		"""
		self.header = header
		self.url = url
		self.class_id = class_id

	def get_class_users(self, output_folder, output_file_name):
		"""Gets all users in a specific class
		:param output_folder: Folder to save the json data
		:param output_file_name: Name for the file containing json data
		:return: A dictionary containing user ids linked to user names
		"""
		api_target = r'{}/api/v1/courses/{}/enrollments'
		enrollment = requests.put(api_target.format(self.url, self.class_id), headers=self.header)

		with open('{}/{}.json'.format(output_folder, output_file_name), 'w') as f:
			json.dump(enrollment.json(), f)

		with open('{}/{}.json'.format(output_folder, output_file_name)) as enrollment_json:
			enrollment_json = json.load(enrollment_json)

		user_dict = {}
		for users in enrollment_json:
			user_dict[users['user']['id']] = users['user']['name']
		return user_dict


class Module(Collector):
	"""Represents and collects data from a single module
	"""
	def __init__(self, module_id=None, url=None, header=None, class_id=None):
		self.module_id = module_id
		super(Module, self).__init__(url=url, header=header, class_id=class_id)

	@staticmethod
	def _get_module_quizzes(module_items):
		"""Returns items from a module that are designated as quizzes
		:param module_items: A json file containing all the items from a module
				:func:`~collectors.Module.get_module_items`
		:return:
		"""
		quiz_list = {}
		for items in module_items:
			if items['type'] == 'Quiz':
				quiz_list[items['content_id']] = items['title']
		return quiz_list

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
		module = requests.put(api_target.format(self.url, self.class_id, self.module_id), headers=self.header)
		notes = self._get_module_notes(module.json())
		quizzes = self._get_module_quizzes(module.json())
		module_dict = {'Subsections': {'Notes': notes, 'Quizzes': quizzes}, 'Overall': module.json()}
		return module_dict

	def get_average_total_module_time(self):
		for students in self.get_class_users('temp', 'temp'):
			# url = r'{}/api/v1/courses/{}/analytics/users/{}/activity'
			api_target = r'{}/api/v1/users/{}/page_views'
			response = requests.put(api_target.format(self.url, students), headers=self.header)
			print(response.json())

	def get_average_individual_module_items_time(self):
		pass


class Quiz(Collector):
	"""Represents a single quiz
	"""
	def __init__(self, quiz_id, class_id=None, header=None, url=None):
		self.quiz_id = quiz_id
		super(Quiz, self).__init__(class_id=class_id, header=header, url=url)

	def _get_quiz_question_ids(self):
		api_target = r'{}/api/v1/courses/{}/quizzes/{}/questions'
		quiz_response = requests.put(api_target.format(self.url, self.class_id, self.quiz_id), headers=self.header)
		quiz_dict = {}
		for questions in quiz_response.json():
			raw_text = questions['question_text']
			first_expression = re.compile('<.*?>')
			questions['question_text'] = re.sub(first_expression, '', raw_text)
			quiz_dict[questions['id']] = (questions['question_text'], questions['position'], questions['answers'])
		return quiz_dict

	def _get_quiz_submissions(self):
		"""Gets all submission objects of a quiz
		:return: a list of submission ids
		"""
		api_target = r'{}/api/v1/courses/{}/quizzes/{}/submissions'
		quiz = requests.put(url=api_target.format(self.url, self.class_id, self.quiz_id), headers=self.header)
		submission_list = []
		for submissions in quiz.json()['quiz_submissions']:
			submission_list.append(submissions['id'])
		return submission_list

	def get_quiz_events(self):
		"""Gets the events of a quiz
		:return: ADD DOCUMENTATION HERE
		"""
		api_target = '{}/api/v1/courses/{}/quizzes/{}/submissions/{}/events'
		for submissions in self._get_quiz_submissions():
			events = requests.put(api_target.format(self.url, self.class_id, self.quiz_id, submissions),
			                      headers=self.header)

			# Gets the events declaring when a question was answered
			event_dict = events.json()
			questions_answered = [i
			                      for i in event_dict['quiz_submission_events']
			                      if i['event_type'] == 'question_answered'
			                      ]
			del questions_answered[0]  # Takes out a list of initialized quiz answers

			# Adds readability information to the output json file
			key_list = self._get_quiz_question_ids()
			for questions in questions_answered:
				current_id = int(questions['event_data'][0]['quiz_question_id'])
				quiz_text = key_list[current_id][0]
				quiz_order = key_list[current_id][1]
				quiz_answers = key_list[current_id][2]
				questions['question_text'] = quiz_text
				questions['order'] = quiz_order
				questions['answers'] = quiz_answers

			# Saves the JSON objects
			with open('{}/{}.json'.format('temp', 'questions_answered{}'.format(submissions)), 'w') as f:
				json.dump(questions_answered, f)
			with open('{}/{}.json'.format('temp', 'all_data{}'.format(submissions)), 'w') as f:
				json.dump(events.json(), f)


class Discussion(Collector):
	"""Represents and collects a single canvas discussion
	"""
	def __init__(self, discussion_id=None):
		self.discussion_id = discussion_id
		super(Discussion, self).__init__()

	def get_discussion(self, output_folder='Discussions', output_file_name='discussiontest.json', anonymous=False):
		"""Returns a id/name dictionary and a name/posts dictionary
		:param output_folder: The folder for output
		:param output_file_name: The file name of the output
		:param anonymous: Should names be included in output
		:return: A tuple containing A dictionary file containing participants linked to their ids and
				users linked to their posts
		"""
		api_target = '{}/api/v1/courses/{}/discussion_topics/{}/view'
		r = requests.put(api_target.format(self.url, self.class_id, self.discussion_id), headers=self.header)

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
