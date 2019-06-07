import requests
from flask import Flask, render_template, request, after_this_request
from flask_cors import CORS
from flask_restful import Api, Resource
from flask_json import jsonify

headers = {"Authorization": "Bearer {}"}

main = Flask(__name__)
api = Api(main)
CORS(main, )


# @main.after_request
# def after_request(response):
# 	response.headers.add('Access-Control-Allow-Origin', '*')
# 	response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
# 	response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
# 	return response


@main.route("/")
def index():
	return render_template("home.html", static_url_path="/static")


@main.route("/courseview")
def courseview():
	token = request.cookies.get("token")
	print(token)
	if not token:
		return render_template("error.html")
	else:
		modified_header = headers
		modified_header["Authorization"] = modified_header["Authorization"].format(token)
		courses = requests.get(
			'https://canvas.instructure.com/api/v1/courses?enrollment_state=active&per_page=50&include[]=course_image',
			headers=modified_header
		)




class TokenTest(Resource):
	@staticmethod
	def get():
		args = request.args
		token = args["token"]
		@after_this_request
		def set_cookie_token(response):
			print("I JUST GOT TRIGGERED!")
			response.set_cookie("token", token)
			return response

		modified_header = headers
		modified_header["Authorization"] = modified_header["Authorization"].format(token)
		test = requests.get("http://canvas.instructure.com/api/v1/courses",
		                    headers=modified_header)
		return {'task': 'Hello world'}, 200, {'Set-Cookie': 'token={}'.format(token)}


class Courses(Resource):
	@staticmethod
	def get():
		test = requests.get("http://canvas.instructure.com/api/v1/courses?enrollment_status=active&per+page=50",
		                    headers=headers)
		print(test)
		return test.json()


api.add_resource(TokenTest, '/api/tokenTest')
main.run()
