package com.byrdofafeather;


import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Map;

import org.ini4j.Wini;
import org.json.JSONObject;
import org.nd4j.linalg.api.ndarray.INDArray;


public class Main {
	public static void main(String[] args) {

		// Testing Modules with GUI
		String url = "";
		String key = "";

		try {
			Wini settings = new Wini(new File("config/settings.ini"));
			url = settings.get("user", "URL");
			key = settings.get("user", "API");
		}

		catch (IOException e) {
			TokenSetup setupMenu = new TokenSetup();
			while(!setupMenu.confirmed) { }
			try {
			Wini settings = new Wini(new File("config/settings.ini"));
			url = settings.get("user", "url");
			key = settings.get("user", "API");
			}
			catch (IOException j) {
				System.out.println("Something very wrong is happening! API key has been confirmed, but ini file doesn't exist!");
				System.out.println(j.toString());
			}
		}

		if (url.length() == 0 | key.length() == 0) {
			System.exit(0);
		}

		String headers[] = new String[2];
		headers[0] = "Authorization"; headers[1] = "Bearer " + key;
		MainMenu main = new MainMenu(url, headers);


		// Testing Modules without GUI
//		String test[] = new String[2];
//		test[0] = "Authorization";
//		test[1] = "Bearer Secret Key";
//
//		ClassCollectors ec = new ClassCollectors("http://nccs.instructure.com", test, 9709);
//
//		Module Moduler = new Module("http://nccs.instructure.com", test, 9709, 8894);
//		Map<String, String> userDict = Moduler.getClassUsers();
//		Moduler.getModuleItems();
//		Map<String, ArrayList<JSONObject>> items = Moduler.getModuleSubsections();
//		ArrayList<JSONObject> quiz = items.get("Quizzes");
//		JSONObject cur_quiz = quiz.get(0);
//		int quizID = cur_quiz.getInt("content_id");
//		Quiz quizTest = new Quiz(Moduler.url, Moduler.header, 9709, quizID);
//		QuizEvents cons = new QuizEvents(quizTest, false);
//		INDArray tensor = cons.buildTensor();
//		AutoEncoder jackWalsh = new AutoEncoder(tensor);
	}
}
