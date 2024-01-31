# PalWorld Server Monitor

<img width="956" alt="Screenshot 2024-01-30 202040" src="https://github.com/eternity336/PalworldServerMonitor/assets/7098793/cff57e31-750c-47bd-a71d-0b558b812900">

Intended as a monitor for your dedicated server.  This is not inheriently secure and I would not advise making this public facing.  However it will work great internally.  It was built with Python, HTML, JQuery and Javascript.  I also used the rcon code from some great work by gavinnn101 refenced below:

- https://github.com/gavinnn101/palworld_dedi_helper

Without it alot of this would not be possible.

Of note I am running everything on a Ubuntu server.  If you decide to run this on Windows you will have to deploy the process differently and I haven't tested it for that.  This is built for linux.  This should still run on windows though if you are so inclided to go through the process.

---

Currently this allows you to:
- Monitor Online Players
- See list of Banned Players
- Kick Players
- Ban Players
- Unban Players (Requires a server restart to take effect.)
- Send a broadcast message
- Restart/Shutdown server after 30 seconds with broadcast warning. (Restart dependent on how you set up the running process.)
- Save world
- Monitor RAM usage
- Monitor CPU usage [Currently this may appear off if you are using a container.  Cause in my environment I am getting the host details.]

---

You will need to create a file called 'config.yaml' and save it in the base folder.  It should look like the follwoing:
    
    server: 127.0.0.1
    rcon_port: 25575
    rcon_pass: 'password'
    ban_list_path: '/Pal/Saved/SaveGames/banlist.txt'

I deployed using gunicorn and developed this using the latest python3.11.
So make sure you have python3 install and install the requirements.txt using

    pip install -r requirements.txt

and then add the systed config /etc/systemd/system/palworldmonitor.service

    [Unit]
    Description=PalWorld Monitor Service
    After=network.target

    [Service]
    User=steam  <-- I have my user as steam but something that isn't root
    ExecStart=/bin/gunicorn -b 0.0.0.0 app:app  <-- Make sure this location is correct
    WorkingDirectory=/path/to/app/ <-- Working dorectory of app
    ExecReload=/bin/kill -s HUP $MAINPID
    KillMode=mixed
    TimeoutStopSec=5
    Restart=always

    [Install]
    WantedBy=multi-user.target

Once you set the config in place you enable and start it

    sudo systemctl enable palworldmonitor.service
    sudo systemctl start palworldmonitor.service

You can check the process status via

    sudo systemctl status palworldmonitor.service

And restart via

    sudo systemctl restart palworldmonitor.service

Then you can access the site with the http://< serverIP >:8000

If you want a different port then 8000 just add the port to the above config after 0.0.0.0 with :port

