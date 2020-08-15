import requests
import json
from datetime import datetime
from dateutil import tz
from os.path import exists


offset_file_name = "offset_tracker_data.json"
updates_file_name = "update_data.json"
base_url = "https://api.telegram.org/"
api_token = "your telegram bot api token"


def get_updates(offset, timeout=120):
    """function getting updates from the api"""
    request_url = f"{base_url}bot{api_token}/getUpdates"
    updates_response = requests.get(request_url, headers={"Accept":"application/json"},
        params={"offset":offset, "timeout":timeout})
    deserialized_json = time_changer(updates_response.json())
    return deserialized_json


def json_write(response_data):
    """writing json response_data to a new file"""
    with open(updates_file_name,"w") as file_object:
        json.dump(response_data, file_object, indent=4)


def json_update(response_data):
    """updating json response_data to as existing file"""
    with open(updates_file_name,"r+") as file_object:
        file_data = json.load(file_object)
        file_data["result"].extend(response_data["result"])
        file_object.seek(0) #i dont know what it does , maybe the pointer helps to read the data in the offset_updater function
        json.dump(file_data,file_object,indent=4)


def send_messages(chat_id, message, parse_mode="HTML", reply_markup = None):
    """sends messages to the chat_id when called upon"""
    post_url = f"https://api.telegram.org/bot{api_token}/sendMessage"
    post_response = requests.post(post_url, headers={"Accept":"application/json"},
        data={"chat_id":chat_id,"text":message,"parse_mode":parse_mode,
        "reply_markup":reply_markup})
    del post_response


def  send_documents(chat_id, document_path, reply_markup = None):
    """sends documents to the chat_id when called upon"""
    binary_read = open(document_path, "rb")
    post_url = f"https://api.telegram.org/bot{api_token}/sendDocument"
    post_response = requests.post(post_url, headers={"Accept":"application/json"},
        data={"chat_id":chat_id,"reply_markup":reply_markup},
        files={"document":binary_read})
    binary_read.close()
    del post_response


def send_photos(chat_id, binary_read):
    """sends photo to the chat_id when called upon"""
    # binary_read = open(photo_path, "rb")
    post_url = f"https://api.telegram.org/bot{api_token}/sendPhoto"
    post_response = requests.post(post_url, headers={"Accept":"application/json"},
        data={"chat_id":chat_id},files={"photo":binary_read})
    # binary_read.close()
    del post_response   


def time_converter(timestamp):
    """converts the unix timestamp into local time"""
    date = datetime.fromtimestamp(timestamp)
    t_zone = tz.gettz('India/Kolkata')#no need to hard code it but for security purpose
    central = date.astimezone(t_zone)
    return (central.strftime("%d-%m-%Y %H:%M"))


def time_changer(deserialized_json):
    """exchanges the date returned by time converter to the timestamp"""
    updated_json = deserialized_json
    for item in updated_json["result"]:
        timestamp = item["message"]["date"]
        item["message"]["date"] = time_converter(timestamp)

    return updated_json

def offset_updater():
    """updates the offset to the offset tracker file"""
    with open(updates_file_name) as file_object:
        file_data = json.load(file_object)
        result_list = file_data["result"]
        offset_id = result_list[-1] ["update_id"]
        offset = offset_id + 1
        offset_list = [offset]
        if not exists(offset_file_name):
            with open(offset_file_name,"w") as offset_object:
                json.dump(offset_list,offset_object)

        else:
            with open(offset_file_name, "r+") as offset_object:
                f_data = json.load(offset_object)
                f_data.extend(offset_list)
                offset_object.seek(0)
                json.dump(f_data,offset_object)


def offset_teller():
    """returns the last used update_id"""
    if not exists(offset_file_name):
        return None

    else:
        with open(offset_file_name,"r") as file_object:
            file_data = json.load(file_object)
            return file_data[-1]
