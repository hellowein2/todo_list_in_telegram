from datetime import datetime


# convert creating time to minutes have passed
### this is a crooked method ###
old_time = datetime.strptime('2024.05.08 00:34', "%Y.%m.%d %H:%M")
now = datetime.now()
time_ago = now - old_time
view_time_ago = str(time_ago)
view_time_passed = view_time_ago[2:4]
