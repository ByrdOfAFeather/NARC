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

example_module = Module(url=nccs_url, header=nccs_header, class_id=9713, module_id=8957)


def main():
	start = time.time()

	gatherer = Quiz(quiz_id=10553, url=nccs_url, header=nccs_header, class_id=9713)
	constructor = QuizEvents(gatherer, anon=False)
	dev_set = constructor.build_dataframe()

	print(dev_set)

	jack_walsh = predictors.AutoEncoder(dev_set, dev_set)
	jack_walsh.PCA()

	# Iterates for a obscene amount of times to produce results to analyze [IGNORABLE]
	for i in range(0, 1001):
		test = jack_walsh.separate(learning_rate=.1, epochs=500000, test_thresh=.4)

		test_file = open("temp/classification/{}_{}.txt".format(str(jack_walsh.loss),
		                                                       datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")),
		                 'w')
		omega = predictors.KMeansSeparator(test)
		results = omega.classify(clusters=2, n_init=80000)
		test_file.write(str(results))

		end = time.time()
		test_file.close()

		print("TOTAL {}".format(end - start))


if __name__ == "__main__": main()
