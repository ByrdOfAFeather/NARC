"""Data Analysis
"""
# Created on Tues. October 17 11:05:37 2017 
# Main file for data analytics
# @author: ByrdOfAFeather


from collectors import *
from constructors import *
from secrets import keys
from ModelTraining import predictors

nccs_token = keys[0]
nccs_url = 'http://nccs.instructure.com'
nccs_header = {'Authorization': 'Bearer {}'.format(nccs_token)}

example_module = Module(url=nccs_url, header=nccs_header, class_id=9709, module_id=8894)


def main():
	quiz_list = []
	for quizzes in example_module.get_module_items()['Subsections']['Quizzes']:
		quiz_list.append(Quiz(quizzes, url=nccs_url, header=nccs_header, class_id=9709))
	start = time.time()

	gatherer = quiz_list[0]
	constructor = QuizEvents(gatherer, anon=False)
	dev_set = constructor.build_dataframe()
	print(dev_set)
	jack_walsh = predictors.AutoEncoder(dev_set, dev_set)
	jack_walsh.run(layer_1_f=40, layer_2_f=35, learning_rate=.1, epochs=30000, test_thresh=.2)
	end = time.time()

	print("TOTAL {}".format(end - start))


if __name__ == "__main__": main()
