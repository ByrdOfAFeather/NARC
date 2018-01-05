from DataProcessing import collectors, constructors
from ModelTraining import predictors
import numpy as np
import tkinter as tk
import requests
import json

temp_dir = r"..\.\temp/data"


class MainBackEnd(tk.Tk):
	"""Serves as the root for the remaining Tkinter GUI menus
	"""
	def __init__(self, *args, **kwargs):
		"""Initializes the root of the GUI
		This function does a few things

		1) Calls the tkinter.Tk __init__ function
		2) Stacks tk.Frame child class objects into a dictionary, this is later used to change the current frame
		3) setups token and url information if it is detected as saved

		Much of this GUI back-end code is inspired by the popular online Stack Overflow answer & related tutorial:
		https://stackoverflow.com/a/7557028
		https://pythonprogramming.net/change-show-new-frame-tkinter/
		"""

		# Checks the value of tokens and deletes it as tk.Tk will fail with unexpected argument if it is not removed.
		is_token = kwargs['is_token']
		eula_accepted = kwargs['eula_accepted']
		del kwargs['is_token']
		del kwargs['eula_accepted']

		tk.Tk.__init__(self, *args, **kwargs)

		# AESTHETIC
		self.geometry("300x300")
		self.title("NARC")

		# Sets API defaults to be reassigned to either the stored token or a new one given by the user
		self.url = None
		self.token = None
		self.headers = None
		self.is_trusted_ssl = True

		# Sets up the container frame which will serve as a important piece of related classes
		container = tk.Frame(self, bd=2, relief=tk.SUNKEN)
		container.grid(row=0, column=0, sticky='nsew')

		# Formats the container frame
		container.grid_rowconfigure(0, weight=1)
		container.grid_columnconfigure(0, weight=1)

		# Builds a dictionary linking {frame_name: frame_object_reference}
		self.frames = {}
		for frames in (EULAMenu, TokenSelector, MainMenu, TensorflowMenu):
			cur_frame = frames(container, self)
			self.frames[frames.__name__] = cur_frame
			cur_frame.grid(row=0, column=0, sticky='nsew')
			cur_frame.grid_rowconfigure(0, weight=1)
			cur_frame.grid_columnconfigure(0, weight=1)

		# Sets the stored token if it is found to exist
		if is_token and not eula_accepted:
			self._setup_token()
			start_frame = 'EULAMenu'

		elif is_token and eula_accepted:
			self._setup_token()
			start_frame = 'MainMenu'

		# Starts the frame as a token & url input menu
		elif not is_token and not eula_accepted: start_frame = 'EULAMenu'

		elif not is_token and eula_accepted: start_frame = 'TokenSelector'

		else: start_frame = 'MainMenu'

		self.change_frame(start_frame)

	# Function to change frames when required by the program
	def change_frame(self, frame):
		for frame_values in self.frames.values():
			frame_values.grid_remove()
		self.frames[frame].winfo_toplevel().geometry("")
		self.frames[frame].tkraise()
		self.frames[frame].grid()
		self.frames[frame].init_gui()

	def _setup_token(self):
		token = json.load(open("{}/token.json".format(temp_dir)))
		self.token = token['token']
		self.url = token['url']
		self.headers = {'Authorization': 'Bearer {}'.format(self.token)}
		self.is_trusted_ssl = token['trusted_ssl']


class TokenSelector(tk.Frame):
	"""Allows the user to setup Canvas API information and store it in a .json format in the temp/data folder
	"""
	def __init__(self, parent, controller):
		"""Simple __init__ function to call the parent init and setup default values

		The values have to exist during the first call to these classes in the backend class values are unable to be
		filled due to the uncertain condition of self.controller.token or self.controller.url

		:param parent: The parent containing the child frame, this is set to the MainBackEnd's self.container
					   :type: tk.Frame()
		:param controller: The tkinter root that is able to add and refresh the GUI
					   :type: tk.Tk()
		"""
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.controller = controller

		# Both of these are reclassified later as tk.Entry() objects to allow for users to input Canvas API information
		self.token_input = None
		self.url_input = None

		self.ssl_trusted_variable = None
		self.ssl_trusted_drop_down = None
		self.ssl_options = None

		# These are both placeholders to take on the value of input values from token and url input objects
		self.token = None
		self.url = None

		# Setups confirmation information that will be used to verify API information
		self.confirmed_button = None
		self.is_collected = False

		self.error = None
		self.default = [True, True]

	def delete_default(self, event):
		"""Changes the default text to nothing or resets it if nothing has been put in
		:param event: Tkinter GUI event
		:return: None
		"""
		if event.widget == self.url_input:
			if self.default[0]:
				event.widget.delete(0, "end")
				self.default[0] = False

			if not self.default[0] and not self.token_input.get():
				self.token_input.insert(0, "Put your API key here!")
				self.default[1] = True

		elif event.widget == self.token_input:
			if self.default[1]:
				event.widget.delete(0, "end")
				self.default[1] = False

			if not self.default[1] and not self.url_input.get():
				self.url_input.insert(0, "Insert your url here! Ex. nccs, ncvps, stanford, etc")
				self.default[0] = True
		return None

	def init_gui(self):
		"""Re-assigns default values to GUI values
		"""
		url_default = "Insert your url here! Ex. nccs, ncvps, stanford, etc"
		self.token_input = tk.Entry(self, width=50)
		self.url_input = tk.Entry(self, width=50)

		self.token_input.delete(0, tk.END), self.url_input.delete(0, tk.END)
		self.token_input.insert(0, "Put your API key here!"), self.url_input.insert(0, url_default)
		self.token_input.bind("<Button-1>", self.delete_default), self.url_input.bind("<Button-1>", self.delete_default)

		self.token_input.grid(row=0, column=0, sticky='nsew'), self.url_input.grid(row=1, column=0, sticky='nsew')

		self.ssl_trusted_variable = tk.StringVar(self)
		self.ssl_options = {'Regular SSL': True, 'Zscaler or Similar Network Security': False}
		self.ssl_trusted_variable.set('Regular SSL')
		self.ssl_trusted_drop_down = tk.OptionMenu(self, self.ssl_trusted_variable, *self.ssl_options, command=self.set_ssl)
		self.ssl_trusted_drop_down.grid()

		self.confirmed_button = tk.Button(self, command=self._confirm_token, width=20,
		                                  bg="#efc729", bd=.5, activeforeground="black")
		self.confirmed_button.grid()

		self.error = tk.Label(self, text="Sorry, either your URL or API key is incorrect!")

	def set_ssl(self, _):
		self.controller.is_trusted_ssl = self.ssl_options[self.ssl_trusted_variable.get()]

	def _confirm_token(self):
		"""Confirms the token and url match together and a single query to the Canvas API can be made successfully
		"""

		# Gets the current tokens from the tk.Entry menus - see self.init_gui()
		cur_token = self.token_input.get()
		cur_url = self.url_input.get()

		# Sets up the target url for the api and token information
		api_target = "http://{}.instructure.com/api/v1/users/activity_stream".format(cur_url)
		headers = {'Authorization': 'Bearer {}'.format(cur_token)}
		try:
			test = requests.put(api_target, headers=headers, verify=self.controller.is_trusted_ssl)
			if test.status_code == 200:
				# If the response is positive the information is saved for storage in a token.json file
				with open('{}/token.json'.format(temp_dir), 'w') as f:
					json.dump({'token': cur_token, 'url': "http://" + cur_url + ".instructure.com",
					           'trusted_ssl': self.controller.is_trusted_ssl}, f)

				# Sets up the information so that the program can continue to run without having to reload the data
				self.is_collected = True
				self.controller.url = "http://" + cur_url + ".instructure.com"
				self.controller.token = cur_token
				self.controller.headers = {"Authorization": "Bearer {}".format(cur_token)}
				self.controller.change_frame('MainMenu')

			else:
				print(test.json())
				self.error.grid()

		except requests.exceptions.ConnectionError as e:
			print("Something has gone wrong with setting up the url! Here's all the information I know: ")
			print("{}".format(api_target), "{}".format(headers), "{}".format(cur_url), "{}".format(cur_token))
			print(e)
			self.error.grid()


class MainMenu(tk.Frame):
	"""Main Menu storing the ability to choose from classes, modules, and quizzes to locate test data to train on
	"""
	def __init__(self, parent, controller):
		""""Simple __init__ function to call the parent init and setup default values

		The values have to exist during the first call to these classes in the backend class values are unable to be
		filled due to the uncertain condition of self.controller.token or self.controller.url

		:param parent: The parent containing the child frame, this is set to the MainBackEnd's self.container
					   :type: tk.Frame()
		:param controller: The tkinter root that is able to add and refresh the GUI
					   :type: tk.Tk()
		"""
		tk.Frame.__init__(self, parent)

		self.parent = parent
		self.controller = controller

		# Placeholder variables for Collector objects to be created when a section is chosen
		self.user_collector = None
		self.course_collector = None
		self.module_collector = None
		self.quiz_collector = None

		# Placeholder variables for drop-down menus for quizzes, modules, and courses
		self.course_drop_down = None
		self.module_drop_down = None
		self.quiz_drop_down = None

		# Placeholder values for buttons used to confirm selection from drop down menus
		self.select_course = None
		self.select_module = None
		self.select_quiz = None

		# Placeholder values for lists of courses, modules, and quizzes [linked to their respective parents]
		self.courses = None
		self.modules = None
		self.quizzes = None

		# Placeholder values for the current ids of selected objects
		self.cur_course_id = None
		self.cur_module_id = None
		self.cur_quiz_id = None

		# Placeholder values for the StringVar containing selection information
		self.course_variable = None
		self.module_variable = None
		self.quiz_variable = None

	def init_gui(self):
		"""Function to setup the menu with just a list of courses linked to the current API User's account
		"""

		# Resets the menu if coming back from TensorflowMenu
		for widget in self.winfo_children():
			widget.pack_forget()
			widget.destroy()

		# Gets a basic UserCollector Object to get course information
		self.user_collector = collectors.UserCollector(self.controller.url,
		                                               self.controller.headers, self.controller.is_trusted_ssl)

		# Declares variables used for the course selection
		self.course_variable = tk.StringVar(self)
		self.courses = self.user_collector.get_associated_courses()

		course_names = list(self.courses.keys())
		self.course_variable.set(course_names[0])

		self.course_drop_down = tk.OptionMenu(self, self.course_variable, *course_names)
		self.course_drop_down.grid()

		# This command links to a function that will update modules and quizzes (with a default value) for convince
		self.select_course = tk.Button(self, text='Select Course!', command=self.update_both)

		self.select_course.grid()

	def update_both(self):
		"""Simple multi-function since lambda only supports a single argument and self.select_course requires two
		"""
		self.update_module()
		self.update_quiz()

	def update_module(self):
		"""Updates module drop-down options 
		"""
		if self.module_drop_down is not None:
			self.module_drop_down.pack_forget()
			self.module_drop_down.destroy()
			self.select_module.pack_forget()
			self.select_module.destroy()

		current_course_key = self.course_variable.get()
		self.cur_course_id = self.courses[current_course_key]

		self.course_collector = collectors.Collector(url=self.controller.url,
		                                             header=self.controller.headers,
													 class_id=self.cur_course_id,
													 verify=self.controller.is_trusted_ssl)
		self.modules = self.course_collector.get_course_modules()

		module_names = list(self.modules.keys())
		self.module_variable = tk.StringVar(self)
		self.module_variable.set(module_names[0])

		self.module_drop_down = tk.OptionMenu(self, self.module_variable, *module_names)
		self.module_drop_down.grid()

		self.select_module = tk.Button(self, text='Select Module!', command=self.update_quiz())
		self.select_module.grid()

	def update_quiz(self):
		if self.quiz_drop_down is not None:
			self.quiz_drop_down.pack_forget()
			self.quiz_drop_down.destroy()
			self.select_quiz.pack_forget()
			self.select_quiz.destroy()

		current_module_key = self.module_variable.get()
		self.cur_module_id = self.modules[current_module_key]
		self.module_collector = collectors.Module(module_id=self.cur_module_id,
		                                          class_id=self.cur_course_id,
		                                          url=self.controller.url, header=self.controller.headers,
		                                          verify=self.controller.is_trusted_ssl)
		self.quizzes = self.module_collector.get_module_items()['Subsections']['Quizzes']

		quiz_names = list(self.quizzes.keys())
		if len(quiz_names) == 0:
			default = "No Quizzes Found!"
			quiz_names = ['test', 'test']
		else: default = quiz_names[0]
		self.quiz_variable = tk.StringVar(self)
		self.quiz_variable.set(default)

		self.quiz_drop_down = tk.OptionMenu(self, self.quiz_variable, *quiz_names)
		self.quiz_drop_down.grid()

		self.select_quiz = tk.Button(self, text='Select Quiz!', command=self.start_tensorflow_gui)
		self.select_quiz.grid()

	def start_tensorflow_gui(self):
		current_quiz_key = self.quiz_variable.get()
		self.cur_quiz_id = self.quizzes[current_quiz_key]
		self.quiz_collector = collectors.Quiz(quiz_id=self.cur_quiz_id, class_id=self.cur_course_id,
		                                      url=self.controller.url, header=self.controller.headers,
		                                      verify=self.controller.is_trusted_ssl)
		self.controller.cur_quiz = self.quiz_collector
		self.controller.change_frame('TensorflowMenu')


class TensorflowMenu(tk.Frame):

	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.quiz = None
		self.quiz_constructor = None
		self.data_set = None
		self.pre_flags = None

	def build_data_set(self):
		self.quiz = self.controller.cur_quiz
		self.quiz_constructor = constructors.QuizEvents(self.quiz, anon=False)
		data_sets = self.quiz_constructor.build_dataframe(pre_flagged=True)
		self.pre_flags = data_sets[0]
		self.data_set = data_sets[1]

	def init_gui(self):

		for widget in self.winfo_children():
			widget.pack_forget()
			widget.destroy()

		temp_back_button = None

		labelvar = tk.StringVar()
		labelvar.set("Building Data Set!")
		label = tk.Label(self, textvar=labelvar)
		label.grid()
		self.controller.update()

		self.build_data_set()

		labelvar.set("Starting AutoEncoder!")
		self.controller.update()

		jack_walsh = predictors.AutoEncoder(self.data_set, self.data_set)
		jack_walsh.PCA()

		output = jack_walsh.separate(learning_rate=.08, epochs=500000, test_thresh=0, labelvar=labelvar,
		                             controller=self.controller)
		omega = predictors.KMeansSeparator(output)

		labelvar.set("Starting Clustering Algorithm!")
		self.controller.update()
		results = omega.classify(clusters=2, n_init=50000)

		labelvar.set("Here's what I think possibly might maybe 50/50 could be the list of cheaters/non-cheaters")
		self.controller.update()

		# Gets the index values of specific classes
		class0 = results[results['Class'] == 0]
		class1 = results[results['Class'] == 1]

		# Gets non-scaled versions of page_leaves values
		class0_page_leaves = self.data_set.loc[class0.index.values]['page_leaves']
		class1_page_leaves = self.data_set.loc[class1.index.values]['page_leaves']

		# Adds pre flagged users to the results for display purposes, as well as removes irrelevant overhead from the
		# pre flags
		results = results.append(self.pre_flags)
		results.drop(['average_time_between_questions', 'time_taken'], axis=1, inplace=True)

		class0_average_page_leaves = (sum(class0_page_leaves) / len(class0_page_leaves))
		class1_average_page_leaves = (sum(class1_page_leaves) / len(class1_page_leaves))

		print("CLASS 0 AVERAGE {}".format(class0_average_page_leaves))
		print(class0_page_leaves)

		print("CLASS 1 AVERAGE {}".format(class1_average_page_leaves))
		print(class1_page_leaves)

		results.loc[(results['page_leaves'] == 'CA'), 'Cheat'] = u'✓'
		results.loc[(results['page_leaves'] == 'CA'), 'Class'] = 2

		if class0_average_page_leaves > class1_average_page_leaves:
			results.loc[(results['Class'] == 0), 'Cheat'] = u'✓'
			results.loc[(results['Class'] == 1), 'Cheat'] = u'❌'

		elif class1_average_page_leaves > class0_average_page_leaves:
			results.loc[(results['Class'] == 0), 'Cheat'] = u'❌'
			results.loc[(results['Class'] == 1), 'Cheat'] = u'✓'

		list_of_labels = []

		iterable_index = list(self.data_set.index.values)
		for index in results.index[results['page_leaves'] == 'CA'].tolist():
			iterable_index.append(index)

		for items in iterable_index:
			if items not in results.index.values:
				list_of_labels.append(tk.Label(self, text=items + '\n' + u'❌'))
			else:
				list_of_labels.append(tk.Label(self, text=items + '\n' + results.loc[items, 'Cheat']))

		for items in list_of_labels:
			items.grid()

		if temp_back_button is not None:
			temp_back_button.pack_forget()
			temp_back_button.destroy()

		temp_back_button = tk.Button(self, text="Select Another Quiz",
		                             command=lambda: self.controller.change_frame('MainMenu'))
		temp_back_button.grid()


class SettingsMenu(tk.Frame):
	"""To be implemented
	"""
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)


class EULAMenu(tk.Frame):
	"""Simple class to gain acceptance of EULA
	Derived heavily from StackOverflow answer: https://stackoverflow.com/a/19647325

	"""
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.controller = controller

		self.scroll_menu = None
		self.eula = None

		self.accept_button = None
		self.decline_button = None

	def init_gui(self):
		eula = \
			"""
MIT License

Copyright (c) 2017-2018 Matthew Byrd

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

			"""

		self.scroll_menu = tk.Scrollbar(self)
		self.scroll_menu.grid(row=0, column=1, sticky='NS')

		self.eula = tk.Text(self, wrap=tk.NONE, yscrollcommand=self.scroll_menu.set)
		self.eula.insert("1.0", eula)
		self.eula.grid(row=0, column=0, sticky='nsew')
		self.eula.configure(state=tk.DISABLED)

		self.accept_button = tk.Button(self, text='Accept!', command=self.update_eula_file)
		self.accept_button.grid()

		self.decline_button = tk.Button(self, text='Decline!', command=lambda: self.controller.destroy())
		self.decline_button.grid()

		self.scroll_menu.config(command=self.eula.yview)

	def update_eula_file(self):
		from datetime import datetime
		with open(r'..\.\temp/eula.txt', 'w') as output:
			output.write("User Agreed to EULA {}".format(datetime.now()))

		if not self.controller.token:
			self.controller.change_frame('TokenSelector')

		elif self.controller.token:
			self.controller.change_frame('MainMenu')
