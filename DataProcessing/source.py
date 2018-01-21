"""Data Analysis
"""
# Created on Tues. October 17 11:05:37 2017 
# Main file for data analytics
# @author: ByrdOfAFeather

from collectors import *
from constructors import *
from secrets import keys, EuroDataSet, PsychDataSet
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
import numpy as np
from pandas.tools.plotting import scatter_matrix
import matplotlib.pyplot as plt
from ModelTraining import predictors

nccs_token = keys[0]
nccs_url = 'http://nccs.instructure.com'
nccs_header = {'Authorization': 'Bearer {}'.format(nccs_token)}


def main():

	EuroDataSet.dropna(axis=0, how='any', inplace=True)
	print(EuroDataSet)
	stds = []
	for items in EuroDataSet.columns.values:
		stds.append(np.std(EuroDataSet[items]))
	print(stds)

	PsychDataSet.dropna(axis=0, how='any', inplace=True)
	print(PsychDataSet)

	# print(EuroDataSet)
	# EuroDataSetFeatures = EuroDataSet.drop("Cheat", axis=1)
	# result = SelectKBest(f_classif, k=4).fit_transform(EuroDataSetFeatures, EuroDataSet['Cheat'])
	# print(result)
	# print(EuroDataSet.corr())

	# print(PsychDataSet)
	# PsychDataSetFeatures = PsychDataSet.drop("Cheat", axis=1)
	# result = SelectKBest(f_classif, k=4).fit_transform(PsychDataSetFeatures, PsychDataSet['Cheat'])
	# print(result)
	# print(PsychDataSet.corr())

	# start = time.time()
	#
	# gatherer = Quiz(class_id=9713, quiz_id=10553, url=nccs_url, header=nccs_header)
	# constructor = QuizEvents(gatherer, anon=False)
	# dev_set = constructor.build_dataframe()
	#
	# print(dev_set)
	#
	# jack_walsh = predictors.AutoEncoder(dev_set, dev_set)
	# jack_walsh.PCA()
	#
	# test_thresh = .1
	# n_init = 500000
	# learning_rate = .08
	#
	# # Iterates for a obscene amount of times to produce results to analyze [IGNORABLE]
	# for i in range(0, 1001):
	# 	test = jack_walsh.separate(learning_rate=learning_rate, test_thresh=test_thresh)
	# 	print(test)
	# 	test_file = open(r"..\.\temp/model_info/classification/classification_{}_{}.txt".format(
	# 																datetime.datetime.now().strftime("%Y-%m-%d T-%H-%M-%S"),
	# 																str(jack_walsh.loss)),
	# 		'w', encoding='utf-8')
	#
	# 	omega = predictors.KMeansSeparator(test)
	# 	results = omega.classify(clusters=2, n_init=n_init)
	#
	# 	class0 = results[results['Class'] == 0]
	# 	class1 = results[results['Class'] == 1]
	# 	class0_page_leaves = class0[2]
	# 	class1_page_leaves = class1[2]
	#
	# 	class0_average_page_leaves = (sum(class0_page_leaves) / len(class0_page_leaves)) ** 2
	# 	class1_average_page_leaves = (sum(class1_page_leaves) / len(class1_page_leaves)) ** 2
	#
	# 	results['Temp'] = None
	#
	# 	if class0_average_page_leaves > class1_average_page_leaves:
	# 		results.loc[results['Class'] == 1, 'Temp'] = 0
	# 		results.loc[results['Class'] == 0, 'Temp'] = 1
	#
	# 		results.loc[results['Temp'] == 1, 'Class'] = 1
	# 		results.loc[results['Temp'] == 0, 'Class'] = 0
	#
	# 	results['Actual'] = EuroDataSet['Cheat']
	# 	results.Actual = results.Actual.astype(float)
	# 	results['Result'] = None
	#
	# 	false_negative = len(results[(results['Class'] == 0) & (results['Actual'] == 1)])
	# 	print(results[(results['Class'] == 0) & (results['Actual'] == 1)])
	# 	results.loc[(results['Class'] == 0) & (results['Actual'] == 1), 'Result'] = u'❌'
	# 	false_positive = len(results[(results['Class'] == 1) & (results['Actual'] == 0)])
	# 	results.loc[(results['Class'] == 1) & (results['Actual'] == 0), 'Result'] = u'❌'
	# 	true_positive = len(results[(results['Class'] == 1) & (results['Actual'] == 1)])
	# 	results.loc[(results['Class'] == 1) & (results['Actual'] == 1), 'Result'] = u'✓'
	# 	true_negative = len(results[(results['Class'] == 0) & (results['Actual'] == 0)])
	# 	results.loc[(results['Class'] == 0) & (results['Actual'] == 0), 'Result'] = u'✓'
	#
	# 	indexers = EuroDataSet.index.values
	# 	missed_cheaters = 0; missed_non_cheaters = 0
	# 	for items in indexers:
	# 			try: results.loc[items, 'Class']
	# 			except KeyError:
	# 				did_cheat = EuroDataSet.loc[items, 'Cheat']
	# 				if did_cheat == 0:
	# 					missed_non_cheaters += 1
	# 					true_negative += 1
	# 				elif did_cheat == 1:
	# 					missed_cheaters += 1
	# 					false_negative += 1
	#
	# 	test_file.write("THRESHOLD FOR TESTING : {}\n".format(test_thresh))
	# 	test_file.write("EPOCHS : {}\n".format(500000))
	# 	test_file.write("LEARNING RATE : {}\n".format(learning_rate))
	# 	test_file.write("N_INIT : {}\n".format(n_init))
	# 	test_file.write(u"{}".format(str(results)))
	# 	test_file.write('\n\n\n')
	# 	test_file.write("TRUE POSITIVES {} FALSE POSITIVES {}\n".format(true_positive, false_positive))
	# 	test_file.write("TRUE NEGATIVES {} FALSE NEGATIVES {}\n".format(true_negative, false_negative))
	# 	test_file.write("MISSED CHEATERS AS ANOMALIES {}\n".format(missed_cheaters))
	# 	test_file.write("MISSED NON-CHEATERS AS ANOMALIES {}\n".format(missed_non_cheaters))
	#
	# 	end = time.time()
	# 	test_file.close()
	#
	# 	print("TOTAL {}".format(end - start))


if __name__ == "__main__": main()
