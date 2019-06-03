import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
from DataProcessing import collectors
import ml_displayers as tfd
import requests
import json
import os
import sys

temp_dir = r"..\.\temp/data"


def resource_path(resource):
	"""Helper function to find resources after PyInstaller compilation
	Taken from post: https://www.reddit.com/r/learnpython/comments/4kjie3/how_to_include_gui_images_with_pyinstaller/
	"""
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys.prefix, resource)
	else:
		return os.path.join(os.path.abspath('.'), resource)


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
		# self.iconbitmap(resource_path(r'temp_logo.ico'))

		# Sets API defaults to be reassigned to either the stored token or a new one given by the user
		self.url = None
		self.token = None
		self.headers = None

		# Sets up the default type of separation {AutoEncoder = Autoencoder and KMeans, Anomaly = OneClassSVM,
		# No Exception = Always if page leaves > 1}
		self.separation_options = ['Auto Encoder', 'Basic Anomaly', 'No Exceptions']
		self.separation_type = self.separation_options[0]

		# Sets up the container frame which will serve as a important piece of related classes
		container = tk.Frame(self)

		# Formats the container frame
		container.pack(side='top', fill='both', expand=True)

		# Builds a dictionary linking {frame_name: frame_object_reference}
		self.frames = {}
		for frames in (EULAMenu, TokenSelector, MainMenu, tfd.DevSettingsMenu, tfd.AutoEncoderSettingsMenu,
		               SettingsMenu):
			cur_frame = frames(container, self)
			self.frames[frames.__name__] = cur_frame
			cur_frame.grid(sticky='nsew')

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
		self.frames[frame].grid(sticky='nsew')
		self.frames[frame].init_gui()

	def autoencoder_frame(self, data_options=[], **kwargs):
		for frame_values in self.frames.values():
			frame_values.grid_remove()
		self.frames['AutoEncoderSettingsMenu'].winfo_toplevel().geometry("")
		self.frames['AutoEncoderSettingsMenu'].tkraise()
		self.frames['AutoEncoderSettingsMenu'].grid(sticky='nsew')
		self.frames['AutoEncoderSettingsMenu'].init_gui(data_options, **kwargs)

	def _setup_token(self):
		token = json.load(open("{}/token.json".format(temp_dir)))
		self.token = token['token']
		self.url = token['url']
		self.headers = {'Authorization': 'Bearer {}'.format(self.token)}


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

		# Placeholder variables for Settings Menu
		self.settings_button = None

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

		self.module_error_label = None
		self.quiz_error_label = None

		self.test_var = None
		self.other_test_var = None

	def init_gui(self):
		"""Function to setup the menu with just a list of courses linked to the current API User's account
		"""

		# Resets the menu, mainly for when coming back from the TensorFlow Menu

		for widget in self.winfo_children():
			widget.pack_forget()
			widget.destroy()

		# This is required, as without it functions that remove the drop down upon error would throw an exception
		# since the widgets are forgotten but not set to None values (i.e if not None would evaluate True, but the
		# drop_down would be long forgotten already, throwing a Tkinter exception)
		self.course_drop_down = None
		self.module_drop_down = None
		self.quiz_drop_down = None

		# Gets a basic UserCollector Object to get course information
		self.user_collector = collectors.UserCollector(self.controller.url,
		                                               self.controller.headers)

		temp_label = ttk.Label(self, text='Getting Courses...')
		temp_label.grid()

		self.controller.update()

		# Declares variables used for the course selection
		self.course_variable = tk.StringVar(self)
		self.courses = self.user_collector.get_associated_courses()
		course_names = list(self.courses.keys())

		temp_label.grid_forget()
		temp_label.destroy()

		# self.test_var = Image.open(r'C:\Users\soult\OneDrive\Pictures\DCshHh3UQAEFkpf.png')
		# self.other_test_var = ImageTk.PhotoImage(self.test_var)
		self.settings_button = tk.Button(self, text='Settings',
			command=lambda: self.controller.change_frame('SettingsMenu'), borderwidth=0)
		self.settings_button.grid(row=0, column=1, sticky='n')

		self.course_drop_down = ttk.OptionMenu(self, self.course_variable, "Select A Course!", *course_names)
		self.course_drop_down.grid(row=0, column=0, sticky='nsew')

		self.course_variable.trace('w', self.update_both)

	@staticmethod
	def _delete_item(drop_down):
		drop_down.grid_forget()
		drop_down.destroy()

	def update_both(self, *_):
		"""Simple multi-function since lambda only supports a single argument and self.select_course requires two
		"""
		# If the error was previously thrown, remove it [it if will be thrown again, it will be recreated later]
		if self.module_error_label is not None:
			self._delete_item(self.module_error_label)
			self.module_error_label = None

		try:
			self.update_module()
			self.update_quiz()

		# Accepts Key Error (the Module or Quiz don't line up in the queried dictionary) or
		# it will accept a index error (The Module or Quiz have no items respectively)
		except (KeyError, IndexError):
			# Removes Quiz drop down if it already existed (moving from a class not missing anything to a class without
			# modules
			if self.quiz_drop_down is not None:
				self._delete_item(self.quiz_drop_down)
				self.quiz_drop_down = None

			self.module_error_label = ttk.Label(self, text='It appears either you don\'t have access to, '
			                                               'or don\'t have any modules in this course!')
			self.module_error_label.grid(sticky='nsew')

	def update_module(self):
		"""Updates module drop-down options 
		"""
		# If there is already a drop-down, delete it.
		if self.module_drop_down is not None:
			self._delete_item(self.module_drop_down)
			self.module_drop_down = None

		# Gets the course ID based on the already made dictionary from a user_collector object
		current_course_key = self.course_variable.get()
		self.cur_course_id = self.courses[current_course_key]

		# Gets the Module ID based on the already made dictionary from a collector class
		self.course_collector = collectors.Collector(url=self.controller.url,
		                                             header=self.controller.headers,
													 class_id=self.cur_course_id)

		temp_label = ttk.Label(self, text='Getting Modules...')
		temp_label.grid()
		self.controller.update()

		# Gets all the modules associated with a course
		self.modules = self.course_collector.get_course_modules()

		temp_label.grid_forget()
		temp_label.destroy()
		self.controller.update()

		# Sets up the StringVar to re-query every time the option is changed.
		module_names = list(self.modules.keys())
		self.module_variable = tk.StringVar(self)
		self.module_variable.trace('w', self.update_quiz)

		# Sets up the module drop down based on the StringVar and declares it's fixed GUI position
		self.module_drop_down = ttk.OptionMenu(self, self.module_variable, module_names[0], *module_names)
		self.module_drop_down.grid(row=2, column=0, sticky='nsew')
		self.settings_button.grid(column=1, row=0)

	def update_quiz(self, *_):
		"""Updates the quiz menu
		:param _: args list containing Tkinter Event Information
		"""
		# If the quiz_drop_down already exists, delete it
		if self.quiz_drop_down is not None:
			self._delete_item(self.quiz_drop_down)
			self.quiz_drop_down = None

		# If a quiz_error_label was already thrown, delete it
		if self.quiz_error_label is not None:
			self._delete_item(self.quiz_error_label)
			self.quiz_error_label = None

		# Sets up the current module based on a previously created dictionary from a Collector object
		current_module_key = self.module_variable.get()
		self.cur_module_id = self.modules[current_module_key]

		# Creates a module collector and sets up a quiz dictionary
		self.module_collector = collectors.Module(module_id=self.cur_module_id,
		                                          class_id=self.cur_course_id,
		                                          url=self.controller.url, header=self.controller.headers)

		temp_label = ttk.Label(self, text='Getting Quizzes...')
		temp_label.grid()
		self.controller.update()

		# Sets up a list of quizzes and their respective names
		self.quizzes = self.module_collector.get_module_items()['Subsections']['Quizzes']
		quiz_names = list(self.quizzes.keys())

		temp_label.grid_forget()
		temp_label.destroy()
		self.controller.update()

		# Creates a button that links to starting the auto_encoder GUI with confirmed settings
		self.select_quiz = ttk.Button(self, text='Select Quiz!', command=self.start_autoencoder_gui)
		self.select_quiz.grid(row=2, column=1, sticky='nsew')

		# Labels a default value if no quizzes are found
		if len(quiz_names) == 0:
			self.quiz_error_label = ttk.Label(self, text='No Quizzes Found In This Module!')
			self.quiz_error_label.grid(sticky='nsew')

		# Sets up the quiz if there are quizzes found
		else:
			default = quiz_names[0]

			self.quiz_variable = tk.StringVar(self)

			self.quiz_drop_down = ttk.OptionMenu(self, self.quiz_variable, default, *quiz_names)
			self.quiz_drop_down.grid(row=3, column=0, sticky='nsew')

		self.settings_button.grid(column=1, row=0)

	def start_autoencoder_gui(self):
		"""Starts the GUI for the autoencoder
		"""
		current_quiz_key = self.quiz_variable.get()
		self.cur_quiz_id = self.quizzes[current_quiz_key]
		self.quiz_collector = collectors.Quiz(quiz_id=self.cur_quiz_id, class_id=self.cur_course_id,
		                                      url=self.controller.url, header=self.controller.headers)
		self.controller.cur_quiz = self.quiz_collector
		self.controller.autoencoder_frame()


class GeneralSettings(tk.Frame):
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

		# These are both placeholders to take on the value of input values from token and url input objects
		self.token = None
		self.url = None

		# Setups confirmation information that will be used to verify API information
		self.confirmed_button = None

		self.error = None
		self.default = [True, True]

		# Sets up default value  values that will fill in the blank when nothing is typed
		self.default_values = None

	def _confirm_token(self):
		"""Confirms the token and url match together and a single query to the Canvas API can be made successfully
		"""

		# Gets the current tokens from the ttk.Entry menus - see self.init_gui()
		cur_token = self.token_input.get()
		cur_url = self.url_input.get()

		# Sets up the target url for the api and token information
		api_target = "http://{}.instructure.com/api/v1/courses?enrollment_state=active&per_page=50".format(cur_url)
		headers = {'Authorization': 'Bearer {}'.format(cur_token)}
		try:
			test = requests.get(api_target, headers=headers, verify=True)
			print(test.status_code)
			if test.status_code == 200:
				# If the response is positive the information is saved for storage in a token.json file
				with open('{}/token.json'.format(temp_dir), 'w') as f:
					json.dump({'token': cur_token, 'url': "http://" + cur_url + ".instructure.com"}, f)

				# Sets up the information so that the program can continue to run without having to reload the data
				self.controller.url = "http://" + cur_url + ".instructure.com"
				self.controller.token = cur_token
				self.controller.headers = {"Authorization": "Bearer {}".format(cur_token)}

			else:
				self.error.grid(sticky='nsew')

		# Assumes any error given as a connection error is probably a error with API or URL
		except requests.exceptions.ConnectionError as e:
			print("Something has gone wrong with setting up the url! Here's all the information I know: ")
			print("{}".format(api_target), "{}".format(headers), "{}".format(cur_url), "{}".format(cur_token))
			print(e)
			self.error.grid(sticky='nsew')

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
				self.token_input.insert(0, self.default_values[0])
				self.default[1] = True

		elif event.widget == self.token_input:
			if self.default[1]:
				event.widget.delete(0, "end")
				self.default[1] = False

			if not self.default[1] and not self.url_input.get():
				self.url_input.insert(0, self.default_values[1])
				self.default[0] = True
		return None


class TokenSelector(GeneralSettings):
	"""Allows the user to setup Canvas API information and store it in a .json format in the temp/data folder
	"""
	def __init__(self, parent, controller):
		GeneralSettings.__init__(self, parent, controller)

	def init_gui(self):
		"""Re-assigns default values to GUI values
		"""
		self.default_values = [
			'Put your API key here',
			'Insert your url here! Ex. nccs, ncvps, stanford, etc'
		]

		url_default = "Insert your url here! Ex. nccs, ncvps, stanford, etc"
		self.token_input = ttk.Entry(self, width=50)
		self.url_input = ttk.Entry(self, width=50)

		self.token_input.delete(0, tk.END), self.url_input.delete(0, tk.END)
		self.token_input.insert(0, "Put your API key here!"), self.url_input.insert(0, url_default)
		self.token_input.bind("<Button-1>", self.delete_default), self.url_input.bind("<Button-1>", self.delete_default)

		self.token_input.grid(row=0, column=0, sticky='nsew'), self.url_input.grid(row=1, column=0, sticky='nsew')

		self.confirmed_button = ttk.Button(self, command=self.confirm_settings, width=20, text='Confirm Information!')
		self.confirmed_button.grid(sticky='nsew')

		self.error = ttk.Label(self, text="Sorry, either your URL or API key is incorrect!")

	def confirm_settings(self):
		self._confirm_token()
		self.controller.change_frame('MainMenu')


class SettingsMenu(GeneralSettings):
	"""
	TODO: Retool as a child of TokenSelector/Make General Settings Menu
	TODO: [Settings Icon] https://www.reddit.com/r/learnpython/comments/4kjie3/how_to_include_gui_images_with_pyinstaller/
	"""
	def __init__(self, parent, controller):
		GeneralSettings.__init__(self, parent, controller)
		self.type_of_separation = None
		self.type_of_separation_var = None

		self.separation_label = None
		self.url_label = None
		self.token_label = None

	def init_gui(self):
		"""Initializes GUI values
		"""
		for widget in self.winfo_children():
			widget.pack_forget()
			widget.destroy()

		self.default_values = [
			self.controller.token,
			self.controller.url.split('/')[2].split('.')[0]
		]

		self.token_label = ttk.Label(self, text="API KEY:")
		self.token_label.grid(sticky='n')

		# Sets up Token Input
		self.token_input = ttk.Entry(self, width=60)
		self.token_input.grid()

		self.url_label = ttk.Label(self, text="URL:")
		self.url_label.grid(sticky='n')

		# Sets up URL Input Button
		self.url_input = ttk.Entry(self, width=60)
		self.url_input.grid()

		self.token_input.delete(0, tk.END), self.url_input.delete(0, tk.END)
		self.token_input.insert(0, self.default_values[0]), self.url_input.insert(0, self.default_values[1])
		self.token_input.bind("<Button-1>", self.delete_default), self.url_input.bind("<Button-1>", self.delete_default)

		self.separation_label = ttk.Label(self, text='Choose The Type Of Separation You want To Use:')
		self.separation_label.grid(row=0, column=2)

		# Sets up the type of separation drop down
		separation_type_style = ttk.Style()
		separation_type_style.configure("OP.TMenubutton", background='#dedede')
		self.type_of_separation_var = tk.StringVar()
		self.type_of_separation_var.set(self.controller.separation_type)
		self.type_of_separation = ttk.OptionMenu(self, self.type_of_separation_var,
			self.controller.separation_type, *self.controller.separation_options, style='OP.TMenubutton')
		self.type_of_separation.grid(sticky='ew', row=1, column=2)

		# Sets up confirm button
		self.confirmed_button = ttk.Button(self, text='Confirm Settings!', command=self.confirm_settings)
		self.confirmed_button.grid(column=1, sticky='n')

	def confirm_settings(self):
		self._confirm_token()
		self.controller.separation_type = self.type_of_separation_var.get()
		self.controller.change_frame('MainMenu')


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

		self.eula = tk.Text(self, wrap=tk.NONE)
		self.eula.insert("1.0", eula)
		self.eula.grid(row=0, column=0, sticky='nsew')
		self.eula.configure(state=tk.DISABLED)

		self.accept_button = ttk.Button(self, text='Accept!', command=self.update_eula_file)
		self.accept_button.grid(sticky='nsew')

		self.decline_button = ttk.Button(self, text='Decline!', command=lambda: self.controller.destroy())
		self.decline_button.grid(sticky='nsew')

	def update_eula_file(self):
		from datetime import datetime
		with open(r'..\.\temp/eula.txt', 'w') as output:
			output.write("User Agreed to EULA {}".format(datetime.now()))

		if not self.controller.token:
			self.controller.change_frame('TokenSelector')

		elif self.controller.token:
			self.controller.change_frame('MainMenu')
