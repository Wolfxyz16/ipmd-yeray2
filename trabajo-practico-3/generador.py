import json
import numpy as np
from datetime import datetime
import time

json_file = 'data/tweets1.json'
gap = 5

with open(json_file, 'r') as file:
    tweets = json.load(file)
    while True:
        try:
            user = np.random.randint(len(tweets))
            tweet = np.random.randint(len(tweets[user]["tweets"]))
            now = datetime.now()
            formatted = now.strftime("%Y-%m-%d %H:%M:%S")
            text = tweets[user]["tweets"][tweet].encode('utf-8','ignore').decode("utf-8").replace('\n', ' ')
            text += "."
            text = text.replace('"', "")
            text = text.replace('\\', "")
            print('{"user_id":' + str(tweets[user]["id"]) + ',"tweet":"' + text + '", "timestamp":"' + formatted + '"}')
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        # Introduce a delay between insertions
        time.sleep(gap)
            
print("Exiting...")