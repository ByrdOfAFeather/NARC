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
		average_time_dict = {}
		for students, answers in self.questions_answered.items():
			if answers:
				temp_time_list = []
				for answer in answers:
					question_time = datetime.datetime(*time.strptime(answer['created_at'].replace("Z", ""), "%Y-%m-%dT%H:%M:%S")[:6])
					temp_time_list.append(question_time)
				if len(temp_time_list) > 1:
					print(temp_time_list[0].time() - temp_time_list[1].time())
				average_time_dict[students] = temp_time_list


