from django.urls import path

from . import views

app_name = "mainpages"
urlpatterns = [
	path("", view=views.index, name="index"),
	path("courses/", view=views.courses, name="courses-view"),
	path("course/<int:course_id>/", view=views.course, name="course"),
	path("course/<int:course_id>/<int:module_id>/", view=views.module, name="module"),
	path("course/<int:course_id>/<int:module_id>/<int:quiz_id>", view=views.quiz, name="quiz"),
	path("about/", view=views.about, name="about"),
	path("contact/", view=views.contact, name="contact"),
	path("oauth_confirm/", view=views.oauth_authorization, name="oauth-authorization"),
	path("what_we_do/", view=views.what_we_do, name="what-we-do"),
	path("privacy_policy", view=views.privacy_policy, name="privacy-policy",),
	path("ferpa_act_compliance", view=views.ferpa_act_compliance, name="ferpa-act-compliance")

]
