import requests
import telegram_functions as tf
from bs4 import BeautifulSoup 
import csv
import json

omdb_base_url = "http://www.omdbapi.com/"
yts_base_url = "https://yts.mt/browse-movies/"
apikey = "your_omdb_api_key"

kb_buttons =[["hell yeah !!!"],["whatever bruh :("]]
kb_markup = {
    "keyboard" : kb_buttons,
    "one_time_keyboard" : True
}
reply_markup = json.dumps(kb_markup)

def omdb_call(chat_id,movie, year):
    """makes a omdb call"""
    omdb_response = requests.get(omdb_base_url, headers={"Accept":"application/json"}
        , params={"apikey":apikey,"t":{movie},"y":{year} , "plot":"full"})

    omdb_response = omdb_response.json()

    if omdb_response["Response"] == "True":
        omdb_name = omdb_response["Title"]
        omdb_release = omdb_response["Year"]
        omdb_rating = omdb_response["imdbRating"]
        omdb_search_list = {"omdb_name":omdb_name,"omdb_release":omdb_release,"omdb_rating":omdb_rating}
        movie_info_string =""
        try :
          image_response = (requests.get(omdb_response["Poster"])).content
          # with open(f"photos/{omdb_name}.jpeg", "wb") as image_object:
          #     image_object.write(image_response)
        except Exception :
          poster_message = "Sorry, can't find the poster for this movie\n\nInconvinience is regretted."
          tf.send_messages(chat_id, poster_message)
        else :
          tf.send_photos(chat_id,image_response)
          # tf.send_photos(chat_id,f"photos/{omdb_name}.jpeg")
        
        for key, value in omdb_response.items():
            if key not in ["Ratings", "Poster", "imdbID", "Website", "Response", "Type", "DVD", "Country"]:
                append_string = f"<b>{key}</b> : {value}\n\n"
                movie_info_string += append_string

        tf.send_messages(chat_id, movie_info_string)
        return omdb_search_list

    else:
        error_message = "Sorry, can't find the movie you've been looking for."
        tf.send_messages(chat_id, error_message)
        return None


     


def yts_scraping(chat_id,search_list):
    """scrapes the yts.mt site for torrents"""
    omdb_name = search_list["omdb_name"]
    omdb_rating = search_list["omdb_rating"]
    omdb_release = search_list["omdb_release"]

    yts_response = requests.post("https://yts.mt/search-movies", 
        data={"keyword":omdb_name,"quality":"all","genre":"all","rating":omdb_rating[0]
        ,"order_by":"downloads"})

    parsed_page = BeautifulSoup(yts_response.content, "html.parser")
    parsed_section = parsed_page.find("section")
    parsed_divs = parsed_section.div.find_all(class_="browse-movie-wrap")

    with open("movie_db.csv", "w", newline="") as f:
        header_writer = csv.writer(f)
        header_writer.writerow(["Title","Year","Link"])

    for each_div in parsed_divs:
        parsed_anchors = each_div.find("a",class_="browse-movie-title")
        movie_name = parsed_anchors.getText()
        movie_link_1 = parsed_anchors["href"]
        movie_year = (each_div.find("div",class_="browse-movie-year").getText())

        movie_data = [movie_name, movie_year, movie_link_1]
        with open("movie_db.csv", "a", newline="") as f_obj:
            csv_writer = csv.writer(f_obj)
            csv_writer.writerow(movie_data)

    with open("movie_db.csv", "r") as file:
        reader = csv.reader(file)
        next(reader)
        flag = False
        for each in reader:
            if each[0].lower() == omdb_name.lower() and each[1] == omdb_release:
                sub_yts_response = requests.get(each[2])
                sub_parsed_response = BeautifulSoup(sub_yts_response.text, "html.parser")
                sub_parsed_divs = sub_parsed_response.find("div", class_="main-content").find_all("div", id="movie-info")
                sub_parsed_anchors = sub_parsed_divs[0].find("p").find_all("a")
                torrent_list = []

                for each_link in sub_parsed_anchors:
                    movie_quality = each_link["title"]
                    torrent_link = each_link["href"]
                    torrent_dict = {"quality":movie_quality,"torrent":torrent_link}
                    torrent_list.append(torrent_dict)

                for each in torrent_list:

                    torrent_file = requests.get(each["torrent"])
                    file_path = each["quality"]
                    with open(f"torrents/{file_path}.torrent", "wb") as f:
                        f.write(torrent_file.content)
                    tf.send_documents(chat_id, f"torrents/{file_path}.torrent")

 
                confirmation_message = "Is this the movie you've been looking for ?"
                tf.send_messages(chat_id, confirmation_message, reply_markup=reply_markup)
                flag = True

        if not flag:
            tf.send_messages(chat_id,"Sorry, can't seem to find the movies torrent.\n\nInconvinience is regretted")