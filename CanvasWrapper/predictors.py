import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd


class AutoEncoder:
	"""Basic Autoencoder class
	:param data_set: should be a numpy array
	"""
	def __init__(self, data_set):
		self.data_set = tf.constant(data_set, dtype=tf.float32, shape=[numpy_data.shape[0], numpy_data.shape[1]])
		self.input_layer_size = data_set.shape[1]

	def _scale_data(self):
		scaler = StandardScaler()
		self.data_set = scaler.fit_transform(self.data_set)

	def _build_model(self):
		self.decode = tf.keras.Sequential()
		self.decode.add(tf.keras.layers.Dense(self.input_layer_size, activation="tanh"))
		self.decode.add(tf.keras.layers.Dense(10, activation="tanh"))
		self.decode.add(tf.keras.layers.Dense(5, activation="tanh"))
		self.decode.add(tf.keras.layers.Dense(2, activation="tanh"))
		self.decode.add(tf.keras.layers.Dense(5, activation="tanh"))
		self.decode.add(tf.keras.layers.Dense(10, activation="tanh"))
		self.decode.add(tf.keras.layers.Dense(self.input_layer_size, activation="linear"))

	def _train_model(self):
		self.decode.compile(optimizer="adam",
		                    loss="MSE")
		# TODO: Implement shuffling
		self.decode.fit(x=self.data_set, y=self.data_set, epochs=10000)
		return self.decode.predict(self.data_set)

	def separate(self):
		self._scale_data()
		self._build_model()
		self._train_model()
		anons = []
		non_anons = []
		predictions = self.decode.predict(self.data_set)
		indiv_error = tf.math.reduce_mean(self.data_set - predictions, axis=1)
		avg_error = tf.math.reduce_mean(self.data_set - predictions)
		error_cond = tf.math.greater_equal(indiv_error, avg_error)
		for index, students in enumerate(error_cond.numpy()):
			if students:
				anons.append(self.data_set[index])
			else:
				non_anons.append(self.data_set[index])
		return anons, non_anons


class KMeans:
	def __init__(self):
		pass

	def separate(self):
		pass


tester = pd.DataFrame.from_dict(data={"24095915": {"average_time_between_questions": 1000, "time_taken": 5, "page_leaves": 0.0, "name": "Test Student",
	              "id": "24095915"},
	 "24120424": {"average_time_between_questions": 2000.0, "time_taken": 5, "page_leaves": 1.0,
	              "name": "Tester Baxter", "id": "24120424"},
	 "24125413": {"average_time_between_questions": 4250.0, "time_taken": 23, "page_leaves": 3.0,
	              "name": "Sora Ultimate", "id": "24125413"},
	 "24125422": {"average_time_between_questions": 2750.0, "time_taken": 34, "page_leaves": 4.0, "name": "Rico",
	              "id": "24125422"}}, orient="index")

numpy_data = tester.loc[list(tester.index)].drop(["name", "id"], axis=1).values
tensor = tf.constant(numpy_data, dtype=tf.float32, shape=[numpy_data.shape[0], numpy_data.shape[1]])
print(tensor)

predictor = AutoEncoder(tensor)
anon, non_anon = predictor.separate()
