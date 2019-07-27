import base64
import json
import os
import threading
from typing import Optional

import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib.auth.models import User
from fcm_django.models import FCMDevice
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from API.predictors import classify
from API.serializers import CustomAuthSerializer, UserSerializer
from API.models import Queuer
from CanvasWrapper.views import error_generator


def get_key(encryption_key: str) -> bytes:
	"""Gets a suitable base64encoded key based on the string passed
	:param encryption_key: A string (probably user provided) that will serve as the key for the encryption
	:return: A bytes-like to be used in encryption
	"""
	encryption_key = encryption_key.encode()  # Converts the key to a bytes object
	salt = os.environ.get("SALT_KEY", "I'm just a placeholder for development!").encode()  # Gets the salt key
	kdf = PBKDF2HMAC(  # Builds a object to derive the key
		algorithm=hashes.SHA256(),
		length=32,
		salt=salt,
		iterations=100000,
		backend=default_backend()
	)
	return base64.urlsafe_b64encode(kdf.derive(encryption_key))  # Returns the key


def parse_data(data):
	frame = pd.DataFrame.from_dict(data, orient="index")
	return frame


def push_notification(cheaters: Optional[list], non_cheaters: Optional[list], user: User) -> None:
	"""WIP. Sends a push notification to the device from which the request originated (TODO: UPDATE DOCUMENTATION)
	:param cheaters: Bytes like encrypted data that represents the cheaters
	:param non_cheaters: Bytes like encrypted data that represents the non cheaters
	:param user: The user that originally sent the request for the data to be processed
	:return:
	"""
	device = FCMDevice.objects.get(user=user)
	if cheaters is None:
		data = {
			"click_action": "FLUTTER_NOTIFICATION_CLICK",
			"screen": "/results",
			"status": "done",
			"sound": "default",
			"results": {
				"message": "Could not separate data into cheaters and non cheaters!"
			}
		}
	else:
		data = {
			"click_action": "FLUTTER_NOTIFICATION_CLICK",
			"screen": "/results",
			"status": "done",
			"sound": "default",
			"results": {
				"cheaters": cheaters,
				"non_cheaters": non_cheaters,
			}
		}

	device.send_message(title="Data ready to view!", body="A quiz has been scanned for cheaters!", data=data)
	pass


def process_mobile_data(data, user):
	del data["secret"]
	# TODO Actually interpret this data
	storage = data["storage"]
	del data["storage"]
	key = get_key(data["encryption_key"])
	del data["encryption_key"]

	data = parse_data(data)
	cheaters, non_cheaters = classify(data)

	if cheaters is None:
		push_notification(None, None, user)

	cheaters, non_cheaters = cheaters, non_cheaters

	queue = Queuer.objects.get(unique_name="Task Queue")

	queue.currently_running = False
	queue.save()
	push_notification(cheaters, non_cheaters, user)


# TODO: More research is required into securing this API
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mobile_endpoint(request):
	# TODO Clean Data
	data = request.POST.get("data", "")
	data = json.loads(data)
	queuer = Queuer.objects.get(unique_name="Task Queue") if \
		Queuer.objects.filter(unique_name="Task Queue").count() else \
		Queuer.objects.create(unique_name="Task Queue", currently_running=False)
	try:
		# Temp security solution for mobile app while in development
		if data["secret"] == os.environ.get("MOBILESECRET", ""):
			if queuer.currently_running:
				return error_generator("A task is already running, try again later!", 202)

			queuer.currently_running = True
			queuer.save()
			task = threading.Thread(target=process_mobile_data, args=[data, request.user])
			task.start()
			response = JsonResponse({"success": {"data": "Your data is being processed and will be returned soon!"}})
			response.status_code = 200
			return response
		else:
			response = JsonResponse({"error": "shoot!"})
			response.status_code = 402
			return response

	except KeyError:
		error_generator("Invalid JSON!", 400)


@api_view(["POST"])
def create_user(request):
	# TODO: Implementation
	data = request.POST.get("data")
	data = json.loads(data)
	username, password = data["username"], data["password"]
	if User.objects.filter(username=username).count():
		# TODO: Fix error code
		return error_generator("Username in use!", 401)
	new_user = User.objects.create(
		username=username,
		password=password
	)
	token = Token.objects.get_or_create(new_user)
	response = JsonResponse({"success": {"data": {"token": token}}})
	response.status_code = 200
	return response


@api_view(["POST"])
def register_user(request):
	serialized = UserSerializer(data=request.data)
	if serialized.is_valid():
		user = User.objects.create(
			username=serialized.validated_data["username"],
		)
		user.set_password(serialized.validated_data["password"])

		FCMDevice.objects.create(user=user,
		                         registration_id=serialized.validated_data["notification_token"],
		                         type=serialized.validated_data["device"])

		token, created = Token.objects.get_or_create(user=user)
		return Response({"success": {"data": {"token": token.key}}}, status=200)
	else:
		print(serialized.errors)
		return Response({"error": {"data": serialized.errors}}, status=406)


class CustomObtainAuthToken(ObtainAuthToken):
	# TODO: Create logic for logging in from a new device!
	serializer_class = CustomAuthSerializer

	def post(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data,
		                                  context={'request': request})
		serializer.is_valid(raise_exception=True)
		user = serializer.validated_data["user"]
		notification_token = serializer.validated_data["notification_token"]
		token = FCMDevice.objects.filter(user=user)
		if token.count():
			token = token[0]
			token.notification_key = notification_token
			token.save()
		else:
			FCMDevice.objects.create(user=user,
			                         registration_id=notification_token,
			                         type=serializer.validated_data["device"])

		token, created = Token.objects.get_or_create(user=user)
		return Response({"success": {"data": {"token": token.key}}}, status=200)

