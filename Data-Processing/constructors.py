import json
import datetime
import time


class QuizEvents:
	def __init__(self, quiz, questions_answered=None):
		print("Initializing Quiz")
		self.data_set = {}
		self.quiz = quiz
		if not questions_answered: self._get_questions_answered()
		else: self.questions_answered = questions_answered
		self._build_average_question_time(), self._get_user_scores()

	def _get_questions_answered(self):
		print("Building Questions Answered")
		self.quiz_events = self.quiz.get_quiz_events()
		self.questions_answered = self.quiz.get_questions_answered()

	def _build_average_question_time(self):
		overall_distance_list = []
		for students, answers in self.questions_answered.items():
			# Checks to see if there are questions answered (sometimes canvas messes up)
			if answers:
				temp_time_list = []
				# Builds a list of questions at the time they were answered
				for answer in answers:
					question_time = datetime.datetime(*time.strptime(answer['created_at'].replace("Z", ""),
					                                                 "%Y-%m-%dT%H:%M:%S")[:6])
					temp_time_list.append(question_time)
				# Checks if the time list is bigger than 1
				# (average time between questions isn't able to be found on < 1 example)
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
					average_time = sum(distance_list) / len(distance_list)

				else: average_time = None
				self.data_set[students] = {'average_time': average_time}

		overall_average_time = sum(overall_distance_list) / len(overall_distance_list)
		self.data_set['Overall'] = {'average_time': overall_average_time}

	def _get_user_scores(self):
		pass

	def get_average_question_time(self, user_id='Overall'):
		assert type(user_id) is str, "Data is indexed by {} not {}".format(str, type(user_id))
		try:
			return self.data_set[user_id]
		except KeyError:
			print("It appears there was an ID error, \nAvailable IDs are {}".format(self.data_set.keys()))
			return None
