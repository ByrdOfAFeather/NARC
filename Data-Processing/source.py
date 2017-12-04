"""Data Analysis
"""
# Created on Tues. October 17 11:05:37 2017 
# Main file for data analytics
# @author: ByrdOfAFeather

from collectors import *
from constructors import *
from secrets import keys


nccs_token = keys[0]
nccs_url = 'http://nccs.instructure.com'
nccs_header = {'Authorization': 'Bearer {}'.format(nccs_token)}

example_module = Module(url=nccs_url, header=nccs_header, class_id=9360, module_id=8803)


def main():
	quiz_list = []
	for quizzes in example_module.get_module_items()['Subsections']['Quizzes']:
		quiz_list.append(Quiz(quizzes, url=nccs_url, header=nccs_header, class_id=9360))
	quiz_events_data = []
	for quiz_objects in quiz_list:
		print("QUIZ OBJECTS: {}".format(quiz_objects))
		QuizEvents(quiz_objects).build_average_question_time()


if __name__ == "__main__": main()
