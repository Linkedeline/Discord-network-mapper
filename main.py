from time import sleep
import os
import json
import sqlite3
import requests
Discord_token = "You're token"
Discord_ID = "you're ID"
HEADERS = {"authorization": Discord_token, "content-type": "application/json"}
def download_image(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully and saved as {save_path}")
    else:
        print("Failed to download image.")
def make_my_profile(user,relation):
    name = user['user']['username']
    theID = user['user']['id']
    avatar = user['user']['avatar']
    img = f"https://cdn.discordapp.com/avatars/{theID}/{avatar}.png?size=4096"
    download_image(img,name+'.png')
    print(name)
    print(relation)
    d = ''
    for i in user['mutual_guilds']: d = d + f"{i['id']} "
    c = ''
    for i in relation: c = c + f"[[{i['user']['username']}]] "
    filename = f"{name}.md"
    line = '---\n' + \
    f"tags: {d}\n" + \
    f"alias: {user['user']['id']} {user['user']['username']}\n" + \
    '---\n' + \
    f"# {user['user']['username']}\n" + \
    f"## Previvously known as: {user['legacy_username']}\n" + \
    "## bio\n" + \
    f"> {user['user_profile']['bio']}\n" + \
    "# Common friends\n" + \
    f"{c}\n" + \
    f"![[{name}.png]]"
    
    return [filename, line]
def make_profile(user,relation):
    name = user['user']['username']
    avatar = user['user']['avatar']
    theID = user['user']['id']
    img = f"https://cdn.discordapp.com/avatars/{theID}/{avatar}.png?size=4096"
    download_image(img,name+'.png')
    print(name)
    add_DB(theID,name)
   
    d = ''
    for i in user['mutual_guilds']: d = d + f"{i['id']} "
    c = ''
    for i in relation: c = c + f"[[{i['username']}]] "
    filename = f"{name}.md"
    line = '---\n' + \
    f"tags: {d}\n" + \
    f"alias: {user['user']['id']} {user['user']['username']}\n" + \
    '---\n' + \
    f"# {user['user']['username']}\n" + \
    f"## Previously known as: {user['legacy_username']}\n" + \
    "## bio\n" + \
    f"> {user['user_profile']['bio']}\n" + \
    "# Common friends\n" + \
    f"{c}\n" + \
    f"![[{name}.png]]"
    return [filename, line]
def create_and_write_file(file_name,line):
    # Get the current file path
    current_file_path = os.path.abspath('./')
    # Extract the directory path
    directory = os.path.dirname(current_file_path)
    try:
        # Open the file in write mode
        with open(file_name, 'w') as file:
            file.write(line)
        print(f"File created with name {file_name} written successfully.")
    except IOError:
        print("An error occurred while creating or writing to the file.")
        # Usage example

def add_DB(userID, username):
    con = sqlite3.connect('user.db')
    c = con.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users  (id  TEXT PRIMARY KEY, username TEXT)''')
    c.execute("INSERT OR REPLACE INTO users (id, username) VALUES (?,?)", (userID, username))
    con.commit()
    con.close()
   
    
def check_user(user_id):
    con = sqlite3.connect('user.db')
    c = con.cursor()
    c.execute("SELECT EXISTS(SELECT 1 FROM users WHERE id = ?)", (user_id,))
    result = c.fetchone()[0]
    exists = True if result == 1 else False
    con.close()
    return exists

url0 = "https://discord.com/api/users/@me/relationships"
friends = requests.get(url0, headers=HEADERS)
urlme = f"https://discord.com/api/users/{Discord_ID}/profile"
profile = requests.get(urlme, headers=HEADERS)
print (profile)
meinfo = make_my_profile(profile.json(), friends.json())
create_and_write_file(meinfo[0],meinfo[1])
total = len([ 'i' for friends in friends.json()])
passing, failling, skipped = 0, 0 ,0 
for i in friends.json():
    ID =str(i['user']['id'])
    url1 = f"https://discord.com/api/users/{ID}/profile" 
    url2 = f"https://discord.com/api/users/{ID}/relationships" 
    friend = requests.get(url1, headers=HEADERS)
    relation = requests.get(url2, headers=HEADERS)
    try:
    #print(friend)
        
        if not (check_user(ID)):
            info = make_profile(friend.json(), relation.json())
            create_and_write_file(info[0],info[1])
            passing += 1
            sleep(1)
        else:
            skipped += 1
            print("user exist and skipped")
    except Exception as e: 
        print(e)
        failling += 1
    os.system('clear')
    print(f"loading... \nPassing: {passing}\nfailed: {failling}\nskipped: {skipped}\n{passing+skipped+failling}/{total} ")
