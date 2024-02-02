import psutil
import os
from palworld_rcon.main import PalworldRcon
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify
from flask import request

app = Flask(__name__)

rcon: PalworldRcon = None

load_dotenv()
server_ip = str(os.getenv('server'))
rcon_port = int(os.getenv('rcon_port'))
rcon_pass = str(os.getenv('rcon_pass'))
ban_list = str(os.getenv('ban_list_path'))

def get_rcon() -> PalworldRcon:
    ## Sets up the RCON connection
    return PalworldRcon(server_ip, rcon_port, rcon_pass)

def run_command(command, args=[]):
    ## generic function for running rcon commands.  Cleans up repeated code.
    rcon = get_rcon()
    return rcon.run_command(command, args)

def showplayers() -> list:
    ## Grabs a list of players online.
    return [line.split(',') for line in run_command("ShowPlayers").split()][1:]

def showplayercount() -> int:
    ## Shows player count from online player list
    return len(showplayers())

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

@app.route("/")
def home():
    ## Homepage for Monitor 
    return render_template('home.html', showplayers=showplayers(), player_count=showplayercount())

@app.route("/getdata")
def get_data():
    ## Data that is refreshed every sec to homepage
    data = {
        'showplayers':showplayers(), 
        'bannedplayers':get_ban_list(),
        'ram':get_ram(),
        'cpu':get_cpu(),
        'player_count': showplayercount(),
        }
    message = {
            'status' : 200,
            'message' : 'OK',
            'data' : data
            }
    resp = jsonify(message)
    return resp

@app.route('/sendbroadcast', methods=['POST'])
def post_message():
    ## HTTP method to grab broadcast message
    return send_broadcast(request.form.get('message').replace(' ','_'))

@app.route("/saveserver")
def push_save():
    ## HTTP method to save world
    return save_world()

@app.route("/shutdown")
def push_shutdown():
    ## HTTP method to shutdown/restart server
    return shutdown()

@app.route('/kickplayer', methods=['POST'])
def kick_player():
    ## HTTP method to kick player
    return kickplayer(request.form.get('id'))

@app.route('/banplayer', methods=['POST'])
def ban_player():
    ## HTTP method to ban player
    return banplayer(request.form.get('id'))

@app.route('/unbanplayer', methods=['POST'])
def unban_player():
    ## HTTP method to unban player
    return unbanplayer(request.form.get('id'))