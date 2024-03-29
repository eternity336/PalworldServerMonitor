var interval_timer = "";

const removeZero = item => (
    Object
      .keys(item)
      .filter(key => item[key] !== 0)
      .reduce((newObj, key) => {
        newObj[key] = item[key];
        return newObj;
      }, {})
  );

function add_s(value){
    if (value == 1) {
        return ''
    }
    return 's'
}

function last_Online(online_date){
    var s = {                                                                  // structure
        year: 31536000,
        month: 2592000,
        week: 604800, // uncomment row to ignore
        day: 86400,   // feel free to add your own row
        hour: 3600,
        minute: 60,
        //second: 1
    };
    
    var d = Math.abs(online_date - Date.now())/1000;
    r = {}
    
    Object.keys(s).forEach(function(key){
        r[key] = Math.floor(d / s[key]);
        d -= r[key] * s[key];
    });
    
    return Object.entries(removeZero(r)).map(([key,value]) => `${value} ${key}${add_s(value)}`).join(" ")
}

function post_data(url, data){
    $.ajax({
        url: url,
        type: 'POST',
        data: data
    }).done(function(data){
        console.log(data);
        fade_message(data);
    });
}

function fade_message(message) {
    element = document.getElementById('messagebar');
    var op = 1;  // initial opacity
    element.innerHTML = message
    element.style.opacity = op;
    element.style.display = 'block';
    setTimeout(10000);
    var timer = setInterval(function () {
        if (op <= 0.1){
            clearInterval(timer);
            element.style.display = 'none';
        }
        element.style.opacity = op;
        element.style.filter = 'alpha(opacity=' + op * 100 + ")";
        op -= op * 0.1;
    }, 300);
}

function delTable(name){
    $(`#${name}`).empty();
}

function send_broadcast(){
    post_data("/sendbroadcast", {'message': $('#broadcast_msg').val()})
    $('#broadcast_msg').val('');
}

function save_world(){
    $.ajax({
        url: "/saveserver",
        type: "GET"
    }).done(function(data){
        console.log(data);
        fade_message(data);
    })
}

function shutdown(){
    $.ajax({
        url: "/shutdown",
        type: "GET"
    }).done(function(data){
        console.log(data);
        fade_message(data);
    })
}

function set_playercount(count){
    if(count == 1){
        message = "Currently there is 1 player online."
    }else{
        message = "Currently there are " + count + " players online."
    }
    $('#playercount').text(message);
}

function kickplayer(id){
    post_data("/kickplayer", {'id': id})
}

function banplayer(id){
    post_data("/banplayer", {'id': id})
}

function unbanplayer(id){
    post_data("/unbanplayer", {'id': id})
}

function create_player_row(player, online){
    var playertable = document.getElementById('showplayers');
    var row = playertable.insertRow(-1);
    var namecell = row.insertCell(0);
    var playerid = row.insertCell(1);
    var steamid = row.insertCell(2);
    var datetime = row.insertCell(3);
    var kick = row.insertCell(4);
    var ban = row.insertCell(5);
    namecell.innerHTML = player[0];
    playerid.innerHTML = player[1];
    steamid.innerHTML = player[2];
    console.log("TEST", player[0], online)
    if(online.includes(player[0])){
        var datetime_icon = `<img class="online_status" src="static/images/online.png" alt="online"/> ${last_Online(new Date(player[3]))}`
    }else{
        var datetime_icon = `<img class="online_status" src="static/images/offline.png" alt="offline"/> ${last_Online(new Date(player[3]))}`
    }
    datetime.innerHTML = datetime_icon;
    const kickbutton = document.createElement('button');
    kickbutton.textContent = 'Kick';
    kickbutton.id = steamid.innerHTML;
    kickbutton.onclick = function() {
        kickplayer(steamid.innerHTML);
    };
    kick.appendChild(kickbutton);
    const banbutton = document.createElement('button');
    banbutton.textContent = 'Ban';
    banbutton.id = steamid.innerHTML;
    banbutton.onclick = function() {
        banplayer(steamid.innerHTML);
    };
    ban.appendChild(banbutton);
}

function create_unban_row(playerid){
    var bannedtable = document.getElementById('bannedplayers');
    var row = bannedtable.insertRow(-1);
    var player = row.insertCell(0);
    var unban_btn = row.insertCell(1);
    player.innerHTML = playerid;
    const unbanbutton = document.createElement('button');
    unbanbutton.textContent = 'Unban';
    unbanbutton.id = playerid;
    unbanbutton.onclick = function() {
        unbanplayer(playerid);
    };
    unban_btn.appendChild(unbanbutton);
}

function addPlayers(players, online){
    console.log('online', players, online)
    for (let i = 0; i < players.length; i++){
        create_player_row(players[i], online)
    }
}

function addBannedPlayers(players){
    console.log('banned', players)
    for (let i = 0; i < players.length; i++){
        create_unban_row(players[i])
    }

}

function refreshData(){
    var ramtitle = document.getElementById('ram_title');
    var rambar = document.getElementById('myRamBar');
    var ramtext = document.getElementById('myRamPerc');
    var cputitle = document.getElementById('cpu_title');
    var cpubar = document.getElementById('myCPUBar');
    var cputext = document.getElementById('myCPUPerc');
    $.ajax({
                url: "/getdata",
                type: 'GET'
            }).done(function(data){
                console.log(data);
                ramused = data.data.ram.used
                ramtotal = data.data.ram.total
                ramtitle.innerHTML = `RAM [ ${ramused}GB / ${ramtotal}GB ]`
                rambar.style.width = `${data.data.ram.percent}%`;
                ramtext.innerHTML = `${data.data.ram.percent}%`;
                cpucores = data.data.cpu.cores;
                cpuperc = data.data.cpu.percent;
                cputitle.innerHTML = `CPU [${cpucores} CORES]`;
                cpubar.style.width = `${cpuperc}%`;
                cputext.innerHTML = `${cpuperc}%`;
                delTable('showplayers');
                delTable('bannedplayers');
                addPlayers(data.data.showplayers, data.data.onlineplayers);
                addBannedPlayers(data.data.bannedplayers);
                set_playercount(data.data.player_count);
            });
}

if (interval_timer == ""){
    interval_timer = setInterval(function() {
        refreshData();
    }, 5000)
}
refreshData();