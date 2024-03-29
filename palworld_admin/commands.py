from dotenv import load_dotenv
from palworld_rcon.main import PalworldRcon
from datetime import datetime as dt
import sqlite3
import psutil
import os

rcon: PalworldRcon = None

con = sqlite3.connect("ded_server.db")
cur = con.cursor()
cur.execute("CREATE TABLE if not exists players(name TEXT UNIQUE, playerid INTEGER PRIMARY KEY, steamid INTEGER UNIQUE, time)")

load_dotenv()
server_ip = str(os.getenv('server'))
rcon_port = int(os.getenv('rcon_port'))
rcon_pass = str(os.getenv('rcon_pass'))
ban_list = str(os.getenv('ban_list_path'))

def save_to_db():
    players = [line.split(',') for line in run_command("ShowPlayers").split('\n') if len(line.split(',')) == 3][1:]
    [_.append(str(dt.now().strftime('%Y-%m-%dT%H:%M:%SZ'))) for _ in players]
    cur.executemany("REPLACE INTO players VALUES(?,?,?,?)", players)
    con.commit()
    return players

def getplayerlist():
    save_to_db()
    cur.execute("Select * from players order by time desc, name desc")
    return cur.fetchall() 

def get_rcon() -> PalworldRcon:
    ## Sets up the RCON connection
    return PalworldRcon(server_ip, rcon_port, rcon_pass)

def run_command(command, args=[]):
    ## generic function for running rcon commands.  Cleans up repeated code.
    rcon = get_rcon()
    return rcon.run_command(command, args)

def showonlineplayers() -> list:
    ## Grabs a list of players online.
    return [_[0] for _ in save_to_db()]
    
def showplayercount() -> int:
    ## Shows player count from online player list
    return len(showonlineplayers())

def get_ram():
    ## Gets Ram metrics from server
    ram = psutil.virtual_memory()
    return {
        'total': round(ram.total / 1024 / 1024 / 1024, 2),
        'used': round(ram.used / 1024 / 1024 / 1024, 2),
        'percent': ram.percent
    }

def get_cpu() -> float:
    ## Gets CPU metrics from server.  If in a container this may show you the HOST values and not just the server.
    return {
        'cores': psutil.cpu_count(),
        'percent': psutil.cpu_percent()
    }

def get_ban_list():
    ## Creates a list of banned players
    if (os.path.isfile(ban_list)):
        with open(ban_list, 'r') as file:
            try:
                ban_users_list = [user.strip() for user in file.readlines() if user != '\n']
            except:
                print("Error in banlist file.")
                ban_users_list = []
    else:
        print("Issue with banlist File.", ban_list)
        ban_users_list = []
    return ban_users_list

def unbanplayer(userid):
    ## Modified banned list with unbanned player removed
    users = get_ban_list()
    for user in users:
        if userid in user:
            users.remove(user)
    with open(ban_list, 'w') as file:
        file.write('\n'.join(users))
    return users

def kickplayer(id):
    ## Kicks player from dedicated server
    return run_command("KickPlayer", [id])

def banplayer(id):
    ## Bans player from dedicated server
    return run_command("BanPlayer", [id])

def save_world():
    ## Saves Dedicated Server
    return run_command("Save")

def send_broadcast(message):
    ## Broadcasts message to dedicated server
    return run_command("Broadcast", [message])

def shutdown():
    ## Shutsdown or restarts dedicated server
    return run_command("Shutdown", ["30", "Server_will_shutdown_in_30_seconds."])
