import base64
import json
import os
import threading
import pandas as pd
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated

from API.predictors import classify
from CanvasWrapper.views import error_generator
from API.models import Queuer


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


def push_notification(cheaters: bytes, non_cheaters: bytes) -> None:
	"""WIP. Sends a push notification to the device from which the request originated (TODO: UPDATE DOCUMENTATION)
	:param cheaters: Bytes like encrypted data that represents the cheaters
	:param non_cheaters: Bytes like encrypted data that represents the non cheaters
	:return:
	"""
	push_json = {"notification": {
		"title": "Data Processed!",
		"body": "The results for your recent request are ready to be reviewed!",
	},
		"data": {
			"click_action": "FLUTTER_NOTIFICATION_CLICK",
			"sound": "default",
			"status": "done",
			"screen": "results",
			"results": {
				"cheaters": str(cheaters)[2:-1],
				"non_cheaters": str(non_cheaters)[2:-1],
			}
		}
	}
	print("DATA IS READY TO BE RETRIEVED")
	pass


def process_mobile_data(data):
	del data["secret"]
	# TODO Actually interpret this data
	storage = data["storage"]
	del data["storage"]
	key = get_key(data["encryption_key"])
	del data["encryption_key"]

	data = parse_data(data)
	cheaters, non_cheaters = classify(data)
	cheaters, non_cheaters = json.dumps(cheaters).encode(), json.dumps(non_cheaters).encode()

	encryptor = Fernet(key)
	cheaters = encryptor.encrypt(cheaters)
	non_cheaters = encryptor.encrypt(non_cheaters)
	queue = Queuer.objects.get(unique_name="Task Queue")

	queue.currently_running = False
	queue.save()
	push_notification(cheaters, non_cheaters)


# TODO: More research is required into securing this API
@api_view(["POST"])
@authentication_classes([SessionAuthentication, TokenAuthentication, BasicAuthentication])
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
			# process_mobile_data.dely(data, task_id)
			task = threading.Thread(target=process_mobile_data, args=[data])
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
