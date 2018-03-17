"""Machine Learning Displayers
A collection of classes that serve as stacked frames for the main GUI all related to the machine learning
aspect of the project.
"""

import tkinter as tk
import tkinter.ttk as ttk
from ModelTraining import predictors
from DataProcessing import constructors


class ResultsMenu(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.controller = controller

	def place_holder(self):
		pass


class DevSettingsMenu(tk.Frame):
	"""Menu to set hyper parameters for Auto Encoder
	"""
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.controller = controller

		self.learning_rate_input = None
		self.threshold_input = None
		self.epochs_input = None

		self.current_learning_rate = None
		self.threshold_input = None
		self.epochs_input = None

		self.options_buttons = None

	def init_gui(self):
		"""Sets up input for hyper parameters and their default values, along with a warning
		"""
		# Styles label to make it look red and menacing

		for widget in self.winfo_children():
			widget.pack_forget()
			widget.destroy()

		style = ttk.Style()
		style.configure('R.TLabel', foreground='red')
		overall_label = ttk.Label(self, text="WARNING THESE ARE DEVELOPER OPTIONS, IF YOU DON'T KNOW WHAT THESE DO, "
		                                     "YOU MAY NOT WANT TO EDIT THESE!", style='R.TLabel')
		overall_label.grid(row=0, column=0)

		# Sets up learning rate input and gets the default value from predictors.AutoEncoder
		self.learning_rate_input = ttk.Entry(self, width=50)
		self.learning_rate_input.insert(tk.END, predictors.AUTOENCODER_DEFAULTS['learning_rate'])
		learning_rate_label = ttk.Label(self, text="Learning Rate: ")
		learning_rate_label.grid(row=1, column=0)
		self.learning_rate_input.grid(row=1, column=1)

		# Sets up threshold_input and gets the default value from predictors.AutoEncoder
		self.threshold_input = ttk.Entry(self, width=50)
		self.threshold_input.insert(tk.END, predictors.AUTOENCODER_DEFAULTS['test_thresh'])
		threshold_label = ttk.Label(self, text="Threshold for separation by MSE: ")
		threshold_label.grid(row=2, column=0)
		self.threshold_input.grid(row=2, column=1)

		# Sets up epochs_input and gets the default value from predictors.AutoEncoder
		self.epochs_input = ttk.Entry(self, width=50)
		self.epochs_input.insert(tk.END, predictors.AUTOENCODER_DEFAULTS['epochs'])
		epochs_label = ttk.Label(self, text="Epochs (Iterations): ")
		epochs_label.grid(row=3, column=0)
		self.epochs_input.grid(row=3, column=1)

		# Sets up a confirm button
		confirm_button = ttk.Button(self, text='Confirm!', command=self.params_config)
		confirm_button.grid()

		self.options_buttons = {
			'Changed Questions': tk.IntVar(),
			'Average Question Time': tk.IntVar(),
			'User Scores': tk.IntVar(),
			'Time Taken': tk.IntVar(),
			'Page Leaves': tk.IntVar(),
			'Difficulty Index': tk.IntVar()
		}

		check_list = [ttk.Checkbutton(self, text=text, var=var) for text, var in self.options_buttons.items()]

		for col_i, buttons in enumerate(check_list):
			buttons.grid(row=col_i + 1, column=2, columnspan=2, sticky='w')

	def params_config(self):
		"""Sets up parameters to pass to the AutoEncoder
		This function finds all the values that can be converted to float (except epochs that has to be converted to
		int because of the restrictions in Python's built in range() function). It then passes all the valid values
		as **kwargs to the controller special autoencoder_frame function which acts similar to the change_frame() function
		but only changes to the Auto Encoder frame instead of all frames and accepts **kwargs. The **kwargs are then
		passed into the AutoEncoderSettings from the autoencoder_frame function, to later be used in a method call
		to the .separate() method of AutoEncoder().

		While predictors.AutoEncoder().separate doesn't explicitly accept **kwargs, the dictionary does match up with
		the parameter names in the function signature, which allows it to be passed. This is helpful as it makes it
		not need to call the function a different way if one of these values is not able to be cast to a float, that
		value will just be removed when the function is called

		to illustrate:
		let's say:

		learning_rate = "Test"
		test_thresh = 1
		epochs = 1

		without using a dictionary, this would pass these values like so:

		if 'learning_rate' in params:
			AutoEncoder().separate(test_thresh=1, epochs=1)
		elif 'learning_rate' in params and 'epochs' not in params:
			AutoEncoder().separate(test_thresh=1)

		etc
		"""
		# Names here match up with AutoEncoder.separate() parameters
		current_input = {'learning_rate': self.learning_rate_input.get(),
		                 'test_thresh': self.threshold_input.get(),
		                 'epochs': self.epochs_input.get()}
		kwargs = {}
		for index, values in current_input.items():
			# Makes sure the values can be cast to float
			try:
				float(values)
			except ValueError:
				continue

			# epochs must be a int value
			if index == 'epochs':
				kwargs[index] = int(values)
			else:
				kwargs[index] = float(values)

		options = []
		for index in self.options_buttons.keys():
			if self.options_buttons[index].get():
				options.append(index)
		self.controller.autoencoder_frame(options, **kwargs)


class AutoEncoderSettingsMenu(tk.Frame):
	"""Menu for tensorflow settings, effected heavily by DevSettingsMenu
	"""
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.controller = controller

		self.quiz = None
		self.quiz_constructor = None
		self.data_set = None
		self.pre_flags = None
		self.labelvar = None

		self.start_button = None
		self.view_data_button = None
		self.data_window = None

		self.params = None
		self.data_options = None

		self.built_data_set = False
		self.previous_options = None
		self.previous_course = None

	def build_data_set(self):
		"""Builds data set
		Sets up the pre_flags which are cheaters pre separated based on unreasonable values in page_leaves
		"""
		self.previous_course = self.controller.cur_quiz.class_id
		self.quiz = self.controller.cur_quiz
		self.quiz_constructor = constructors.QuizEvents(self.quiz, self.data_options, False, True, self)
		data_sets = self.quiz_constructor.build_dataframe()
		self.pre_flags = data_sets[0]
		self.data_set = data_sets[1]
		self.labelvar.set("Data Set Built.")
		self.built_data_set = True

	def init_gui(self, data_options, **kwargs):
		"""Initializes GUI for Tensorflow start menu
		:param kwargs: Arguments passed to override the default values of the AutoEncoder. These come from the DevSettingsMenu
		"""
		self.previous_options = self.data_options

		if len(data_options):
			self.data_options = data_options
		else:
			if self.controller.separation_type == 'No Exceptions':
				self.data_options = ['Page Leaves']
			else:
				self.data_options = ['Average Question Time', 'Time Taken', 'Page Leaves']
		self.params = kwargs

		self.built_data_set = 1 if self.previous_options == self.data_options else 0

		# Resets the menu
		for widget in self.winfo_children():
			widget.pack_forget()
			widget.destroy()

		self.labelvar = tk.StringVar(self)
		label = ttk.Label(self, textvar=self.labelvar)
		label.grid(sticky='nsew', columnspan=10)

		# Checks if the data set is built or if the quiz has changed since the last build
		if not self.built_data_set or self.previous_course != self.controller.cur_quiz.class_id:
			self.labelvar.set("Building Data Set!")

			self.controller.update()

			self.build_data_set()

		else:
			self.labelvar.set("Data Set Built!")

		# Opens dev settings menu if Ctrl + F12 is pressed
		self.controller.bind('<Control-F12>', lambda _: self.controller.change_frame('DevSettingsMenu'))

		self.start_button = ttk.Button(self, text="Start Separation Process!", command=self.start_separator)
		self.start_button.grid(sticky='nsew')

	def start_separator(self):
		"""Simple function to check for what type of separation the user wants to do
		"""
		if self.controller.separation_type == 'Auto Encoder':
			self.start_autoencoder()

			# Sets up the view data button
			self.view_data_button = ttk.Button(self, text="View Data!", command=self.open_data_window)
			self.view_data_button.grid(sticky='nsew')

		elif self.controller.separation_type == 'Basic Anomaly':
			self.start_basic_anomaly()

			# Sets up the view data button  
			self.view_data_button = ttk.Button(self, text="View Data!", command=self.open_data_window)
			self.view_data_button.grid(sticky='nsew')

		elif self.controller.separation_type == 'No Exceptions':
			self.start_no_exception()

	def open_data_window(self):
		"""Displays the current data set in a new window, with data summaries"""
		self.view_data_button.grid_forget()
		self.view_data_button.destroy()

		self.data_window = tk.Toplevel()
		c = 0
		for cols in self.data_set.columns.values:
			c += 1
			col_label = ttk.Label(self.data_window, text="{} ".format(cols))
			col_label.grid(row=0, column=c)

		i, j = 0, 0
		for index in self.data_set.index.values:
			i += 1
			j = 0
			cur_index_label = ttk.Label(self.data_window, text="{}".format(index))
			cur_index_label.grid(row=i, column=0)
			for values in self.data_set.loc[index]:
				j += 1
				cur_value_label = ttk.Label(self.data_window, text='{}'.format(values))
				cur_value_label.grid(row=i, column=j)

	def start_autoencoder(self):
		"""Starts the process of separating the data through a autoencoder.

		This function relies on the automatically separated cheaters from the data-set. These cheaters are people
		who have a extremely high number of page leaves when the data set is built. The are separated into the pre-flags
		dataframe, which contains their index and information. These are then added back into the menu, already flagged
		as cheaters. They are found by comparing the index of the original data_set that is fed into the autoencoder and
		the index of the pre_flag. If a item is in pre_flag but not in the original data_set, then it is labeled as a
		positive for cheating.
		"""
		self.built_data_set = False

		# Resets the start button if it already exists (Returning from DevSettings Menu or by Selecting Another Quiz)
		self.start_button.grid_forget()
		self.start_button.destroy()

		# Sets a default value for the temp_back_button
		temp_back_button = None

		# Creates a auto encoder object
		self.labelvar.set("Starting AutoEncoder!")
		self.controller.update()
		jack_walsh = predictors.AutoEncoder(self.data_set, self.data_set)

		if self.params:
			# if parameters are passed when called the function, pass them into separate
			output = jack_walsh.separate(labelvar=self.labelvar, controller=self.controller, **self.params)
		else:
			# otherwise, use the default function
			output = jack_walsh.separate(labelvar=self.labelvar, controller=self.controller)

		# Starts the clustering algorithm (won't start until the separation finishes)
		self.labelvar.set("Starting Clustering Algorithm!")
		self.controller.update()
		omega = predictors.KMeansSeparator(output)
		results = omega.classify(clusters=2, n_init=50000)

		# outputs the cheaters
		self.labelvar.set("DO NOT TAKE AT FACE VALUE")
		self.display_autoencoder_outputs(results)

	def display_autoencoder_outputs(self, results):
		"""Sets up the display with outputs from the KMeansSeparator function
		:param results: return value of KMeansSeparator.classify() function
		"""

		temp_back_button = None

		# Gets a series where the class is equal to 1 or 0
		class0 = results[results['Class'] == 0]
		class1 = results[results['Class'] == 1]

		# Gets non-scaled versions of page_leaves values
		class0_page_leaves = self.data_set.loc[class0.index.values]['page_leaves']
		class1_page_leaves = self.data_set.loc[class1.index.values]['page_leaves']

		# Adds pre flagged users to the results for display purposes, as well as removes irrelevant overhead from the
		# pre flags
		results = results.append(self.pre_flags)
		results.drop(['average_time_between_questions', 'time_taken'], axis=1, inplace=True)

		# Gets the average page leave amount from both classes
		class0_average_page_leaves = (sum(class0_page_leaves) / len(class0_page_leaves))
		class1_average_page_leaves = (sum(class1_page_leaves) / len(class1_page_leaves))

		# Finds where ever the pre-flags are cheaters and labels them accordingly
		results.loc[(results['page_leaves'] == 'CA'), 'Cheat'] = u'✓'
		# The class is a outlier as it shouldn't be included in the separation, since these values where not considered
		# in the original separation
		results.loc[(results['page_leaves'] == 'CA'), 'Class'] = 2

		# if the average page leaves is higher, set that class to the cheater class and the other to the non-cheater
		# class
		if class0_average_page_leaves > class1_average_page_leaves:
			results.loc[(results['Class'] == 0), 'Cheat'] = u'✓'
			results.loc[(results['Class'] == 1), 'Cheat'] = u'❌'

		elif class1_average_page_leaves > class0_average_page_leaves:
			results.loc[(results['Class'] == 0), 'Cheat'] = u'❌'
			results.loc[(results['Class'] == 1), 'Cheat'] = u'✓'

		elif class0_average_page_leaves == class1_average_page_leaves:
			results.loc[(results['Class'] == 0), 'Cheat'] = u'❌'
			results.loc[(results['Class'] == 1), 'Cheat'] = u'❌'

		# Builds index for the participants
		iterable_index = list(self.data_set.index.values)
		for index in results.index[results['page_leaves'] == 'CA'].tolist():
			iterable_index.append(index)

		list_of_labels = []
		# Builds labels for the participants, if they don't appear in the results index, they are labeled as
		# non-anomalous students, therefore, they are classified as non-cheaters.
		for items in iterable_index:
			if items not in results.index.values or str(results.loc[items, 'Cheat']) == 'nan':
				list_of_labels.append(tk.Label(self, text='{}\n{}'.format(items, u'❌')))
			else:
				if str(results.loc[items, 'Opposite Distance']) == 'nan':
					list_of_labels.append(tk.Label(self, text="{}\n{}".format(
						items, results.loc[items, 'Cheat'])))

				else:
					list_of_labels.append(tk.Label(self, text="{}\n{}\n{}" .format(
						items, results.loc[items, 'Cheat'],
						"OD: {}\nADL {}".format(
							round(results.loc[items, 'Opposite Distance'], 2),
							round(results.loc[items, 'Assigned Distance'], 2)
						)
					)))

		# Grids labels
		i = -1
		row_index = 0
		for labels in list_of_labels:
			i += 1

			if i % 5 == 0:
				row_index += 1
				i = 0

			labels.config(font=("TkDefaultFont", 9))
			labels.grid(row=row_index + 2, column=i, sticky='n', padx=10, pady=5)

		# Reset the temp_back_button
		if temp_back_button is not None:
			temp_back_button.pack_forget()
			temp_back_button.destroy()

		# Sets a back button to return and select another quiz
		temp_back_button = ttk.Button(self, text="Select Another Quiz",
		                             command=lambda: self.controller.change_frame('MainMenu'))
		temp_back_button.grid(row=0, column=4)

	def start_basic_anomaly(self):
		self.built_data_set = False
		jack_walsh = predictors.OneClassSVMSeperator(self.data_set)
		jack_walsh.run()

	def start_no_exception(self):
		# Sets a default value for the temp_back_button
		temp_back_button = None

		self.built_data_set = False

		self.labelvar.set("{} Indicates a cheat, {} Indicates a not cheater".format(u'✓', u'❌'))

		# Resets the start button if it already exists (Returning from DevSettings Menu or by Selecting Another Quiz)
		self.start_button.grid_forget()
		self.start_button.destroy()

		label_list = []
		jack_walsh = self.data_set.loc[self.data_set['page_leaves'] >= 1]
		self.data_set.drop(jack_walsh.index.values, inplace=True)

		for items in self.data_set.index.values:
			label_list.append(ttk.Label(self, text="{}\n{}".format(items, u'❌')))

		for items in jack_walsh.index.values:
			label_list.append(ttk.Label(self, text="{}\n{}\nPage Leaves: {}".format(items, u'✓',
			                                                                        jack_walsh.loc[items, 'page_leaves'])))

		# Grids labels
		i = -1
		row_index = 0
		for labels in label_list:
			i += 1

			if i % 5 == 0:
				row_index += 1
				i = 0

			labels.config(font=("TkDefaultFont", 9))
			labels.grid(row=row_index, column=i, sticky='w', padx=10, pady=5)

		# Reset the temp_back_button
		if temp_back_button is not None:
			temp_back_button.pack_forget()
			temp_back_button.destroy()

		temp_back_button = ttk.Button(self, text="Select Another Quiz",
		                             command=lambda: self.controller.change_frame('MainMenu'))
		temp_back_button.grid(row=0, column=4)
