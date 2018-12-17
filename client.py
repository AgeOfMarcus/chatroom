import requests, json, getpass, time, os
from hackerman import utils
from hackerman.crypto import xor
from termcolor import colored as c

wd = os.getcwd()
if "/" in wd:
	clear = lambda: os.system("clear")
elif "\\" in wd:
	clear = lambda: print("\n"*100)
else:
	clear = lambda: print("\n"*100)

class Client(object):
	def __init__(self, server, username, password):
		if server.endswith("/"):
			self.server = server[:-1]
		else:
			self.server = server
		self.usr = username
		self.pwd = password

	def recv(self):
		dat = requests.post(self.server+"/messages", 
			data={'user':self.usr})
		if dat.status_code == 401:
			raise BaseException(dat.content.decode())
		dec = xor.decrypt(utils.b64d(dat.content.decode()), self.pwd)
		msg = json.loads(dec.decode())
		return msg

	def send(self, msg):
		dat = {'user':self.usr, 'time':time.time(),
		'msg':msg}
		enc = xor.encrypt(json.dumps(dat).encode(), self.pwd)
		req = requests.post(self.server+"/send",
			data={'user':self.usr, 'msg':utils.b64e(enc)})
		if req.status_code == 401:
			raise BaseException(req.content.decode())
		else:
			return True

	def register(self):
		r = requests.post(self.server+"/register",
			data={'user':self.usr, 'pass':self.pwd})
		if r.content.decode() == "status: ok":
			return True
		else:
			return False

# colours
alert = lambda msg: c("[!]","red")+" "+msg
plus = lambda msg: c("[+]","green")+" "+msg
info = lambda msg: c("[*]","cyan")+" "+msg

def main():
	url = input("Enter server address: ")
	usr = input("Enter username: ")
	pwd = getpass.getpass("Enter password: ")
	cl = Client(url, usr, pwd)
	try:
		msg = cl.recv()
	except BaseException:
		print(alert("Error recieving messages."))
		rg = input(info("Attempt to register user? Y/n: ")).lower()
		if rg == "n":
			return 1
		else:
			done = cl.register()
			if not done:
				print(alert("Unable to register user."))
				return 1
			else:
				print(plus("User has been registered"))
	while True:
		try:
			msg = cl.recv()
			a = clear()
			time.sleep(0.5)
			for m in msg:
				t = str(m['time'])
				while len(t) < 18:
					t += "0"
				print("{%s} [%s] > %s" % (
						c(t,"blue"),
						c(m['user'],"green"),
						m['msg']
					))
		except KeyboardInterrupt:
			try:
				msg = input("[%s] >>> " % c(cl.usr,"green"))
				cl.send(msg)
			except KeyboardInterrupt:
				return 0

if __name__ == "__main__":
	exit(main())