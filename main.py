import telegram_functions as tf
import web_scraping_functions as ws
import os
import re
from datetime import datetime

def main():
    """main function runs all the sub functions of the bot"""
    offset = tf.offset_teller()
    updates_data = tf.get_updates(offset)
    if updates_data["result"]:
        updates_list = updates_data["result"]
        for each_update in updates_list:
            chat_id = each_update["message"]["chat"]["id"]
            first_name = each_update["message"]["from"]["first_name"]
            try:
                update_message = (each_update["message"]["text"]).lower()

            except KeyError:
                error_message = "Please, send a <strong>valid movie</strong> name"
                tf.send_messages(chat_id, error_message)

            else:
                if update_message == "/start" or update_message == "/help":
                    help_message_1 = f"Hello {first_name}!!!, I'm a bot designed to help you seach info and torrent about <i>Hollywood movies</i>."
                    help_message_2 = f"To search just enter the name of the movie.\n\n<b>Note: </b>Try to enter the full name of the movie as in the poster for best results and if you know the year of release enter it seperated by a comma(only use it to seperate movie from release year). \n\n example : spectral, 2016."
                    tf.send_messages(chat_id, help_message_1)
                    tf.send_messages(chat_id, help_message_2)

                elif update_message == "hell yeah !!!" or update_message =="whatever bruh :(":
                    if update_message == "hell yeah !!!":
                        success_message = "Enjoy the movie"
                        tf.send_messages(chat_id, success_message)

                    else:    
                        failure_message = "Sry, we will improve the process next time.\n\nInconvinience is regretted."
                        tf.send_messages(chat_id, failure_message)

                else:
                    pattern = re.compile(r"([\w\s':!\/\+\?~{}@#_-]+)\s*,?\s*(\d{4}$)?")
                    match = pattern.search(update_message)
                    movie_tuple = match.groups()
                    search_list = ws.omdb_call(chat_id, movie_tuple[0], movie_tuple[1])
                    if search_list:
                        ws.yts_scraping(chat_id, search_list)
                    





        is_exists = os.path.exists(tf.updates_file_name)

        if is_exists:
            tf.json_update(updates_data)
            tf.offset_updater()

        else:
            tf.json_write(updates_data)
            tf.offset_updater()


while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    time_list = ["00:00","04:00","08:00","12:00","16:00","20:00","24:00"]
    if current_time in time_list:
        os.remove(tf.updates_file_name)
        os.remove(tf.offset_file_name)
    main()