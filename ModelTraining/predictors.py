import os
import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

if not os.path.exists(r'..\.\temp'):
	os.makedirs(r'..\.\temp')

if not os.path.exists(r'..\.\temp/model_info'):
	os.makedirs(r'..\.\temp/model_info')

if not os.path.exists(r'..\.\temp/model_info/results'):
	os.makedirs(r"..\.\temp/model_info/results")

if not os.path.exists(r'..\.\temp/model_info/classification'):
	os.makedirs(r'..\.\temp/model_info/classification')

temp_dir = r'..\.\temp/model_info'

class AutoEncoder:
	"""Main class for implementing a AutoEncoder into Tensor flow
	"""
	def __init__(self, data_set, test_data_set=None):
		self.data_scaler = StandardScaler().fit(data_set)
		self.data_set = self.data_scaler.transform(data_set)
		if len(test_data_set): self.test_index = test_data_set.index.values
		self.test_data_set = self.data_scaler.transform(test_data_set)
		self.loss = None
		self.org_loss = None

	def PCA(self):
		"""Automatically preforms a optional PCA on the input data set
		:return: a data set scaled down using sci-kit learn's implementation of PCA
		"""
		self.data_set = PCA().fit_transform(X=self.data_set)

	@staticmethod
	def _get_anomalies(anomaly_rates, test_thresh=0.0):
		"""Gets anomalies based on user threshold
		:param anomaly_rates: the anomalies and their respective errors (indexer, error, data)
		:param test_thresh: by default set to the average of the anomaly rates, otherwise, user set
		:return: list of anomalies
		"""
		if not test_thresh: test_thresh = sum([i[1] for i in anomaly_rates]) / len(anomaly_rates)
		else: test_thresh = test_thresh
		print("THIS IS THE TEST THRESHOLD : {}".format(test_thresh))
		anomalies = []
		for items in anomaly_rates:
			if items[1] >= test_thresh:
				del items[1]  # Gets rid of the error to output the data with the index and original data
				anomalies.append(items)
		return anomalies

	def separate(self, learning_rate=.08, layer_1_f=10, layer_2_f=5, layer_3_f=2,
	        epochs=800000, test_thresh=.1, test=True, labelvar=None, controller=None):
		"""Separates non-anomalous data from anomalous data
		:param learning_rate: Learning rate for Adagradoptimizer (implemented from Tensor flow)
		:param layer_1_f: The number of neurons in the first hidden layer
		:param layer_2_f: The number of neurons in the second hidden layer
		:param layer_3_f: The number of neurons in the third hidden layer
		:param epochs: The number of iterations to preform Adagradoptimization
		:param test_thresh: The threshold by which to classify anomalies
		:param test: If the test set should be used
		:return: A list of anomalies (index, data)
		"""
		anomaly_list = []
		time = datetime.now().strftime("%Y-%m-%d T-%H-%M-%S")
		log_name = 'run-{}'.format(time)
		log_dir = '{}/logs/{}/'.format(temp_dir, log_name)

		input_features = self.data_set.shape[1]

		weights = {
			'encoder_h1': tf.Variable(tf.random_normal([input_features, layer_1_f]), name="encoder_h1"),
			'encoder_h2': tf.Variable(tf.random_normal([layer_1_f, layer_2_f]), name="encoder_h2"),
			'encoder_h3': tf.Variable(tf.random_normal([layer_2_f, layer_3_f]), name="encoder_h3"),
			'decoder_h1': tf.Variable(tf.random_normal([layer_3_f, layer_2_f]), name="decoder_h1"),
			'decoder_h2': tf.Variable(tf.random_normal([layer_2_f, layer_1_f]), name="decoder_h2"),
			'decoder_h3': tf.Variable(tf.random_normal([layer_1_f, input_features]), name="decoder_h3")
		}

		bias = {
			'encoder_b1': tf.Variable(tf.zeros([layer_1_f]), name="encoder_b1"),
			'encoder_b2': tf.Variable(tf.zeros([layer_2_f]), name="encoder_b2"),
			'encoder_b3': tf.Variable(tf.zeros([layer_3_f]), name="encoder_b3"),
			'decoder_b1': tf.Variable(tf.zeros([layer_2_f]), name="decoder_b1"),
			'decoder_b2': tf.Variable(tf.zeros([layer_1_f]), name="decoder_b2"),
			'decoder_b3': tf.Variable(tf.zeros([input_features]), name="decoder_b3")
		}

		# Hyperbolic tangent activation functions representing the first three layers and encoder section
		def encoder(X):
			layer_1 = tf.nn.tanh(tf.add(tf.matmul(X, weights['encoder_h1']), bias['encoder_b1']),
			                     name="en_layer_1")
			layer_2 = tf.nn.tanh(tf.add(tf.matmul(layer_1, weights['encoder_h2']), bias['encoder_b2']),
			                     name="en_layer_2")
			layer_3 = tf.nn.tanh(tf.add(tf.matmul(layer_2, weights['encoder_h3']), bias['encoder_b3']),
			                     name="en_layer_3")
			return layer_3

		# Hyperbolic tangent activation functions and linear layer representing the last three layers and decoder section
		def decoder(X):
			layer_1 = tf.nn.tanh(tf.add(tf.matmul(X, weights['decoder_h1']), bias['decoder_b1']),
			                     name="de_layer_1")
			layer_2 = tf.nn.tanh(tf.add(tf.matmul(layer_1, weights['decoder_h2']), bias['decoder_b2']),
			                     name="de_layer_2")
			# Linear Layers due to AutoEncoder being a regression task
			layer_3 = tf.add(tf.matmul(layer_2, weights['decoder_h3']), bias['decoder_b3'],
			                 name="de_layer_3")
			return layer_3

		data = tf.placeholder(dtype=tf.float32, shape=[None, input_features], name='data-set')
		encoder_op = encoder(data)
		decoder_op = decoder(encoder_op)

		y_pred = decoder_op
		y_true = data

		loss = tf.reduce_mean(tf.pow(y_true - y_pred, 2), name="loss")
		optimizer = tf.train.AdagradOptimizer(learning_rate=learning_rate).minimize(loss)
		init = tf.global_variables_initializer()

		loggart_scaler = tf.summary.scalar("MSE", loss)
		loggart = tf.summary.FileWriter(log_dir, tf.get_default_graph())

		with tf.Session() as session:
			session.run(init)

			def train(x, log=False):
				for i in range(0, epochs):
					_, self.loss = session.run([optimizer, loss], feed_dict={data: x})

					if i % 100 == 0:
						print("STEP {} LOSS {}".format(i, self.loss))

						# GUI Updates at iterations
						if labelvar is not None:
							labelvar.set("Current Loss: {}\n"
							             "{} Iterations Left\n"
							             "Learning Rate: {}\n"
							             "Threshold: {}\n"
										 "This will take a lot of processing power!".format(self.loss, epochs - i, learning_rate, test_thresh))
							controller.update()

							if i == epochs - 1:
								labelvar.set("Training Finished!")
								controller.update()

						if log:
							summary_str = loggart_scaler.eval(feed_dict={data: x})
							loggart.add_summary(summary_str, i)
							self.org_loss = self.loss

			train(self.data_set, log=True)
			if test:
				anomaly_rates = []
				ex = open('{}/results/results_{}_{}.txt'.format(temp_dir, time, self.loss), 'w')
				ex.write("Layer 1: {} Layer 2: {} Layer 3: {}\n "
				         "Learning Rate {} Threshold {} Loss {}\n"
				         "Epochs {}\n".format(layer_1_f, layer_2_f, layer_3_f,
				                           learning_rate, test_thresh,
				                           self.loss, epochs)
				         )
				ex.write("Weights {}\n".format(session.run(weights)))
				ex.write("Bias {}\n".format(session.run(bias)))
				ex.write("===================================\n")
				ex.write("{\n")
				for index, items in enumerate(self.test_data_set):
					user_id = self.test_index[index]

					print("USER ID {}".format(user_id))

					point = np.reshape(items, (1, input_features))
					cur_result = session.run(decoder_op, feed_dict={data: point})
					MSE = session.run(tf.reduce_mean(tf.pow(cur_result - point, 2)))

					print("Anomaly MSE {}".format(MSE))
					anomaly_rates.append([user_id, MSE, items])
					ex.write("{}:".format(user_id))
					ex.write(" {}\n\n".format(MSE))
				ex.write("}")
				anomaly_list = self._get_anomalies(anomaly_rates, test_thresh=test_thresh)
				ex.close()
			loggart.close()
		return anomaly_list


class KMeansSeparator:
	"""Main class representing an implementation of SKLearn's KMEANS algorithm
	"""
	def __init__(self, data_set, scale=False):
		self.data_set = data_set
		self.scale = scale
		if scale:
			self.data_set_index = self.data_set.index.values
			self.scaler = StandardScaler().fit(self.data_set)
			self.data_set = self.scaler.transform(self.data_set)
		else: pass

	def classify(self, n_init=1000, clusters=2):
		"""Classification function written specifically for Canvas LMS data sets
		:param n_init: Number of time clustering algorithm initializes its self
		:param clusters: Number of classes to be separated into
		:return: Dictionary containing index: original data | (including predicted class)
		"""
		classifier = KMeans(n_clusters=clusters, n_init=n_init)
		results_dict = {}
		if self.scale:
			classifier.fit_transform(self.data_set)
			for index, values in enumerate(self.data_set):
				print(values)
				point = np.reshape(values, (1, -1))
				cur_prediction = classifier.predict(point)
				cur_user = self.data_set_index[index]
				results_dict[cur_user] = cur_prediction
		else:
			data_dict = {}
			for user_id, data in self.data_set:
				data_dict[user_id] = data

			data_dict = pd.DataFrame.from_dict(data_dict, orient='index')
			results_dict = data_dict.copy()

			classifier.fit_transform(data_dict)
			indexs = data_dict.index.values

			for index in range(0, len(data_dict)):
				cur_index = indexs[index]
				items = data_dict.loc[cur_index]
				point = np.reshape(items, (1, -1))
				predict = classifier.predict(point)
				results_dict.at[cur_index, 'Class'] = predict

		return results_dict
