A message board application

/**********REQUIREMENTS*********/
Both server.py and client.py should run using python 3.x

/**********INSTRUCTIONS*********/
!!! Before starting both programs, remember to adjust the server IP to your local host IP (unable to assign static IP)!!!
On start will be prompted to enter IP address and port number to connect to server
Once connected will be given a list of possible commands to enter and execute
Commands must be entered as shown in the terminal to execute properly
Only allow a certain amount of commands at each iteration (if user is not connected, they cannot join, etc.)
When prompted for which group must enter answer with the following format "Group #"

Functions:
help        Return the help menu
connect         Command to connect to the server
exit            Command to exit the server
join            Command to join the message board
leave           Command to leave the message board
post            Command to post in the message board
message         Command to retrieve message in the message board
users           Command to retrieve list of users in the message board
groups          Command to retrieve list of available groups in the message board
group_join      Command to join a group
group_leave     Command to leave a group
group_post      Command to post in a group
group_message   Command to retrieve message in a group
group_users     Command to retrieve list of users in a group

/**********ASSUMPTIONS**********/
Assuming there are only 5 groups each named "Group #"
Assuming user can join multiple groups so for each group command the group has to be specified
Assuming everytime a client exit the server, the server will not memorize the username
Assuming the user have to leave all the groups if decides to leave the main group.
Assuming username will stay the same once you join the server
Assuming message IDS will be strictly numerical

/**********ISSUES**********/
1. Once the user leave the message board, they cannot join the message board again (UNRESOLVED)
2. If the user leave without group_leave, their user name may still be saved under other groups. (RESOLVED: once they leave they will automatically leave all the groups)
3. The user might input command that is impossible to execute (joining a group without connecting). (UNRESOLVED, need to modify the code for error catching)
4. After 'join' the user could not see the 2 most recent messages (RESOLVED, need to modify for posting and group_join as well)