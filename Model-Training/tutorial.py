import os
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import fetch_california_housing
from datetime import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

now = datetime.utcnow().strftime('%Y%m%d%H%M%S')
root_logdir = "logs"
logdir = "{}/run-{}/".format(root_logdir, now)

housing = fetch_california_housing()


data_scalar = StandardScaler()
housing.data = data_scalar.fit_transform(housing.data)
m, n = housing.data.shape
housing_data_with_bias = np.c_[np.ones((m, 1)), housing.data]

n_epochs = 100
learning_rate = .01

# X = tf.constant(housing_data_with_bias, dtype=tf.float32, name="X")
# y = tf.constant(housing.target.reshape(-1, 1), dtype=tf.float32, name='y')
X = tf.placeholder(tf.float32, shape=(None, n + 1), name="X")
y = tf.placeholder(tf.float32, shape=(None, 1), name='y')
batch_size = 100
n_batches = int(np.ceil(m/batch_size))
theta = tf.Variable(tf.random_uniform([n + 1, 1], -1, -1), name="theta")

y_pred = tf.matmul(X, theta, name='predictions')
with tf.name_scope("loss") as scope:
	error = y_pred - y
	mse = tf.reduce_mean(tf.square(error), name='mse')
# gradients = 2/m * tf.matmul(tf.transpose(X), error)
# gradients = tf.gradients(mse, [theta])[0]
optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
# training_op = optimizer.minimize(mse)
minimizeOP = optimizer.minimize(mse)
saver = tf.train.Saver()
mse_summary = tf.summary.scalar('MSE', mse)
file_writer = tf.summary.FileWriter(logdir, tf.get_default_graph())
init = tf.global_variables_initializer()


def fetch_batch(epoch, batch_index, batch_size):
	batch_index *= 100
	endex = batch_index + batch_size
	if endex == 0: endex = 100
	X_batch = housing_data_with_bias[batch_index:endex]
	y_batch = housing.target.reshape(-1, 1)[batch_index:endex]
	return X_batch, y_batch


with tf.Session() as xd:
	xd.run(init)

	for epoch in range(n_epochs):
		for batch_index in range(n_batches):
			X_batch, y_batch = fetch_batch(epoch, batch_index, batch_size)
			xd.run(minimizeOP, feed_dict={X: X_batch, y: y_batch})
			if batch_index % 5 == 0:
				summary_str = mse_summary.eval(feed_dict={X: X_batch, y: y_batch})
				step = epoch * n_batches + batch_index
				file_writer.add_summary(summary_str, step)
	best_theta = theta.eval()
	# save_path = saver.save(xd, '/tmp/my_model_final.ckpt')
	print(best_theta)
file_writer.close()