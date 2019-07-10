import tensorflow as tf
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


class AutoEncoder:
	"""Basic Autoencoder class
	:param data_set: should be a numpy array
	"""
	def __init__(self, data_set):
		self.data_set = data_set
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
		self.decode.fit(x=self.data_set, y=self.data_set, epochs=1000)
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
				anons.append((index, self.data_set[index]))
			else:
				non_anons.append((index, self.data_set[index].tolist()))
		return anons, non_anons


class KMeansSeparator:
	def __init__(self):
		pass

	def seperate(self, data_set, n_init=1000, n_clusters=2):
		return KMeans(n_init=n_init, n_clusters=n_clusters).fit_predict(data_set)


def returned_tolist(array):
	return array.tolist()


def classify(org_data):
	numpy_data = org_data.loc[list(org_data.index)].drop(["name", "id"], axis=1).values
	predictor = AutoEncoder(numpy_data)
	anon, non_anon = predictor.separate()
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
		for non_cheat in zeros: non_anon.append((anon_dict[non_cheat]["org_index"], returned_tolist(anon_dict[non_cheat]["data"])))
		cheat_list = []
		for cheat in zeros: cheat_list.append((anon_dict[cheat]["org_index"], returned_tolist(anon_dict[cheat]["data"])))
		return cheat_list, non_anon
	elif zero_sum_squared > one_sum_squared:
		for non_cheat in ones: non_anon.append((anon_dict[non_cheat]["org_index"], returned_tolist(anon_dict[non_cheat]["data"])))
		cheat_list = []
		for cheat in zeros: cheat_list.append((anon_dict[cheat]["org_index"], returned_tolist(anon_dict[cheat]["data"])))
		return cheat_list, non_anon
	else:
		return None, None
