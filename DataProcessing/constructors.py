import datetime
import time
import pandas as pd
import os
import json
import requests


if not os.path.exists(r'..\.\temp'):
	os.makedirs(r'..\.\temp')

if not os.path.exists(r'..\.\temp/data'):
	os.makedirs(r'..\.\temp/data')

temp_dir = r'..\.\temp/data'


class QuizEvents:
	"""A builder of data sets for quiz event information"""
	def __init__(self, quiz, questions_answered=None, anon=True, pre_flags=False):
		print("Initializing Quiz")
		self.anon = anon  # anon = anonymous (false: index = user id & true: index = user name)
		self.data_set = {}
		self.quiz = quiz

		if not questions_answered: self._get_questions_answered()
		else: self.questions_answered = questions_answered

		self.pre_flags = pre_flags
		self._init_data_set()

	def _get_questions_answered(self):
		"""Gets submission events and questions answered events
		"""
		print("Building Questions Answered")
		self.submissions = self.quiz.submissions[1]
		self.questions_answered = self.quiz.get_questions_answered()

	def _init_data_set(self):
		"""Creates the entire data set
		"""
		# Dictionary key initialization

		# Sets pandas options for displaying a much larger data set
		pd.set_option('display.max_columns', 10)
		pd.set_option('display.width', 1000)

		for submit in self.submissions:
			user_id = str(submit['user_id'])
			self.data_set[user_id] = {}
		self.data_set['Overall'] = {}

		# self._build_changed_questions(correct_only=True)
		self._build_average_question_time()
		# self._build_user_scores()
		self._build_difficulty_index()
		self._build_time_taken()
		self._build_user_page_leaves()
		if not self.anon: self._non_anon_data_set()

	def _build_difficulty_index(self):

		api_target = '{}/api/v1/courses/{}/quizzes/{}/statistics?per_page=10000'
		question_stats = requests.put(api_target.format(self.quiz.url, self.quiz.class_id, self.quiz.quiz_id),
		                              headers=self.quiz.header)

		correct_answers = self.quiz.get_correct_answers()

		for students, answers in self.questions_answered.items():
			self.data_set[str(students)]['difficulty_index'] = 0

			current_correct_answers = correct_answers[students]
			for correct_questions in current_correct_answers:
				for question in question_stats.json()['quiz_statistics'][0]['question_statistics']:
					if int(question['id']) == correct_questions:
						self.data_set[str(students)]['difficulty_index'] += question['difficulty_index']

		self.data_set['Overall']['difficulty_index'] = 0

	def _build_changed_questions(self, correct_only=False):
		correct_answers = self.quiz.get_correct_answers()
		for students, answers in self.questions_answered.items():
			changed_questions = []
			changed_to_correct = []
			previous_answers = {}
			for answer in answers:
				current_question = answer['event_data'][0]['quiz_question_id']
				current_answer = answer['event_data'][0]['answer']

				if current_question in previous_answers.keys():
					if previous_answers[current_question] == current_answer:
						pass
					else:
						changed_questions.append((students,
						                          current_question,
						                          current_answer))

					previous_answers[current_question] = current_answer

				else:
					previous_answers[current_question] = current_answer

			if correct_only:
				for student, question, current_answer in changed_questions:
					if int(current_answer) in correct_answers[str(student)][int(question)]:
						changed_to_correct.append((student, question, current_answer))

			if not correct_only: self.data_set[str(students)]['changed_questions'] = len(changed_questions)
			if correct_only: self.data_set[str(students)]['changed_questions'] = len(changed_to_correct)

		self.data_set['Overall']['changed_questions'] = 5

	def _build_average_question_time(self):
		"""Adds the average question time as a feature to the current data set
		"""
		overall_distance_list = []
		for students, answers in self.questions_answered.items():
			temp_time_list = []
			# Builds a list of questions at the time they were answered
			for answer in answers:
				question_time = datetime.datetime(*time.strptime(answer['created_at'].replace("Z", ""),
				                                                 "%Y-%m-%dT%H:%M:%S")[:6])
				temp_time_list.append(question_time)
			# Checks if the time list is bigger than 1
			# (average time between questions isn't able to be found on n <= 1 examples)
			if len(temp_time_list) > 1:
				temp_distance_list = []
				# Builds a list of distances in datetime object format
				for i in range(0, len(temp_time_list) - 1):
					current = temp_time_list[i]
					after = temp_time_list[i+1]
					temp_distance_list.append(after - current)

				distance_list = []
				# Builds a list of distances and adds to a running list of distances
				for items in temp_distance_list:
					distance_list.append(items.seconds)
					overall_distance_list.append(items.seconds)
				average_time = round(sum(distance_list) / len(distance_list), 2)
			else: average_time = None
			self.data_set[str(students)]['average_time_between_questions'] = average_time

		overall_average_time = round(sum(overall_distance_list) / len(overall_distance_list), 2)
		self.data_set['Overall']['average_time_between_questions'] = overall_average_time

	def _build_user_scores(self):
		"""Adds the user score as a feature to the current data set
		"""
		score_list = []
		for submit in self.submissions:
			current_points = submit['kept_score']
			current_points_possible = submit['quiz_points_possible']
			current_score = round(current_points/current_points_possible, 2)
			user_id = str(submit['user_id'])
			score_list.append(current_score)
			self.data_set[user_id]['score'] = current_score

		overall_average = round(sum(score_list) / len(score_list), 2)
		self.data_set['Overall']['score'] = overall_average

	def _build_user_page_leaves(self):
		"""Adds the amount of times a user leaves a page as a feature to the current data set
		"""
		all_page_leaves = []
		page_leaves = []
		page_leave_list = self.quiz.get_page_leaves()

		for user_id, full_list in page_leave_list.items():
			cur_length = len(full_list)
			all_page_leaves.append(cur_length)
			page_leaves.append(cur_length)

			# Converts the dictionary keys into a list, takes the length to get the total number of questions
			# the multiplies by .5 to get 50 percent of the total number of questions
			if self.pre_flags:
				questions_no_subdivision = len(list(self.quiz.get_quiz_question_ids().keys())) * .70
				if cur_length >= questions_no_subdivision:
					self.data_set[user_id]['page_leaves'] = 'CA'
				else:
					self.data_set[user_id]['page_leaves'] = cur_length ** 2

			else:
				self.data_set[user_id]['page_leaves'] = cur_length ** 2

		average_page_leaves = round(sum(all_page_leaves) / len(all_page_leaves), 2)
		self.data_set['Overall']['page_leaves'] = average_page_leaves

	def _build_time_taken(self):
		"""Builds A Dictionary of time taken for the overall test
		"""
		time_taken = []
		for submit in self.submissions:
			time_taken.append(submit['time_spent'])
			user_id = str(submit['user_id'])
			self.data_set[user_id]['time_taken'] = submit['time_spent']
		overall_average = round(sum(time_taken) / len(time_taken), 2)
		self.data_set['Overall']['time_taken'] = overall_average

	def _get_quiz_distance(self):
		"""Gets the "distance" between the current quiz and average quiz score of a user
		TO BE IMPLEMENTED
		"""
		pass

	def _non_anon_data_set(self):
		"""Gets the user names and assigns them as indexes in the data set
		"""
		rebuild = False
		if os.path.exists(r"{}/user_names_{}.json".format(temp_dir, self.quiz.quiz_id)):
			quiz_users = json.load(open(r"{}/user_names_{}.json".format(temp_dir, self.quiz.quiz_id)))
			# Check to see if new submissions have come in
			if len(quiz_users['Overall']) != len(self.data_set['Overall']) or len(quiz_users) != len(self.data_set):
				rebuild = True
			else:
				print("Getting Already Made User Name List")
				# Sets pandas options for displaying a much larger data set
				pd.set_option('display.max_columns', 100)
				pd.set_option('display.width', 100000)

				self.data_set = quiz_users

		else: rebuild = True

		if rebuild:
			print("Rebuilding Name List")
			name_set = {}
			for ids, values in self.data_set.items():
				profile = requests.put(r'{}/api/v1/users/{}/profile'.format(self.quiz.url, ids), headers=self.quiz.header)
				try:
					name_set[profile.json()['name']] = values
				except KeyError:
					name_set['Overall'] = values  # Overall throws key error

			with open('{}/{}.json'.format(temp_dir, 'user_names_{}'.format(self.quiz.quiz_id)), 'w') as f:
				json.dump(name_set, f)

			self.data_set = name_set

	def get_average_question_time(self, user_id='Overall'):
		"""Gets average question time for a individual user
		:param user_id: Set to Overall (average) by default, finds the individual user in a dataframe
		:return: float value of average time between questions for passed user or the average value
		"""
		assert type(user_id) is str, "Data is indexed by {} not {}".format(str, type(user_id))

		try:
			return self.data_set[user_id]['average_time']

		except KeyError:
			print("It appears there was an ID error, \nAvailable IDs are {}".format(self.data_set.keys()))
			return None

	def get_user_score(self, user_id='Overall'):
		"""Simple method to get a score for a individual user
		:param user_id: Set to Overall (average) by default, finds the individual user in a dataframe
		:return: Float values of a user's score
		"""
		assert type(user_id) is str, "Data is indexed by {} not {}".format(str, type(user_id))

		try:
			return self.data_set[user_id]['score']

		except KeyError:
			print("It appears there was an ID error, \nAvailable IDs are {}".format(self.data_set.keys()))
			return None

	def get_page_leaves(self, user_id='Overall'):
		"""Simple method of getting the page leaves of a individual user
		:param user_id: Set to Overall (average) by default, finds the individual user in a dataframe
		:return: Float value of the number of page leaves a user has
		"""
		assert type(user_id) is str, "Data is indexed by {} not {}".format(str, type(user_id))

		try:
			return self.data_set[user_id]['page_leaves']

		except KeyError:
			print("It appears there was an ID error, \nAvailable IDs are {}".format(self.data_set.keys()))
			return None

	def build_dataframe(self):
		"""Builds a dataframe based on the current data set
		:return: Pandas dataframe containing input data
		"""
		# Creates a copy to preserve the integrity of the overall data in the data_set variable
		data_set_copy = self.data_set.copy()
		del self.data_set['Overall']
		data_set = self.data_set

		self.data_set = data_set_copy
		del data_set_copy

		data_frame = pd.DataFrame.from_dict(data_set, orient='index')

		if self.pre_flags:
			pre_flags = data_frame.loc[data_frame['page_leaves'] == 'CA']
			data_frame.drop(data_frame.loc[data_frame['page_leaves'] == 'CA'].index.values, inplace=True)
			return pre_flags, data_frame
		else:
			return data_frame
