package com.byrdofafeather;


import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.JsonNode;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


class ClassCollectors {
	String header[] = new String[2];
	String url = null;
	String classID = null;

	ClassCollectors() {
		System.out.println("Did not get API information! Things probably aren't going to work!");
	}

	ClassCollectors(String usrURL, String[] usrHeader, int usrClassID) {
		header = usrHeader;
		url = usrURL;
		classID = Integer.toString(usrClassID);
	}

	/**
	 * Gets all of the users in a specific class
	 *
	 * @return A map linking user IDs to names
	 * @see ClassCollectors
	 */
	Map<String, String> getClassUsers() {
		String apiTarget = url + "/api/v1/courses/" + classID + "/enrollments?per_page=50";
		HttpResponse<JsonNode> users;
		Map<String, String> userDict = new HashMap<String, String>();

		try {
			users = Unirest.get(apiTarget).header(header[0], header[1]).asJson();
			JsonNode userBody = users.getBody();
			JSONArray userArray = userBody.getArray();
			// Iterates through the list of JSON objects returned
			for (int i = 0; i < userArray.length(); i++) {

				JSONObject cur = userArray.getJSONObject(i);
				System.out.println(cur);
				String userID = Integer.toString(cur.getInt("user_id"));

				JSONObject user = cur.getJSONObject("user");
				String userName = user.getString("name");

				userDict.put(userID, userName);
			}
		} catch (UnirestException e) {
			System.out.println(e.toString());
			userDict = null;
		}

		return userDict;
	}

	Map<String, String> getCourseModules() {
		String apiTarget = url + "/api/v1/courses/" + classID + "/modules";
		HttpResponse<JsonNode> modules;
		Map<String, String> modulesDict = new HashMap<>();

		try {
			modules = Unirest.get(apiTarget).header(header[0], header[1]).asJson();
			JsonNode modulesBody = modules.getBody();
			JSONArray modulesArray = modulesBody.getArray();
			for (int i = 0; i < modulesArray.length(); i++) {
				JSONObject currentModule = modulesArray.getJSONObject(i);
				if (currentModule.getBoolean("published")) {
					String currentName = currentModule.getString("name");
					String currentID = Integer.toString(currentModule.getInt("id"));
					modulesDict.put(currentName, currentID);
				}
			}
		}

		catch (UnirestException e) { System.out.println(e.toString()); }

		return modulesDict;
	}

}

/**
 * Collector Subclass that represents and collects data from one module
 *
 * @see ClassCollectors
 */
class Module extends ClassCollectors {
	String moduleID = null;

	Module(String usrURL, String[] usrHeader, int usrClassID, int usrModuleID) {
		super(usrURL, usrHeader, usrClassID);
		moduleID = Integer.toString(usrModuleID);
		getModuleQuizzesDict();
	}

	/**
	 * Gets all the objects in a module that look like notes (ExternalURLS and Files)
	 *
	 * @param items The original JSONArray representing a fully returned module items query.
	 * @return An array containing JSON Objects representing items from the original array that fit note criteria.
	 */
	private ArrayList<JSONObject> getModuleNotes(JSONArray items) {
		ArrayList<JSONObject> quizArray = new ArrayList<JSONObject>();
		for (int i = 0; i < items.length(); i++) {
			JSONObject cur = items.getJSONObject(i);
			String type = cur.getString("type");
			if (type.equals("File")) {
				quizArray.add(items.getJSONObject(i));
			} else if (type.equals("ExternalUrl")) {
				quizArray.add(items.getJSONObject(i));
			}
		}
		return quizArray;
	}

	/**
	 * Gets all the objects in a module that are labeled quizzes
	 *
	 * @param items The original JSONArray representing a fully returned module items query.
	 * @return An array containing JSON Objects representing items from the original array that fit Quiz criteria.
	 */
	private ArrayList<JSONObject> getModuleQuizzes(JSONArray items) {
		ArrayList<JSONObject> quizArray = new ArrayList<JSONObject>();
		for (int i = 0; i < items.length(); i++) {
			JSONObject cur = items.getJSONObject(i);
			String type = cur.getString("type");
			if (type.equals("Quiz")) {
				quizArray.add(items.getJSONObject(i));
			}
		}
		return quizArray;
	}

	/**
	 * Gets all the items in a module in a overall and subsections format
	 *
	 * @return JSONArray containing the full list of module items
	 */
	public JSONArray getModuleItems() {
		String apiTarget = url + "/api/v1/courses/" + classID + "/modules/" + moduleID + "/items";
		HttpResponse<JsonNode> items;
		JSONArray Overall;

		try {
			items = Unirest.get(apiTarget).header(header[0], header[1]).asJson();
			JsonNode itemsBody = items.getBody();
			Overall = itemsBody.getArray();
		} catch (UnirestException e) {
			System.out.println(e.toString());
			Overall = null;
		}

		return Overall;
	}

	/**
	 * Gets subsection items from the module and maps them to ArrayLists
	 *
	 * @return A map linking Notes and Quizzes together Map<Section, ArrayList<JSONObject>>
	 * @see Module#getModuleQuizzes(JSONArray)
	 * @see Module#getModuleNotes(JSONArray)
	 */
	public Map<String, ArrayList<JSONObject>> getModuleSubsections() {
		String apiTarget = url + "/api/v1/courses/" + classID + "/modules/" + moduleID + "/items";
		HttpResponse<JsonNode> items;
		Map<String, ArrayList<JSONObject>> subsections = new HashMap<String, ArrayList<JSONObject>>();

		try {
			items = Unirest.get(apiTarget).header(header[0], header[1]).asJson();
			JsonNode itemsBody = items.getBody();
			JSONArray itemsArray = itemsBody.getArray();

			subsections.put("Notes", this.getModuleNotes(itemsArray));
			subsections.put("Quizzes", this.getModuleQuizzes(itemsArray));
		} catch (UnirestException e) {
			System.out.println(e.toString());
		}
		return subsections;
	}

	public Map<String, String> getModuleQuizzesDict() {
		Map<String, ArrayList<JSONObject>> subsections = getModuleSubsections();
		ArrayList<JSONObject> quizObjects = subsections.get("Quizzes");
		Map<String, String> quizDict = new HashMap<>();

		for (int i = 0; i < quizObjects.size(); i++) {
			JSONObject currentQuiz = quizObjects.get(i);
			String quizName = currentQuiz.getString("title");
			String quizID = Integer.toString(currentQuiz.getInt("content_id"));
			quizDict.put(quizName, quizID);
		}

		return quizDict;
	}
}

class Quiz extends ClassCollectors {
	String quizID = null;
	Map<String, String> submissionIndex;

	Quiz(String usrURL, String[] usrHeader, int usrClassID, int userQuizID) {
		super(usrURL, usrHeader, usrClassID);
		quizID = Integer.toString(userQuizID);
		submissionIndex = getUserSubmissionIndex();
	}

	/**
	 * Gets a submission index, linking users to their quiz submissions
	 *
	 * @return A Map connecting a users submission ID to their actual user ID.
	 */
	private Map<String, String> getUserSubmissionIndex() {
		String apiTarget = url + "/api/v1/courses/" + classID + "/quizzes/" + quizID + "/submissions?per_page=50";
		Map<String, String> index = new HashMap<String, String>();

		try {
			HttpResponse<JsonNode> submissionObjects = Unirest.get(apiTarget).header(header[0], header[1]).asJson();

			JsonNode submissionBody = submissionObjects.getBody();
			JSONArray submissionArray = submissionBody.getArray();
			JSONObject submissionsList = submissionArray.getJSONObject(0); // Allows for string indexing
			JSONArray submissions = submissionsList.getJSONArray("quiz_submissions"); // Gets the actual list

			for (int i = 0; i < submissions.length(); i++) {
				JSONObject cur = submissions.getJSONObject(i);

				String userID = Integer.toString(cur.getInt("user_id"));
				String submissionID = Integer.toString(cur.getInt("id"));

				index.put(submissionID, userID);
			}
		} catch (UnirestException e) {
			System.out.println(e.toString());
		}

		return index;
	}

	public ArrayList<JSONObject> getSubmissionEvents() {
		System.out.println("Getting Submission Events");
		String apiTarget = url + "/api/v1/courses/" + classID + "/quizzes/" + quizID + "/submissions?per_page=50";
		ArrayList<JSONObject> submissionEvents = new ArrayList<JSONObject>();

		try {
			HttpResponse<JsonNode> submissionObjects = Unirest.get(apiTarget).header(header[0], header[1]).asJson();

			JsonNode submissionBody = submissionObjects.getBody();
			JSONArray submissionArray = submissionBody.getArray();
			JSONObject submissionsList = submissionArray.getJSONObject(0); // Allows for string indexing
			JSONArray submissions = submissionsList.getJSONArray("quiz_submissions"); // Gets the actual list

			for (int i = 0; i < submissions.length(); i++) {
				JSONObject cur = submissions.getJSONObject(i);
				submissionEvents.add(cur);
			}

		} catch (UnirestException e) {
			System.out.println(e.toString());
		}

		return submissionEvents;
	}


	/**
	 * Gets the individual IDS for questions and specific information
	 *
	 * @return a Map with a String array containing the original text, placement, and answers
	 */
	private Map<String, String[]> getQuizQuestionIDs() {
		System.out.println("Getting Quiz Question IDs");
		String apiTarget = url + "/api/v1/courses/" + classID + "/quizzes/" + quizID + "/questions";
		Map<String, String[]> questionIDs = new HashMap<String, String[]>();

		try {
			HttpResponse<JsonNode> questions = Unirest.get(apiTarget).header(header[0], header[1]).asJson();
			JsonNode questionsBody = questions.getBody();
			JSONArray questionsArray = questionsBody.getArray();
			for (int i = 0; i < questionsArray.length(); i++) {
				JSONObject curQuestion = questionsArray.getJSONObject(i);
				String questionID = Integer.toString(curQuestion.getInt("id"));

				String questionText = curQuestion.getString("question_text");
				String questionPosition = Integer.toString(curQuestion.getInt("position"));
				String questionAnswers = curQuestion.getJSONArray("answers").toString();
				String curArray[] = new String[3];

				curArray[0] = questionText;
				curArray[1] = questionPosition;
				curArray[2] = questionAnswers;

				questionIDs.put(questionID, curArray);
			}
		} catch (UnirestException e) {
			System.out.println(e.toString());
		}

		return questionIDs;
	}

	/**
	 * Gets a Map of users linked to their question answered event(s) for this particular quiz
	 *
	 * @return A map indexed with user ids and resulting in a array of question answered event jsons
	 * @see Quiz#getQuizEvents()
	 * @see Quiz#getQuizQuestionIDs()
	 */
	Map<String, ArrayList<JSONObject>> getQuestionsAnswered() {
		System.out.println("Getting Questions Answered");
		Map<String, JSONObject> events = getQuizEvents();
		Map<String, ArrayList<JSONObject>> questionsAnswered = new HashMap<String, ArrayList<JSONObject>>();
		List<String> userIDs = new ArrayList<String>(events.keySet());
		Map<String, String[]> questionIDs = getQuizQuestionIDs();

		for (int i = 0; i < events.size(); i++) {
			String curUser = userIDs.get(i);
			JSONObject curEventsObjects = events.get(curUser);
			ArrayList<JSONObject> curQuestionsAnswered = new ArrayList<JSONObject>();

			JSONArray curEventsArray = curEventsObjects.getJSONArray("quiz_submission_events");

			for (int j = 0; j < curEventsArray.length(); j++) {
				JSONObject curEvent = curEventsArray.getJSONObject(j);
				if (curEvent.getString("event_type").equals("question_answered")) {
					curQuestionsAnswered.add(curEvent);
				}
			}
			questionsAnswered.put(curUser, curQuestionsAnswered);

			for (int g = 0; g < questionsAnswered.get(curUser).size(); g++) {
				JSONObject curEvent = questionsAnswered.get(curUser).get(g);
				JSONArray curDataArray = curEvent.getJSONArray("event_data");
				JSONObject curData = curDataArray.getJSONObject(0);

				String currentID = Integer.toString(curData.getInt("quiz_question_id"));
				String quizText = questionIDs.get(currentID)[0];
				String quizOrder = questionIDs.get(currentID)[1];

				curData.put("question_text", quizText);
				curData.put("order", quizOrder);
			}
			questionsAnswered.get(curUser).remove(0);
		}
		return questionsAnswered;
	}

	Map<String, ArrayList<JSONObject>> getPageLeaves() {
		System.out.println("Getting Page Leaves");
		Map<String, JSONObject> events = getQuizEvents();
		Map<String, ArrayList<JSONObject>> pageLeaves = new HashMap<String, ArrayList<JSONObject>>();
		List<String> userIDs = new ArrayList<String>(events.keySet());

		for (int i = 0; i < events.size(); i++) {
			String curUser = userIDs.get(i);
			JSONObject curEventsObjects = events.get(curUser);
			ArrayList<JSONObject> curQuizEvents = new ArrayList<JSONObject>();

			JSONArray curEventsArray = curEventsObjects.getJSONArray("quiz_submission_events");

			for (int j = 0; j < curEventsArray.length(); j++) {
				JSONObject curEvent = curEventsArray.getJSONObject(j);
				if (curEvent.getString("event_type").equals("page_blurred") |
						curEvent.getString("event_type").equals("page_focused")) {

					curQuizEvents.add(curEvent);
				}
			}
			pageLeaves.put(curUser, curQuizEvents);
		}

		return pageLeaves;
	}

	/**
	 * Gets the events of a quiz
	 *
	 * @return A map indexed by user ID and resulting in a JSONObject
	 * @see Quiz#getUserSubmissionIndex()
	 */
	Map<String, JSONObject> getQuizEvents() {
		System.out.println("Getting Quiz Events");
		String apiTarget = url + "/api/v1/courses/" + classID + "/quizzes/" + quizID + "/submissions/";
		Map<String, JSONObject> events = new HashMap<String, JSONObject>();
		List<String> submissionIDs = new ArrayList<String>(submissionIndex.keySet());

		for (int i = 0; i < submissionIndex.size(); i++) {
			String submissionID = submissionIDs.get(i);
			String curAPITarget = apiTarget + submissionID + "/events";
			try {
				HttpResponse<JsonNode> curEventsResponse = Unirest.get(curAPITarget).header(header[0], header[1]).asJson();
				JsonNode curEventsNode = curEventsResponse.getBody();
				JSONArray curEventsArray = curEventsNode.getArray();
				JSONObject curEvents = curEventsArray.getJSONObject(0);

				String userID = submissionIndex.get(submissionID);
				events.put(userID, curEvents);
			} catch (UnirestException e) {
				System.out.println(e.toString());
			}
		}
		return events;
	}
}

//class Discussion extends ClassCollectors {
//	String discussionID = null;
//
//	Discussion(String usrURL, String[] usrHeader, int usrClassID, int usrDiscussionID) {
//		super(usrURL, usrHeader, usrClassID);
//		discussionID = Integer.toString(usrDiscussionID);
//	}
//}
