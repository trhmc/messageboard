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
	print('help\t\tReturn the help menu')
	print('connect\t\tCommand to connect to the server')
	print('exit\t\tCommand to exit the server')
	print('join\t\tCommand to join the message board')
	print('leave\t\tCommand to leave the message board')
	print('post\t\tCommand to post in the message board')
	print('message\t\tCommand to retrieve message in the message board')
	print('users\t\tCommand to retrieve list of users in the message board')
	print('groups\t\tCommand to retrieve list of available groups in the message board')
	print('group_join\tCommand to join a group')
	print('group_leave\tCommand to leave a group')
	print('group_post\tCommand to post in a group')
	print('group_message\tCommand to retrieve message in a group')
	print('group_users\tCommand to retrieve list of users in a group')
	print("Press Ctrl+C to stop.")

IP = "192.168.86.26"
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
	print("Message board\nIP: "+IP+"\nPort: "+str(PORT))
	help()
	try:
		while (not end):
			opt = input("Enter a command: ")
			# for when the user needs the command menu
			if opt == "help":
				help()
			elif opt == "connect":
				server_ip = input("Enter server ip address: ")
				server_port = input("Enter server port: ")
				if (server_ip == IP) and (int(server_port) == PORT):
					user_s.connect((server_ip, int(server_port)))
					print("Connected to "+server_ip+"-Port: "+server_port)
				else:
					print("Could not connect to "+server_ip+"-Port: "+server_port)
			elif opt == "exit":
				user_s.send(create_json(opt,username,'','').encode())
				end = True
			elif opt == "join":
				username = input("Enter your username: ")
				user_s.send(create_json(opt,username,"","").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Needs a youve joined a group message and access to the most recent 2 message
				msg = server_msg["Data"].split('\n\r')
				for m in msg:
					print(m)
			elif opt == "leave":
				user_s.send(create_json(opt,username,"","").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Needs a simple you've left the group message
				print(server_msg["Data"])
			elif opt == "post":
				sub = input("Enter your Subject: ")
				msg = sub + "\n\r" + input("Enter your message: ")
				user_s.send(create_json(opt,username,"", msg).encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Should recieve back your message on the message board below the most recent message
				print(server_msg["Data"])
			elif opt == "users":
				user_s.send(create_json(opt,username,"","").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Should recieve back a list of all users 
				print(server_msg["Data"])
			elif opt == "message":
				msg_id = input("Enter the msg id: ")
				user_s.send(create_json(opt, username, "", msg_id).encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#should recieve back the specific message requested
				print(server_msg["Data"])
			#
			#
			#Group Section 
			elif opt == "groups":
				user_s.send(create_json(opt,username,"","").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Needs a list of all possible groups
				print(server_msg["Data"])
			elif opt == "group_join":
				gNum = input("Enter the group you would like to join: ")
				user_s.send(create_json(opt,username,gNum,"").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Needs a youve joined a group message and access to the most recent 2 message of that specific group
				print(server_msg["Data"])
			elif opt == "group_leave":
				gNum = input("Enter which group would you like to leave: ")
				user_s.send(create_json(opt,username,gNum,"").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Needs a simple you've left the group message perferrably with the number of the group
				print(server_msg["Data"])
			elif opt == "group_post":
				gNum = input("Enter which group you would like to post to: ")
				sub = input("Enter your Subject: ")
				msg = sub + "\n\r" + input("Your Message: ")
				user_s.send(create_json(opt,username,gNum, msg).encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Should recieve back your message on the message board below the most recent message
				print(server_msg["Data"])
			elif opt == "group_users":
				gNum = input("Enter which group you would like to view its users: ")
				user_s.send(create_json(opt,username,gNum,"").encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#Should recieve back a list of all users for that specific group 
				print(server_msg["Data"])
			elif opt == "group_message":
				gNum = input("Enter which group was the message posted to: ")
				msg_id = input("Enter the msg id: ")
				user_s.send(create_json(opt, username, gNum, msg_id).encode())
				server_msg = convert_json(data=user_s.recv(1024))
				#should recieve back the specific message requested
				print(server_msg["Data"])
			else:
				print("Command Invalid")
	except KeyboardInterrupt:
		print("Keyboard Interrupted, exiting")

	print("Message board terminating...")
	user_s.close()