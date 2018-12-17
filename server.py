from flask import Flask, jsonify, request
from flask_cors import CORS
from hackerman.crypto import xor
from hackerman import utils
import json

class Server(object):
	def __init__(self, users={}, messages=[]):
		self.users = users
		self.messages = messages
	def add_user(self, username, password):
		if username in self.users:
			return False
		else:
			self.users[username] = password
			return True
	def run(self, host="0.0.0.0", port=8000):
		app = Flask(__name__)
		CORS(app)

		@app.route("/messages", methods=["POST"])
		def return_messages():
			dat = request.form
			if not dat['user'] in self.users:
				return "status: unauthorized", 401
			m = json.dumps(self.messages).encode()
			e = xor.encrypt(m, self.users[dat['user']])
			return utils.b64e(e)

		@app.route("/send", methods=['POST'])
		def send_message():
			dat = request.form
			if not dat['user'] in self.users:
				return "status: unauthorized", 401
			enc = utils.b64d(dat['msg'])
			msg = xor.decrypt(enc, self.users[dat['user']])
			self.messages.append(msg)
			return "status: ok"

		@app.route("/register", methods=['POST'])
		def new_user():
			usr = request.form['user']
			pwd = request.form['pass']
			res = self.add_user(usr, pwd)
			if res:
				return "status: ok"
			else:
				return "status: user already exists"

		app.run(host=host, port=port)

if __name__ == "__main__":
	Server().run()