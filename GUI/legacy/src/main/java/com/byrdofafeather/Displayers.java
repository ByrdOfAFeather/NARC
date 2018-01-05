package com.byrdofafeather;

import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.JsonNode;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;
import org.ini4j.Wini;
import org.json.JSONException;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;
import java.io.File;
import java.io.IOException;
import java.nio.file.FileAlreadyExistsException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Map;

public class Displayers { }

/**
 * Used as a startup GUI to create and store user settings
 */
class UserText extends JTextField implements FocusListener {

	private String hint;
	private boolean showingHint;

	UserText(String userInputMessage, int sizeWidth, int sizeHeight) {
		super(userInputMessage);
		hint = userInputMessage;
		showingHint = true;
		super.addFocusListener(this);
		setPreferredSize(new Dimension(sizeWidth, sizeHeight));
		setLayout(new GridBagLayout());
	}


	public void focusGained(FocusEvent e) {
		if (this.getText().length() == 0) {
			super.setText("");
			showingHint = false;
		}

	}

	public void focusLost(FocusEvent e) {
		if (this.getText().length() == 0) {
			super.setText(hint);
			showingHint = true;
		}
	}

	public String getText(){
		return showingHint ? "" : super.getText();
	}

}

/**
 * Used as a generalized GUI for the programs main menu\
 */
class MainMenu extends JFrame implements ActionListener {
	// User Components Initialization

	UserCollectors user; // User given the settings.ini file
	Map<String, String> userCourses; // Dict linking user to their courses


	// Information strings containing locations and authorization information
	String courseID = ""; // ID for the target class
	String moduleID = ""; // Id for the target Module
	String url; // The domain name for Canvas Target
	String token[] = new String[2]; // Token array for headers in Canvas authorization


	// GUI Components for the course section
	JPanel courses = new JPanel(); // Drop down menu containing names of courses
	JLabel coursesLabel = new JLabel("Select The Course You Want To Look At!"); // Label for courses
	JButton setCourse = new JButton("Select Course!"); // Button to confirm selection
	JComboBox<String> coursesChoices; // Combo Box of courses for items in the drop down

	// GUI Components for the modules section
	JPanel modules = new JPanel();
	JLabel moduleLable = new JLabel("Select The Module You Would Like To Look At!");
	JButton setModule = new JButton("Select Module!");
	JComboBox<String> moduleChoices;
	Map<String, String> courseModules;

	// GUI Components for the quizzes section
	JPanel quizzes = new JPanel();
	JLabel quizLabel = new JLabel("Select The Quiz You Would Like To Look At!");
	JButton setQuiz = new JButton("Select Quiz!");
	JComboBox<String> quizChoices;
	Map<String, String> moduleQuizzes;

	Module currentModule;



	MainMenu(String usrURL, String usrToken[]) {
		modules.setVisible(false);
		setModule.setVisible(false);
		quizzes.setVisible(false);
		setQuiz.setVisible(false);

		// Sets url and token information
		url = usrURL;
		token = usrToken;

		// Gets the user and their courses
		user = new UserCollectors(url, token);
		userCourses = user.getAssociatedCourses();

		// Sets the label to visable and adds it to the drop down
		coursesLabel.setVisible(true);
		courses.add(coursesLabel);

		// Sets up the drop down by adding classes into coursesChoices component
		getCourses();

		// Adds action listener to confirmation buttons
		setCourse.addActionListener(this);
		setModule.addActionListener(this);

		// Adds the course sections to the main Frame
		add(courses);
		add(setCourse);
		add(modules);
		add(setModule);
		add(quizzes);
		add(setQuiz);

		// Sets basic GUI settings
		initGUI();
	}

	/**
	 * Sets basic GUI settings
	 */
	private void initGUI() {
		setLayout(new FlowLayout());
		setVisible(true);
		setSize(900, 900);
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
	}

	private void updateModule() {
		try {
			modules.remove(moduleChoices);
		}

		catch (NullPointerException e) {
			System.out.println("It appears no modules have been initialized yet");
			System.out.println(e.toString());
		}

		ClassCollectors currentCourse = new ClassCollectors(url, token, Integer.parseInt(courseID));
		try {
			courseModules = currentCourse.getCourseModules();
			ArrayList<String> moduleList = new ArrayList<>(courseModules.keySet());
			String moduleArray[] = moduleList.toArray(new String[moduleList.size()]);
			moduleChoices = new JComboBox<>(moduleArray);
		}

		catch (JSONException e) {
			String filler[] = new String[1];
			filler[0] = "No Modules Found";
			moduleChoices = new JComboBox<>(filler);
			System.out.println(e.toString());
		}

		modules.add(moduleLable);
		modules.add(moduleChoices);
		if (!modules.isVisible()) { modules.setVisible(true); }
		if (!setModule.isVisible()) { setModule.setVisible(true); }
		modules.updateUI();
		moduleID = courseModules.get(moduleChoices.getSelectedItem().toString());
	}

	/**
	 * Builds drop down menu for courses
	 */
	private void getCourses() {
		ArrayList<String> keyList = new ArrayList<>(userCourses.keySet());
		String keyArray[] = keyList.toArray(new String[keyList.size()]);

		coursesChoices = new JComboBox<>(keyArray);
		courses.add(coursesChoices);
	}

	private void updateQuizzes() {
		try {
			quizzes.remove(quizChoices);
		}
		catch (NullPointerException e) {
			System.out.println("It appears no quizzes have been initialized yet");
			System.out.println(e.toString());
		}


		// TODO: Find a far more robust method of making sure there's no quiz data

		if (moduleChoices.getItemAt(0).equals("No Modules Found")) {
			String filler[] = new String[1];
			filler[0] = "No Quizzes Found";
			quizChoices = new JComboBox<>(filler);
		}

		else {
			currentModule = new Module(url, token, Integer.parseInt(courseID), Integer.parseInt(moduleID));
			moduleQuizzes = currentModule.getModuleQuizzesDict();
			ArrayList<String> keyArrayList = new ArrayList<>(moduleQuizzes.keySet());
			String keyArray[] = keyArrayList.toArray(new String[keyArrayList.size()]);
			quizChoices = new JComboBox<>(keyArray);
 		}


		quizzes.add(quizLabel);
		quizzes.add(quizChoices);

		if (!quizzes.isVisible()) { quizzes.setVisible(true); }
		if (!setQuiz.isVisible()) { setQuiz.setVisible(true); }
		quizzes.updateUI();

	}

	public void actionPerformed(ActionEvent e) {
		// When a course is 'selected' with the button, redraws the module section and corresponding quiz section
		if (e.getSource() == setCourse) {
			try {
				courseID = userCourses.get(coursesChoices.getSelectedItem().toString());
				updateModule();
				updateQuizzes();
			}
			catch (NullPointerException j) {
				System.out.println("Looks like a Course wasn't selected?");
				System.out.println(j.toString());
			}
		}

		else if (e.getSource() == setModule) {
			try {
				updateQuizzes();
			}

			catch (NullPointerException j) {
				System.out.println("Looks like a Module wasn't selected?");
				System.out.println(j.toString());
			}
		}

	}



}

/**
 * Sets up token settings with first open
 */
class TokenSetup extends JFrame implements ActionListener {


	private UserText tokenGet = new UserText("API Key", 200, 20);
	private UserText urlGet  = new UserText("URL Domain (ex. nccs)", 200, 20);

	private JButton confirm = new JButton("Confirm");
	private JTextArea error = new JTextArea("Verification Failed!");

	private String url;
	private String key;
	private String headers[] = new String[2];

	boolean confirmed = false;

	TokenSetup() {
		confirm.addActionListener(this);
		error.setVisible(false);

		this.add(tokenGet);
		this.add(urlGet);
		this.add(confirm);
		this.add(error);

		this.setLayout(new FlowLayout());

		this.setSize(900, 900);
		this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);

		setVisible(true);

		headers[0] = "Authorization";
		headers[1] = "Bearer " + key;
	}

	public void actionPerformed(ActionEvent e) {

		if (e.getSource() == confirm) {
			key = tokenGet.getText();
			url = "http://" + urlGet.getText() + ".instructure.com";
			headers[1] = "Bearer " + key;

			boolean keyVerification = verifyKey();

			if (keyVerification) {
				dispose();

				try { Files.createDirectory(Paths.get("config")); }
				catch (FileAlreadyExistsException a ) { System.out.println("Config Folder Already Created! Skipping!"); }
				catch (IOException b) { System.out.println(b.toString()); }

				try { Files.createFile(Paths.get("config/settings.ini")); }
				catch (FileAlreadyExistsException a ) { System.out.println("Settings File Already Created! Skipping!"); }
				catch (IOException b) { System.out.println(b.toString()); }


				try {
					Wini settings = new Wini(new File("config/settings.ini"));
					settings.put("user", "API", key);
					settings.put("user", "URL", url);
					settings.store();
					confirmed = true;
				}

				catch (IOException j) { System.out.println(j.toString()); }

				new MainMenu(url, headers);
			}

			else { error.setVisible(true); }

		}

	}

	private boolean verifyKey() {
		if (url.length() == 0 | key.length() == 0) { return false; }

		String apiTarget = url + "/api/v1/users/activity_stream";
		boolean status = false;

		try {
			HttpResponse<JsonNode> response = Unirest.get(apiTarget).header(headers[0], headers[1]).asJson();

			if (response.getStatusText().equals("OK")) { status = true; }

		}

		catch (UnirestException e) {
			System.out.println(e.toString());
			return false;
		}

		return status;
	}
}
