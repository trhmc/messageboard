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
	global USERS, MESSAGES
	# checking if a username is taken or not
	if username in USERS:
		message = create_json('join', username, '', 'Username-taken')
	else:
		USERS.append(username)
		print("Added "+username+" to list of users")
		# adding the last two message to send back to client
		message_id = len(MESSAGES)
		if message_id > 1:
			msg_board = MESSAGES[message_id-2]+'\n\r'+MESSAGES[message_id-1]
		elif message_id == 1:
			msg_board = MESSAGES[message_id-1]
		elif message_id == 0:
			msg_board = ''
		message = create_json('join', username, '', 'Username-accept'+'\n\r'+msg_board)
	return message

def leave(username):
	global USERS
	USERS = [user for user in USERS if user != username]
	print(username+" has left the building.")
	message = create_json('leave', username, '', 'Username-removed')
	return message

def post(username, data):
	global MESSAGES
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
	global USERS
	# may think of different way to represent data
	message = create_json('users', username, '', USERS)
	print(username+" retrieved list of users")
	return message

def message(username, data):
	global MESSAGES
	message_id = int(data)
	if message_id in MESSAGES:
		msg = 'Message-retreived:\n'+MESSAGES[message_id]
	else:
		return create_json('message', username, '', 'ID invalid')
	print(username+' retrieve message #'+data)
	return create_json('message', username, '', msg)

def in_group(username, group):
	if username not in GROUP_USERS[group]:
		return False
	return True

def groups(username):
	global GROUP_USERS, GROUPS
	g = []
	for group in GROUPS:
		if not(in_group(username, group)):
			g.append(group)
	msg = 'Groups available to join:\n'
	for grp in g:
		msg = msg + grp + '\t'
	message = create_json('groups', username, '', msg)
	return message

def groupjoin(username, group):
	global GROUP_USERS
	gtj = group
	# join if user not in group, send error if user already in group
	if not(in_group(username, gtj)):
		GROUP_USERS[gtj].append(username)
		message = create_json('group_join', username, group, gtj+'-successfully-joined')
		print(username+" joined group "+gtj)
	else:
		message = create_json('group_join', username, group, gtj+'-already-joined')
	return message


def groupleave(username, group):
	global GROUP_USERS
	gtl = group
	if (in_group(username, gtl)):
		GROUP_USERS[gtl] = [u for u in GROUP_USERS[gtl] if u != username]
		message = create_json('group_leave', username, group, gtl+'-successfully-left')
	else:
		message = create_json('group_leave', username, group, 'not-in-'+gtl)
	print(username+" left group "+gtl)
	return message

def groupmessage(username, group, data):
	global GROUP_USERS, GROUP_MESSAGES
	gm = group
	msg_id = data
	if (in_group(username, gm)):
		if msg_id not in GROUP_MESSAGES[gm].keys():
			message = create_json('group_message', username, group, 'Group message ID invalid')
		else:
			print(username+" found msg[" + msg_id+ "] " "in "+gm)
			message = create_json('group_message', username, group, gm+'-message-id-'+msg_id+'\n\r'+GROUP_MESSAGES[gm][data])
	else:
		message = create_json('group_message', username, group, 'user-not-in-group')
	return message

def grouppost(username, group, data):
	# checking if user in group to post
	global GROUP_MESSAGES
	if not(in_group(username, group)):
		server_message = create_json('group_post', username, group, 'user-not-in-group')
	else:
		gm = group
		message_id = str(len(GROUP_MESSAGES[gm]))
		sender = username
		message = data
		post_date = str(date.today())
		msg = sender+"\n\r"+post_date+"\n\r"+message
		GROUP_MESSAGES[gm][message_id] = msg
		print(username+" posted in group "+gm)
		print("Current "+gm+" message num: "+str(len(GROUP_MESSAGES[gm])))
		# print(str(GROUP_MESSAGES[gm]))
		server_message = create_json('group_post', username, group, 'post-success')
	return server_message

def groupuser(username, group):
	global GROUP_USERS
	gu = group
	if in_group(username, group):
		message = GROUP_USERS[gu]
	else:
		message = 'user-not-in-group'
	return create_json('group_users', username, group, message)

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
			user_conn.send(handle_error(0).encode())
		elif ((opt == "group_message")|(opt == "group_users")|(opt == "group_post")|(opt == "group_leave")|(opt == "group_join"))&(grp==''):
			user_conn.send(handle_error(0).encode())
		elif (grp != '') and (grp not in GROUPS):
			user_conn.send(handle_error(2).encode())

		# exit
		elif opt == "exit":
			user_conn.send(leave(username).encode())
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
			user_conn.send(groupmessage(username, grp, data).encode())

		# group user
		elif opt == "group_users":
			user_conn.send(groupuser(username, grp).encode())

		# group post
		elif opt == "group_post":
			user_conn.send(grouppost(username, grp, data).encode())

		else:
			user_conn.send(handle_error(1).encode())

	print("User disconnected:", user_addr)
	user_conn.close()

HOST = "192.168.86.26"
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
