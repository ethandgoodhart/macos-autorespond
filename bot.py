import numpy as np
import datetime
import sqlite3
import openai
import random
import time
import sys
import os

def formattedDate(d):
	n = (d / 1000000000) + 978289204
	time1 = time.gmtime(n)
	timestamp = [time.mktime(time1)]
	dt = [datetime.datetime.fromtimestamp(q) for q in timestamp]
	date = [(s.strftime('%Y-%m-%d %H:%M:%S')) for s in dt]
	return date[0]

def formattedDateObject(d):
	n = (d / 1000000000) + 978289204
	time1 = time.gmtime(n)
	return time.mktime(time1)

chatHistory = ""
u = os.popen('id -un').read().replace("\n", "")
db_location = "/Users/" + u + "/Library/Messages/chat.db"
connection = sqlite3.connect(db_location)
cursor = connection.cursor()

def sendMessage(message, sender):
	os.system('osascript sendMessage.applescript "' + sender + '" "' + message + '"')

def getResponse(message, chat_id):
	previous_conversation = cursor.execute("SELECT text, is_from_me, date FROM 'message' T1 INNER JOIN chat_message_join T2 ON T2.message_date = T1.date WHERE chat_id = "+str(chat_id)+" AND text NOT LIKE '%￼%' AND text NOT LIKE '%http%' OR '%.com%' OR '%\u200b%' AND text IS NOT NULL ORDER BY date ASC").fetchall()
	training_convo = ""

	for m in previous_conversation[:50]:
		if m[1] == 1:
			training_convo += "You: " + m[0] + "\n"
		else:
			training_convo += "Friend: " + m[0] + "\n"

	openai.api_key = sys.argv[1]

	response = openai.Completion.create(
		engine="davinci",
		prompt=training_convo.strip()+"\nFriend: "+message+"You:",
		temperature=0.4,
		max_tokens=60,
		top_p=1.0,
		frequency_penalty=0.5,
		presence_penalty=0.0,
		stop=["Friend:"]
	)

	return response.choices[0]['text'].strip()

start_date = datetime.datetime.strptime(str(datetime.datetime.now()).split(".")[0], '%Y-%m-%d %H:%M:%S')
print("Auto-Response Enabled\n")

while True:
	raw_result = cursor.execute("SELECT text, chat_identifier, date, T2.chat_id as date_utc FROM 'message' T1 INNER JOIN 'chat_handle_join' T2 INNER JOIN 'chat' T3 WHERE NOT is_from_me=1 AND T2.handle_id=T1.handle_id AND T3.ROWID=T2.chat_id AND chat_identifier NOT LIKE '%chat%' AND cache_roomnames IS NULL ORDER BY date DESC LIMIT 1").fetchone()
	formatted_date = formattedDate(raw_result[2])
	date_object = datetime.datetime.strptime(formatted_date, '%Y-%m-%d %H:%M:%S')

	if date_object > start_date:
		if len(cursor.execute("SELECT * FROM 'chat_handle_join' T1 INNER JOIN 'handle' T2 ON T2.id = '"+str(sys.argv[2])+"' AND T1.handle_id = T2.ROWID AND T1.chat_id = " + str(raw_result[3])).fetchall()) > 0:
			os.system('open "https://youtu.be/1-wb9ddKsDE"')
			start_date = date_object
		else:
			new_message_text = raw_result[0].strip()
			new_message_sender = raw_result[1]
			response = getResponse(new_message_text, raw_result[3])
			start_date = date_object
			sendMessage(response, new_message_sender)
			print("Responded to '"+new_message_text+"' with '"+response+"'")
