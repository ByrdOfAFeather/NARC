from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.serializers import AuthTokenSerializer


class CustomAuthSerializer(AuthTokenSerializer):
	username = serializers.CharField(write_only=True)
	password = serializers.CharField(write_only=True)
	notification_token = serializers.CharField(write_only=True)

	def validate(self, attrs):
		attrs = super().validate(attrs)
		if attrs["notification_token"]:
			return attrs
		else:
			# TODO come back and edit code
			raise serializers.ValidationError("FCM Token required!", code="authorization")


class UserSerializer(serializers.ModelSerializer):
	notification_token = serializers.ReadOnlyField()

	def validate(self, attrs):
		super().validate(attrs)
		try:
			validate_password(attrs["password"])
			return attrs
		except ValidationError:
			raise serializers.ValidationError({"password": "Password does not meet requirements!"}, code=406)

	class Meta:
		model = User
		fields = ("username", "password", "notification_token")
