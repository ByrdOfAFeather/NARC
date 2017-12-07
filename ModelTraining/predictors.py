import os
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import StandardScaler
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

time = datetime.utcnow().strftime('%Y%m%d%H%M%S')
log_root = 'logs'
log_name = 'run-{}'.format(time)
log_dir = '{}/{}/'.format(log_root, log_name)


class AutoEncoder:
	def __init__(self, data_set, test_data_set=None):
		self.data_scaler = StandardScaler().fit(data_set)
		self.data_set = self.data_scaler.transform(data_set)
		if len(test_data_set): self.test_index = test_data_set.index.values
		self.test_data_set = self.data_scaler.transform(test_data_set)

	def run(self, learning_rate=.01, layer_1_f=40, layer_2_f=20):
		input_features = self.data_set.shape[1]
		weights = {
			'encoder_h1': tf.Variable(tf.random_normal([input_features, layer_1_f])),
			'encoder_h2': tf.Variable(tf.random_normal([layer_1_f, layer_2_f])),
			'decoder_h1': tf.Variable(tf.random_normal([layer_2_f, layer_1_f])),
			'decoder_h2': tf.Variable(tf.random_normal([layer_1_f, input_features]))
		}

		bias = {
			'encoder_b1': tf.Variable(tf.random_normal([layer_1_f])),
			'encoder_b2': tf.Variable(tf.random_normal([layer_2_f])),
			'decoder_b1': tf.Variable(tf.random_normal([layer_1_f])),
			'decoder_b2': tf.Variable(tf.random_normal([input_features]))
		}

		def encoder(X):
			layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(X, weights['encoder_h1']), bias['encoder_b1']))
			layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['encoder_h2']), bias['encoder_b2']))
			return layer_2

		def decoder(X):
			layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(X, weights['decoder_h1']), bias['decoder_b1']))
			layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['decoder_h2']), bias['decoder_b2']))
			return layer_2

		data = tf.placeholder(dtype=tf.float32, shape=[None, input_features], name='data-set')
		encoder_op = encoder(data)
		decoder_op = decoder(encoder_op)

		y_pred = decoder_op
		y_true = data

		loss = tf.reduce_mean(tf.pow(y_true - y_pred, 2))
		optimizer = tf.train.RMSPropOptimizer(learning_rate=learning_rate).minimize(loss)
		init = tf.global_variables_initializer()

		with tf.Session() as session:
			session.run(init)
			for i in range(0, 1000):
				_, l = session.run([optimizer, loss], feed_dict={data: self.data_set})
				if i % 100 == 0:
					print("STEP {} LOSS {}".format(i, l))
			if self.test_data_set.any:
				for index, items in enumerate(self.test_data_set):
					print("=========USER ID {}=========".format(self.test_index[index]))
					items = np.reshape(items, (1, input_features))
					cur_result = session.run(decoder_op, feed_dict={data: items})
					MSE = session.run(tf.reduce_mean(tf.pow(cur_result - items, 2)))
					print("ACTUAL {}".format(items))
					print("PREDICT {}".format(cur_result))
					print("MEAN SQUARED ERROR {}\n".format(MSE))
