import secrets as sc

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


nccs_token = sc.keys[0]
nccs_url = 'http://nccs.instructure.com'
nccs_header = {'Authorization': 'Bearer {}'.format(nccs_token)}

dev_set = sc.EuroDataSet  # Simple Canvas data set based on a AP Euro History Quiz, Built with QuizEvents


class DataSet:
	"""Highly specialized class used to graph specific canvas data
	"""
	def __init__(self, data_set):
		self.set = data_set

	def question_time_page_leaves_score(self):
		"""Graphs page_leaves by average_time_between_questions by score
		"""
		assert self.set['average_time_between_questions'], \
			"It appears average_time_between_questions is not a feature in this data set! Try rebuilding with it enabled!"
		assert self.set['page_leaves'],\
			"It appears page_leaves is not a feature in this data set! Try rebuilding with it enabled!"

		x = []; y = []; z = []
		fit = plt.figure()
		ax = fit.add_subplot(111, projection='3d')

		for no, items in enumerate(self.set.index.values):
			x.append(self.set.loc[items]['average_time_between_questions'])
			y.append(self.set.loc[items]['page_leaves'])
			z.append(float(self.set.loc[items]['score']) * 100)
			ax.text(s=self.set.index.values[no], x=x[no], y=y[no], z=z[no])

		ax.set_xlabel("Time Between Questions")
		ax.set_ylabel("Time Taken")
		ax.set_zlabel("Score")

		ax.set_title("Page Leaves and Time Taken by Score")

		ax.scatter(x, y, z)
		plt.show()

	def corr_matrix(self):
		"""Gets a correlation matrix from the current data set
		"""
		return self.set.corr()
