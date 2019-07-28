"""File containing helpers in running the NARC process on data sent from the app.
"""
import hashlib

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class AutoEncoder:
	"""A generic class representing a predesignated autoencoder
	"""
	# TODO: Change so that the AutoEncoder model an be a singleton and the weights are simply reset at each training
	def __init__(self, data_set: np.array):
		self.data_set = data_set
		self.input_layer_size = data_set.shape[1]

	def _scale_data(self) -> None:
		scaler = StandardScaler()
		self.data_set = scaler.fit_transform(self.data_set)

	def _build_model(self) -> None:
		self.model = tf.keras.Sequential()
		self.model.add(tf.keras.layers.Dense(self.input_layer_size, activation="tanh"))
		self.model.add(tf.keras.layers.Dense(10, activation="tanh"))
		self.model.add(tf.keras.layers.Dense(5, activation="tanh"))
		self.model.add(tf.keras.layers.Dense(2, activation="tanh"))
		self.model.add(tf.keras.layers.Dense(5, activation="tanh"))
		self.model.add(tf.keras.layers.Dense(10, activation="tanh"))
		self.model.add(tf.keras.layers.Dense(self.input_layer_size, activation="linear"))

	def _train_model(self) -> np.array:
		self.model.compile(optimizer="adam",
		                   loss="MSE")
		# TODO: Implement shuffling (Maybe)
		self.model.fit(x=self.data_set, y=self.data_set, epochs=5000)
		return self.model.predict(self.data_set)

	def separate(self, hashes) -> tuple:
		self._scale_data()
		self._build_model()
		self._train_model()
		anons = []
		non_anons = []
		predictions = self.model.predict(self.data_set)
		indiv_error = tf.math.reduce_mean(self.data_set - predictions, axis=1)
		avg_error = tf.math.reduce_mean(self.data_set - predictions)
		error_cond = tf.math.greater_equal(indiv_error, avg_error)
		for index, students in enumerate(error_cond.numpy()):
			if students:
				anons.append((index, self.data_set[index]))
			else:
				non_anons.append(hashes[index])
		return anons, non_anons


class KMeansSeparator:
	def __init__(self):
		pass

	def seperate(self, data_set, n_init=1000, n_clusters=2):
		return KMeans(n_init=n_init, n_clusters=n_clusters).fit_predict(data_set)


def returned_tolist(array):
	# key = ""
	# for x in array:
	# 	x = str(x)
	# 	key += x
	# key = hashlib.sha3_256(key).hex
	return array.tolist()


def hasher(cur_row, hashes):
	string = str(cur_row["average_time_between_questions"]) + str(cur_row["time_taken"]) + str(cur_row["page_leaves"])
	hashes.append(hashlib.sha256(string.encode()).hexdigest())


def classify(org_data: pd.DataFrame) -> tuple:
	hashes = []
	hash_data = org_data.drop(["name", "id"], axis=1)

	hash_data.apply(lambda row: hasher(row, hashes), axis=1)
	numpy_data = org_data.loc[list(org_data.index)].drop(["name", "id"], axis=1).values
	predictor = AutoEncoder(numpy_data)
	anon, non_anon = predictor.separate(hashes)
	anon_dict = {}

	actual_anon_pos = 0
	for org_dataset_pos, data in anon:
		data_set_index = list(org_data.index)[org_dataset_pos]
		anon_dict[actual_anon_pos] = {"data": data}
		anon_dict[actual_anon_pos]["name"] = org_data.loc[data_set_index]["name"]
		anon_dict[actual_anon_pos]["id"] = org_data.loc[data_set_index]["id"]
		anon_dict[actual_anon_pos]["org_index"] = org_dataset_pos
		actual_anon_pos += 1

	meanie = KMeansSeparator()

	if len(anon) <= 1:
		return None, None

	classes = meanie.seperate([item[1] for item in anon])

	zeros = []
	ones = []

	for index, classification in enumerate(classes):
		if classification:
			ones.append(index)
		else:
			zeros.append(index)
	print(anon_dict)
	print(org_data)

	# TODO: Testing for zeros and errors coming from that

	one_sum_squared = (sum([org_data.loc[anon_dict[index]["id"], "page_leaves"] for index in ones]) / len(ones)) ** 2
	zero_sum_squared = (sum([org_data.loc[anon_dict[index]["id"], "page_leaves"] for index in zeros]) / len(zeros)) ** 2

	if one_sum_squared > zero_sum_squared:
		# for non_cheat in zeros: non_anon.append((anon_dict[non_cheat]["org_index"], returned_tolist(anon_dict[non_cheat]["data"])))
		for non_cheat in zeros: non_anon.append(hashes[anon_dict[non_cheat]["org_index"]])
		cheat_list = []
		# for cheat in zeros: cheat_list.append((anon_dict[cheat]["org_index"], returned_tolist(anon_dict[cheat]["data"])))
		for cheat in ones: cheat_list.append(hashes[anon_dict[cheat]["org_index"]])
		return cheat_list, non_anon
	elif zero_sum_squared > one_sum_squared:
		# for non_cheat in ones: non_anon.append((anon_dict[non_cheat]["org_index"], returned_tolist(anon_dict[non_cheat]["data"])))
		for non_cheat in ones: non_anon.append(hashes[anon_dict[non_cheat]["org_index"]])
		cheat_list = []
		# for cheat in zeros: cheat_list.append((anon_dict[cheat]["org_index"], returned_tolist(anon_dict[cheat]["data"])))
		for cheat in zeros: cheat_list.append(hashes[anon_dict[cheat]["org_index"]])
		return cheat_list, non_anon
	else:
		return None, None
