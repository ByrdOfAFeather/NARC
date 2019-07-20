from django.urls import path
from rest_framework.authtoken import views as v
from . import views

app_name = "api"
urlpatterns = [
	path("post_mobile/", view=views.mobile_endpoint, name="mobile-endpoint"),
	path("token_auth/", view=views.CustomObtainAuthToken.as_view(), name="token-auth"),
	path("create_user/", view=views.register_user, name="create-user")
]
