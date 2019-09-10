from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.serializers import AuthTokenSerializer


class CustomAuthSerializer(AuthTokenSerializer):
	username = serializers.CharField(write_only=True)
	password = serializers.CharField(write_only=True)
	notification_token = serializers.CharField(write_only=True)
	device = serializers.CharField(max_length=7, write_only=True)

	def validate(self, attrs):
		attrs = super().validate(attrs)
		try:
			# Test if the key exists
			if len(attrs["notification_token"]) == 0:
				raise serializers.ValidationError({"notification_token": "can't use empty FCM Token!"}, 406)
			else:
				if attrs["device"] != "android" and attrs["device"] != "ios":
					raise serializers.ValidationError({"device": "must be android or ios"}, code=406)
				else:
					return attrs
		except KeyError:
			raise serializers.ValidationError({"notification_token": "FCM Token required!"}, code="authorization")


class UserSerializer(serializers.ModelSerializer):
	notification_token = serializers.ReadOnlyField()
	device = serializers.ReadOnlyField()

	def validate(self, attrs):
		super().validate(attrs)
		try:
			validate_password(attrs["password"])
			if self.initial_data["device"] != "android" and self.initial_data["device"] != "ios" \
					and self.initial_data["device"] != "pc":
				raise serializers.ValidationError({"device": "must be android ios or pc"}, code=406)
			# TODO: Validate notification token
			attrs["notification_token"] = self.initial_data["notification_token"]
			attrs["device"] = self.initial_data["device"]
			return attrs
		except ValidationError:
			raise serializers.ValidationError({"password": "Password does not meet requirements!"}, code=406)

	class Meta:
		model = User
		fields = ("username", "password", "notification_token", "device")
