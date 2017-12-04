import json
import datetime
import time


class QuizEvents:
	def __init__(self, quiz, questions_answered=None):
		self.quiz = quiz
		if not questions_answered: self._get_questions_answered()
		else: self.questions_answered = questions_answered

	def _get_questions_answered(self):
		self.questions_answered = self.quiz.get_quiz_events(questions_answered=True)

	def build_average_question_time(self):
		for students, answers in self.questions_answered.items():
			average_time_dict = {}
			if answers:
				for answer in answers:
					temp_time_list = []
					test = datetime.datetime(*time.strptime(answer['created_at'].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")[:6])
					print(students)
					print(test)
		print(temp_time_list)
