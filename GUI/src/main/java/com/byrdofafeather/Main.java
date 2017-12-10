package com.byrdofafeather;

import java.util.ArrayList;
import java.util.Map;
import org.json.JSONObject;

public class Main {
    public static void main(String[] args) {
        String test[] = new String[2];
        test[0] = "Authorization";
        test[1] = "Bearer Secret Key";

        Module Moduler = new Module("http://nccs.instructure.com", test, 9360,8803);
        Map<String, String> userDict = Moduler.getClassUsers();
        Moduler.getModuleItems();
        Map<String, ArrayList<JSONObject>> items = Moduler.getModuleSubsections();
        ArrayList<JSONObject> quiz = items.get("Quizzes");
        JSONObject cur_quiz = quiz.get(0);
        int quizID = cur_quiz.getInt("content_id");
        System.out.println(quizID);
        Quiz quizTest = new Quiz(Moduler.url, Moduler.header, 9360, quizID);
    }
}
