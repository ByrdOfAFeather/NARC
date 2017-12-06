import datetime
import time
import pandas as pd


class QuizEvents:
	def __init__(self, quiz, questions_answered=None):
		print("Initializing Quiz")
		self.data_set = {}
		self.quiz = quiz

		if not questions_answered: self._get_questions_answered()
		else: self.questions_answered = questions_answered

		self._init_data_set()

	def _get_questions_answered(self):
		print("Building Questions Answered")
		self.submissions = self.quiz.submissions[1]
		self.questions_answered = self.quiz.get_questions_answered()

	def _init_data_set(self):

		for submit in self.submissions:
			user_id = str(submit['user_id'])
			self.data_set[user_id] = {}
		self.data_set['Overall'] = {}

		self._build_average_question_time()
		self._build_user_scores()
		self._build_user_page_leaves()
		self._build_time_taken()

	def _build_average_question_time(self):
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
					next = temp_time_list[i+1]
					temp_distance_list.append(next - current)

				distance_list = []
				# Builds a list of distances and adds to a running list of distances
				for items in temp_distance_list:
					distance_list.append(items.seconds)
					overall_distance_list.append(items.seconds)
				average_time = round(sum(distance_list) / len(distance_list), 2)
			else: average_time = None
			self.data_set[students]['average_time_between_questions'] = average_time

		overall_average_time = round(sum(overall_distance_list) / len(overall_distance_list), 2)
		self.data_set['Overall']['average_time_between_questions'] = overall_average_time

	def _build_user_scores(self):
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
		all_page_leaves = []
		page_leaves = []
		page_leave_list = self.quiz.get_page_leaves()

		for user_id, full_list in page_leave_list.items():
			cur_length = len(full_list)
			all_page_leaves.append(cur_length)
			page_leaves.append(cur_length)
			self.data_set[user_id]['page_leaves'] = cur_length

		average_page_leaves = round(sum(all_page_leaves) / len(all_page_leaves), 2)
		self.data_set['Overall']['page_leaves'] = average_page_leaves

	def _build_time_taken(self):
		time_taken = []
		for submit in self.submissions:
			time_taken.append(submit['time_spent'])
			user_id = str(submit['user_id'])
			self.data_set[user_id]['time_taken'] = submit['time_spent']
		overall_average = round(sum(time_taken) / len(time_taken), 2)
		self.data_set['Overall']['time_taken'] = overall_average

	def _get_quiz_distance(self):
		pass

	def get_average_question_time(self, user_id='Overall'):
		assert type(user_id) is str, "Data is indexed by {} not {}".format(str, type(user_id))

		try:
			return self.data_set[user_id]['average_time']

		except KeyError:
			print("It appears there was an ID error, \nAvailable IDs are {}".format(self.data_set.keys()))
			return None

	def get_user_score(self, user_id='Overall'):
		assert type(user_id) is str, "Data is indexed by {} not {}".format(str, type(user_id))

		try:
			return self.data_set[user_id]['score']

		except KeyError:
			print("It appears there was an ID error, \nAvailable IDs are {}".format(self.data_set.keys()))
			return None

	def get_page_leaves(self, user_id='Overall'):
		assert type(user_id) is str, "Data is indexed by {} not {}".format(str, type(user_id))

		try:
			return self.data_set[user_id]['page_leaves']

		except KeyError:
			print("It appears there was an ID error, \nAvailable IDs are {}".format(self.data_set.keys()))
			return None

	def build_dataframe(self):
		return pd.DataFrame.from_dict(self.data_set, orient='index')
