import socket
import sys
import json
import time
from datetime import date

import threading

USERS = []
GROUPS = ['Group 1', 'Group 2', 'Group 3', 'Group 4', 'Group 5']
MESSAGES = {} # 'id: content'
GROUP_MESSAGES = {'Group 1': {},
				'Group 2': {},
				'Group 3': {},
				'Group 4': {},
				'Group 5': {}}
GROUP_USERS = {'Group 1': [],
				'Group 2': [],
				'Group 3': [],
				'Group 4': [],
				'Group 5': []}
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

def join(username):
	# checking if a username is taken or not
	if username in USERS:
		message = create_json('join', username, '', 'Username-taken')
	else:
		USERS.append(username)
		print("Added "+username+" to list of users")
		message = create_json('join', username, '', 'Username-accept')
	return message

def leave(username):
	USERS = [user for user in USERS if user != username]
	print(username+" has left the building.")
	message = create_json('leave', username, '', 'Username-removed')
	return message

def post(username, data):
	# imagine message under format: id\n\rsender\n\rpost_date\n\rmessage
	message_id = len(MESSAGES)
	sender = username
	message = data
	post_date = str(date.today())
	msg = sender+"\n\r"+post_date+"\n\r"+message
	MESSAGES[message_id] = msg
	print(username+" posted a new message")
	print("current # of msg: "+str(len(MESSAGES)))
	return create_json('post', username, '', 'post-success')

def users(username):
	# may think of different way to represent data
	message = create_json('users', username, '', USERS)
	print(username+" retrieved list of users")
	return message

def message(username, data):
	message_id = int(data)
	if message_id in MESSAGES:
		msg = 'Message-retreived:\n'+MESSAGES[message_id]
	else:
		return create_json('message', username, '', 'ID invalid')
	print(username+' retrieve message #'+data)
	return create_json('message', username, '', msg)

def groups(username):
	g = []
	for group in GROUPS:
		if username not in GROUPS[group]:
			g.append(group)
	message = create_json('groups', username, '', g)
	return message

def groupjoin(username, group):
	gtj = group
	# join if user not in group, send error if user already in group
	if username not in GROUPS[gtj]:
		message = create_json('groupjoin', username, group, gtj+'-successfully-joined')
	else:
		message = create_json('groupjoin', username, group, gtj+'-already-joined')
	print(username+" joined group "+gtj)
	return message


def groupleave(username, group):
	gtl = group
	if username in GROUPS[gtl]:
		GROUPS[gtl] = [u for u in GROUPS[gtl] if u != username]
		message = create_json('groupleave', username, group, gtl+'-successfully-left')
	else:
		message = create_json('groupleave', username, group, 'not-in-'+gtl)
	print(username+" left group "+gtl)
	return message

def groupmessage(username, group):
	gm = group
	if username in GROUPS[gm]:
		message = create_json('groupmessage', username, group, gm+'-last-2-message\n\r'+GROUP_MESSAGES[gm][0:2])
	else:
		message = create_json('groupmessage', username, group, 'user-not-in-group')
	print(username+" found msg in "+gm)
	return message

def grouppost(username, group, data):
	gm = group
	message_id = str(len(GROUP_MESSAGES[gm]))
	sender = username
	message = data
	post_date = str(date.today())
	msg = sender+"\n\r"+post_date+"\n\r"+message
	GROUP_MESSAGES[gm][message_id] = msg
	print(username+" posted in group "+gm)
	return create_json('grouppost', username, group, 'post-success')

def groupuser(username, group, data):
	gu = group
	if username in GROUP_USERS[gu]:
		message = GROUP_USERS[gu]
	else:
		message = 'user-not-in-group'
	return create_json('groupuser', username, group, message)

def handle_error(num):
	# 0 for wrong opt and group
	if num == 0:
		error_msg = 'Cmd-and-group-mismatch'
		message = create_json('error', '', '', error_msg)
	# 1 for wrong opt
	elif num == 1:
		error_msg = 'Cmd-invalid'
		message = create_json('error', '', '', error_msg)
	# 2 for wrong group
	elif num == 2:
		error_msg = 'Group-invalid'
		message = create_json('error', '', '', error_msg)
	return message

def handle_user(user_conn, user_addr):
	# handling function per user
	user_thread = True
	while user_thread:
		user_message_l = []
		user_message = user_conn.recv(1024)
		# print(user_message)
		user_message_l = convert_json(data=user_message)
		# print(user_message_l)
		opt = user_message_l["Type"]
		username = user_message_l["Username"]
		grp = user_message_l["Group"]
		data = user_message_l["Data"]

		# if opt == "connect":
		# # connect
		# connect(user_conn, user_addr)

		#handle error
		if ((opt == "exit")|(opt == "message")|(opt == "users")|(opt == "groups")|(opt == "leave")|(opt == "join")|(opt == "post"))&(grp!=''):
			user_conn.send(handle_error(0)).encode()
		elif ((opt == "group_message")|(opt == "group_user")|(opt == "group_post")|(opt == "group_leave")|(opt == "group_join"))&(grp==''):
			user_conn.send(handle_error(0)).encode()
		elif (grp != '') and (grp not in GROUPS):
			user_conn.send(handle_error(2).encode())

		# exit
		elif opt == "exit":
			user_thread = False
			break

		# join
		elif opt == "join":
			user_conn.send(join(username).encode())

		# leave
		elif opt == "leave":
			user_conn.send(leave(username).encode())
			user_thread = False
			break

		# users request
		elif opt == "users":
			user_conn.send(users(username).encode())

		# post
		elif opt == "post":
			user_conn.send(post(username, data).encode())

		# message
		elif opt == "message":
			user_conn.send(message(username, data).encode())

		# group
		elif opt == "groups":
			user_conn.send(groups(username).encode())

		# join group
		elif opt == "group_join":
			user_conn.send(groupjoin(username, grp).encode())

		# leave group
		elif opt == "group_leave":
			user_conn.send(groupleave(username, grp).encode())

		# group message
		elif opt == "group_message":
			user_conn.send(groupmessage(username, grp).encode())

		# group user
		elif opt == "group_user":
			user_conn.send(groupuser(username, grp).encode())

		# group post
		elif opt == "group_post":
			user_conn.send(grouppost(username, grp, data).encode())

		else:
			user_conn.send(handle_error(1).encode())

	print("User disconnected:", user_addr)
	user_conn.close()

HOST = "10.10.28.110"
PORT = 12345

if __name__ == "__main__":
	CONNECTIONS = []
	try:
		# Using IPv4 and TCP protocols
		server = socket.socket()
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print("Socket created: "+HOST+"-Port: "+str(PORT))
		print("Press Ctrl+C to stop.")
	except socket.error as error:
		print("Socket creation failed with error %s" %(error))
		sys.exit()

	server.bind((HOST, PORT))
	server.listen(1)

	try:
		while True:
			user_conn, user_addr = server.accept()

			print("New request from %s" %(str(user_addr)))
			t = threading.Thread(target=handle_user, args=(user_conn, user_addr))
			t.start()
			CONNECTIONS.append(t)

	except KeyboardInterrupt:
		print("\nCtrl+C pressed...")
	except Exception as err:
		print("Exception: %s"%err)

	print("Shutting down.")
	server.close()
	for connection in CONNECTIONS:
		connection.join()
