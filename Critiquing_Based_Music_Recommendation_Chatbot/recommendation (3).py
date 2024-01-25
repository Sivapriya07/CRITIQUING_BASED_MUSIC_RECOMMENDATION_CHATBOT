import base64
from requests import post, get
import json

client_id = "3c807945a2cc4df0bfc4d2143a091a27"
client_secret = "e558e47f4912400db3038a1c67e81a80"


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content_type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    result_json = json.loads(result.content)
    token = result_json["access_token"]
    return token


def get_auth_headers(token):
    headers = {"Authorization": "Bearer " + token}
    return headers


def get_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_headers(token)
    query = f"?q={artist_name}&type=artist&limit=1"
    query_url = url + query
    result = get(query_url, headers=headers)
    result_json = json.loads(result.content)["artists"]["items"]
    if len(result_json) == 0:
        return None
    return result_json[0]


def get_artist_tracks(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=IN"
    headers = get_auth_headers(token)
    result = get(url, headers=headers)
    result_json = json.loads(result.content)["tracks"]
    return result_json


def recommend_by_artist(token,artist_seed, song_seed):
    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_headers(token)
    params = {
        "seed_artist": artist_seed,
        "seed_tracks": song_seed,
        "market": "IN",
        "limit": 5
    }
    result = get(url, headers=headers, params=params)
    result_json = json.loads(result.content)["tracks"]
    return result_json

def recommend_by_songs(token, song_seed):
    url = "https://api.spotify.com/v1/recommendations"
    headers = get_auth_headers(token)
    params = {
        "seed_tracks": song_seed,
        "market": "IN",
        "limit": 5
    }
    result = get(url, headers=headers, params=params)
    result_json = json.loads(result.content)["tracks"]
    return result_json

def get_track(token,track_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_headers(token)
    query = f"?q={track_name}&type=track&market=IN&limit=1"
    query_url = url + query
    response = get(query_url, headers=headers)
    response_json = json.loads(response.content)['tracks']['items']
    if len(response_json) == 0:
        return None
    return response_json[0]

def empty_URL(preview_url):
    if preview_url is not None:
        return cprint(preview_url, "blue")
    else:
        return cprint("There is no music preview available for this song.", "blue")


################################################################CHATBOT###############################################################################
import re
import random
from termcolor import colored, cprint

greetings = ['Hello!', 'Hi there!', 'Hey!', 'Greetings!', 'Nice to see you!']

artist_vs_song_question = ["Are you looking for music recommendations based on a certain artist or song?",
            "Would you like me to suggest some music based on an artist or song you like?",
            "Do you want me to recommend music based on a particular artist or song?",
            "Are you interested in discovering new music based on an artist or song you enjoy?",
            "Can I provide you with music recommendations based on a specific artist or song?",
            "Do you want me to suggest some songs or artists based on your preferences?",
            "Are you open to getting music suggestions based on an artist or song you like?",
            "Would you like me to curate a playlist based on an artist or song that you enjoy?",
            "Can I offer you some music recommendations based on a favorite artist or song?",
            "Are you interested in exploring new music based on an artist or song you're familiar with?"]

artist_question = ["Please provide the name of the artist:",
                   "What is the name of the artist you would like to search?",
                   "Type in the artist's name:",
                   "Enter the name of the artist you're interested in:",
                   "What is the name of the artist you want to look up?",
                   "Please input the artist's name:",
                   "Who is the artist you'd like to find?",
                   "What's the name of the artist you're searching for?",
                   "Type the name of the artist you want to find:",
                   "Please provide the artist's name to begin the search:"]

songlist_question = ["Which song did you enjoy the most? Please enter it below (1-10):",
                 "Input the title of the song you liked the most (1-10):",
                 "Please type in the name of the song you enjoyed the most (1-10):",
                 "Enter the title of the song that you liked the most (1-10):",
                 "What is the name of the song that you enjoyed the most (1-10)?",
                 "Please provide the title of the song you liked the most (1-10):",
                 "Which song stood out to you the most? Please enter it below (1-10):",
                 "Type the title of the song you enjoyed the most (1-10):",
                 "Can you tell me the name of the song that you liked the most (1-10)?",
                 "Which song was your favorite? Please enter the title (1-10):"]

feedback_question = ["Would you say you enjoyed the song? (Yes/No/Stop)",
                     "Did the song appeal to you? (Yes/No/Stop)",
                     "Are you liking the song? (Yes/No/Stop)",
                     "Do you find the song enjoyable? (Yes/No/Stop)",
                     "Would you like to hear more music like this? (Yes/No/Stop)",
                     "Was the song to your liking? (Yes/No/Stop)",
                     "Do you want to continue listening to the song? (Yes/No/Stop)",
                     "Is the song to your taste? (Yes/No/Stop)",
                     "Did you enjoy listening to the song? (Yes/No/Stop)",
                     "Are you interested in listening to more songs like this? (Yes/No/Stop)"]

song_question = ["What type of song do you feel like listening to based on your current mood?",
                 "Which genre of music suits your current mood?",
                 "What kind of music would you like to listen to right now, based on your mood?",
                 "Based on how you're feeling right now, what type of song would you like to hear?",
                 "Can you describe your mood so I can suggest a suitable song?",
                 "Tell me about your mood and I'll recommend a song that fits.",
                 "Depending on your mood, what genre of music would you like to listen to?",
                 "Which type of music would you prefer to listen to right now, given your mood?",
                 "Let me know your current mood, and I'll suggest a song that fits the bill.",
                 "What kind of music would you like to hear that would complement your current mood?"]

goodbyes = ['Goodbye!', 'See you later!', 'Bye!', 'Nice chatting with you!', 'Take care!']

def get_greeting():
    return random.choice(greetings)

def artist_vs_song_query():
    return random.choice(artist_vs_song_question)

def artist_query():
    return random.choice(artist_question)

def song_list_query():
    return random.choice(songlist_question)

def song_query():
    return random.choice(song_question)

def feedback_query():
    return random.choice(feedback_question)

def get_goodbye():
    return random.choice(goodbyes)

cprint("\n" + get_greeting() + "\n","yellow")

stop_flag = True

decision = input(colored(artist_vs_song_query() + "\n", "light_green")).strip()

artist_pattern = re.compile(r'^\s*(art(?:i|is|ist|ists)?\w*)\s*[^\w\s]*\s*$', re.IGNORECASE)
song_pattern = re.compile(r'^\s*(son(?:g|gs|gg)?)\s*[^\w\s]*\s*$', re.IGNORECASE)

while not (artist_pattern.match(decision) or song_pattern.match(decision)):
    print("Invalid input. Please enter either 'artist' or 'song'." + "\n")
    decision = input(colored(artist_vs_song_query() + "\n", "light_green")).strip()

token = get_token()
if artist_pattern.match(decision):
    while True:
        artist_name = input(colored("\n" + artist_query() + "\n", "light_green"))
        search_artist = get_artist(token, artist_name)
        if search_artist:
            artist = search_artist["name"]
            cprint("\n" + artist + "\n", "cyan")
            confirm_artist = input(colored("Is this the artist you are looking for? (Yes/No)\n", "light_green")).strip()
            if confirm_artist.lower() == "yes":
                artist_id = search_artist["id"]
                artist_tracks = get_artist_tracks(token, artist_id)
                cprint("\n" + f"These are all the {artist}'s top tracks:" + "\n", "cyan")
                for idx, song in enumerate(artist_tracks):
                    cprint(f"{idx + 1}. {song['name']}", "yellow")
                break
            elif confirm_artist.lower() == "no":
                cprint("\nPlease provide the appropriate artist name.", "red")
        else:
            cprint("\n" + "Artist not found. Please try again.", "red")
    
    while True:
        try:
            asking_song = int(input(colored("\n" + song_list_query(), "light_green")))
            if 1 <= asking_song <= 10:
                break
            else:
                cprint("Please enter a number between 1 and 10.", "red")
        except ValueError:
            cprint("Invalid input. Please enter a number between 1 and 10.", "red")

    select_song = artist_tracks[asking_song - 1]
    song_id = select_song["id"]
    cprint("\nHere is the song that you chosen", "cyan")
    cprint("\n" + select_song['name'], "yellow")
    empty_URL(select_song['preview_url'])
    recommended_list = recommend_by_artist(token, artist_id, song_id)
    cprint("\nHere's a diverse song that you might enjoy and that showcases a range of musical styles within this category.","light_green")
    recommend_song_name = recommended_list[0]['name']
    recommend_song_url = recommended_list[0]['preview_url']
    latest_recommend_song_id = recommended_list[0]['id']
    cprint("\n" + recommend_song_name,"yellow")
    empty_URL(recommend_song_url)
    
    while True:
        
        feedback = input(colored("\n" + feedback_query() + "\n", "light_green")).strip()
        
        if feedback.lower() == 'stop':
            cprint("\n" +  get_goodbye(), "light_green")
            break
        
        elif feedback.lower() == 'yes':
            seed_song = recommend_by_artist(token, artist_id, latest_recommend_song_id);
            song_name = seed_song[0]['name']
            song_preview = seed_song[0]['preview_url']
            cprint("\n" + song_name,"yellow")
            empty_URL(song_preview)
            
        elif feedback.lower() == 'no':
            next_song = 0
            next_song += 1
            recommended_list_song = recommend_by_artist(token, artist_id, song_id)[next_song]
            song_name = recommended_list_song['name']
            song_preview = recommended_list_song['preview_url']
            cprint("\n" + song_name,"yellow")
            empty_URL(song_preview)

        else:
            cprint("\n" + "Sorry, I didn't understand that. Please choose 'yes', 'no', or 'stop'."  + "\n", "red")



elif song_pattern.match(decision):
    
    while stop_flag :
        user_song = input(colored("\n" + song_query() + "\n", "light_green"))
        song_recommend = get_track(token, user_song)
        
        if song_recommend is None:
            cprint("\nSorry, I couldn't find a song matching that name. Please try again.\n", "red")
            continue
        else:
            song_id = song_recommend["id"]
            cprint("\nHere is the song that you chosen", "cyan")
            cprint("\n" + song_recommend['name'], "yellow")
            empty_URL(song_recommend['preview_url'])
            recommended_list = recommend_by_songs(token, song_id)
            cprint("\nHere's a diverse song that you might enjoy and that showcases a range of musical styles within this category.","light_green")
            latest_recommend_song_id = recommended_list[0]['id']
            cprint("\n" + recommended_list[0]['name'], "yellow")
            empty_URL(recommended_list[0]['preview_url'])
        
            while True:
                
                feedback = input(colored("\n" + feedback_query() + "\n", "light_green")).strip()
                
                if feedback.lower() == 'stop':
                    stop_flag = False
                    cprint("\n" +  get_goodbye(), "light_green")
                    break
                
                elif feedback.lower() == 'yes':
                    seed_song = recommend_by_songs(token, latest_recommend_song_id);
                    song_name = seed_song[0]['name']
                    song_preview = seed_song[0]['preview_url']
                    cprint("\n" + song_name,"yellow")
                    empty_URL(song_preview)
                    
                elif feedback.lower() == 'no':
                    next_song = 0
                    next_song += 1
                    recommended_list_song = recommend_by_songs(token, song_id)[next_song]
                    song_name = recommended_list_song['name']
                    song_preview = recommended_list_song['preview_url']
                    cprint("\n" + song_name,"yellow")
                    empty_URL(song_preview)
                
                else:
                    cprint("Sorry, I didn't understand that. Please choose 'yes', 'no', or 'stop'.", "red")
                    