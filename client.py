import socket
import json

def convert_json(data, mode=1):
	"""
	2 modes of converting a data
	mode=1: json data to dictionary
	mode=0: dictionary to json data
	"""
	# json -> dict
	if mode:
		j = json.loads(data.decode('utf-8'))
	# dict -> json
	else:
		j = json.dumps(data)
	return j

def create_json(opt, username, group, data):
	message = {"Type": opt,
				"Username": username,
				"Group": group,
				"Data": data}
	return json.dumps(message)

def help():
	print('Commands: ')
	print('connect ip port')
	print('exit')
	print('join')
	print('leave')
	print('post')
	print('message')

IP = "10.10.28.110"
PORT = 12345

if __name__ == "__main__":
	user_s = socket.socket()
	server_ip = ""
	server_port = ""
	opt = ""
	username = ""
	grp = ""
	data = ""
	end = False
	print(IP)
	help()
	try:
		while (not end):
			opt = input("Enter a command: ")
			if opt == "connect":
				server_ip = input("Enter server ip address: ")
				server_port = input("Enter server port: ")
				if (server_ip == IP) and (int(server_port) == PORT):
					user_s.connect((server_ip, int(server_port)))
					print("Connected to "+server_ip+"-Port: "+server_port)
				else:
					print("Could not connect to "+server_ip+"-Port: "+server_port)
			elif opt == "exit":
				user_s.send(create_json('exit','','','').encode())
				end = True
			elif opt == "join":
				username = input("Enter your username: ")
				user_s.send(create_json("join",username,"","").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				print(server_msg["Data"])

			elif opt == "leave":
				user_s.send(create_json("leave",username,"","").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				print(server_msg["Data"])
			elif opt == "post":
				msg = input("Your message: ")
				user_s.send(create_json("post",username,"", msg).encode())
				server_msg = convert_json(data=user_s.recv(1024))
				print(server_msg["Data"])
			elif opt == "users":
				user_s.send(create_json("users",username,"","").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				print(server_msg["Data"])
			elif opt == "message":
				msg_id = input("Enter the msg id: ")
				user_s.send(create_json("message", username, "", msg_id).encode())
				server_msg = convert_json(data=user_s.recv(1024))
				print(server_msg["Data"])
	except KeyboardInterrupt:
		print("Keyboard Interrupted, exiting")

	print("Message board terminating...")
	user_s.close()