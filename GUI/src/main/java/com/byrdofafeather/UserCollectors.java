package com.byrdofafeather;

import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.JsonNode;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

public class UserCollectors {
	String url;
	String header[] = new String[2];

	UserCollectors() {
		System.out.println("Got no API Data! Exiting!");
		System.exit(0);
	}

	UserCollectors(String usrURL, String usrheader[]) {
		url = usrURL;
		header = usrheader;
	}

	Map<String, String> getAssociatedCourses() {
		String apiTarget = url + "/api/v1/courses?enrollment_state=active&per_page=50";
		HttpResponse<JsonNode> courses;
		Map<String, String> coursesDict = new HashMap<>();

		try {
			courses = Unirest.get(apiTarget).header(header[0], header[1]).asJson();
			JsonNode coursesBody = courses.getBody();
			JSONArray coursesArray = coursesBody.getArray();
			for (int i = 0; i < coursesArray.length(); i++) {
				JSONObject currentCourse = coursesArray.getJSONObject(i);
				String currentName = currentCourse.getString("name");
				String currentID = Integer.toString(currentCourse.getInt("id"));
				coursesDict.put(currentName, currentID);
			}
		}

		catch (UnirestException e) { System.out.println(e.toString()); }

		return coursesDict;
	}
}
