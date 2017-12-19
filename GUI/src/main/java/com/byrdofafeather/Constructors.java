package com.byrdofafeather;

import org.json.JSONObject;
import org.nd4j.linalg.api.ndarray.INDArray;
import org.nd4j.linalg.factory.Nd4j;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Constructors {
}

class QuizEvents {
	Map<String, ArrayList<JSONObject>> questionsAnswered = null;
	private ArrayList<JSONObject> submissions = null;
	private boolean anon = false;
	private Quiz quiz;
	Map<String, Map<String, Float>> dataSet = new HashMap<String, Map<String, Float>>();

	QuizEvents(Quiz usrQuiz, boolean usrAnon) {
		quiz = usrQuiz;
		anon = usrAnon;
		getQuestionsAnswered();
		initDataSet();
		System.out.println(buildTensor());
	}

	private void getQuestionsAnswered() {
		submissions = this.quiz.getSubmissionEvents();
		questionsAnswered = this.quiz.getQuestionsAnswered();
	}

	private void initDataSet() {
		System.out.println("Building Constructor Data Set");
		buildUserScores();
		buildUserPageLeaves();
		buildTimeTaken();
	}

	private void buildUserScores() {
		ArrayList<Float> overallScore = new ArrayList<Float>();
		for (int i = 0; i < submissions.size(); i++) {
			JSONObject currentSubmission = submissions.get(i);
			float currentPoints = (float) currentSubmission.getInt("kept_score");
			float pointsPossbile = (float) currentSubmission.getInt("quiz_points_possible");
			float currentScore = currentPoints / pointsPossbile;

			String userID = Integer.toString(currentSubmission.getInt("user_id"));
			Map<String, Float> curMap = new HashMap<String, Float>(1);
			curMap.put("score", currentScore);
			dataSet.put(userID, curMap);
			overallScore.add(currentScore);
		}

		float sum = 0;
		for (float curScore : overallScore) {
			sum += curScore;
		}
		float averageScore = sum / overallScore.size();
		Map<String, Float> curOverallMap = new HashMap<String, Float>(1);
		curOverallMap.put("score", averageScore);
		dataSet.put("Overall", curOverallMap);
	}

	private void buildUserPageLeaves() {
		Map<String, ArrayList<JSONObject>> pageLeavesList = this.quiz.getPageLeaves();
		List<String> userIDIndex = new ArrayList<String>(pageLeavesList.keySet());
		ArrayList<Float> allPageLeaves = new ArrayList<Float>();

		for (int i = 0; i < pageLeavesList.size(); i++) {
			String userID = userIDIndex.get(i);
			ArrayList<JSONObject> pageLeaves = pageLeavesList.get(userID);
			float curLength = pageLeaves.size();
			allPageLeaves.add(curLength);

			Map<String, Float> curMap = new HashMap<String, Float>();
			Map<String, Float> prevMap = dataSet.get(userID);
			curMap.putAll(prevMap);
			curMap.put("page_leaves", curLength);

			dataSet.put(userID, curMap);
		}

		float sum = 0;
		for (float curPageLeaves : allPageLeaves) {
			sum += curPageLeaves;
		}
		float pageLeavesAverage = sum / allPageLeaves.size();

		Map<String, Float> curMap = new HashMap<String, Float>();
		Map<String, Float> prevMap = dataSet.get("Overall");

		curMap.putAll(prevMap);
		curMap.put("page_leaves", pageLeavesAverage);
		dataSet.put("Overall", curMap);
	}

	private void buildTimeTaken() {
		ArrayList<Float> overallTimeTaken = new ArrayList<Float>();

		for (JSONObject curSubmission : submissions) {
			String userID = Integer.toString(curSubmission.getInt("user_id"));
			float curTimeTaken = (float) curSubmission.getInt("time_spent");
			overallTimeTaken.add(curTimeTaken);

			Map<String, Float> curMap = new HashMap<String, Float>();
			Map<String, Float> prevMap = dataSet.get(userID);
			curMap.putAll(prevMap);
			curMap.put("time_taken", curTimeTaken);

			dataSet.put(userID, curMap);
		}

		float sum = 0;
		for (float curPageLeaves : overallTimeTaken) {
			sum += curPageLeaves;
		}
		float timeTakenAverage = sum / overallTimeTaken.size();

		Map<String, Float> curMap = new HashMap<String, Float>();
		Map<String, Float> prevMap = dataSet.get("Overall");

		curMap.putAll(prevMap);
		curMap.put("time_taken", timeTakenAverage);
		dataSet.put("Overall", curMap);

	}

	INDArray buildTensor() {
		List<String> dataSetIndex = new ArrayList<String>(dataSet.keySet());
		List<Float> floatList = new ArrayList<Float>();
		int featureSize = 0;

		for (String curKey : dataSetIndex) {
			if (curKey.equals("Overall")) {
				continue;
			}
			Map<String, Float> curMap = dataSet.get(curKey);
			List<String> curMapIndex = new ArrayList<String>(curMap.keySet());
			featureSize = curMap.size();
			for (String newKey : curMapIndex) {
				floatList.add(curMap.get(newKey));
			}

		}

		float array[] = new float[floatList.size()];

		for (int i = 0; i < array.length; i++) {
			array[i] = floatList.get(i);
		}

		INDArray dataArray = new Nd4j().create(
				array,
				new int[]{dataSetIndex.size() - 1, featureSize},
				'c');
		return dataArray;
	}
}

