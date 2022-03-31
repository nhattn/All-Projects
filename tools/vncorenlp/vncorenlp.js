var styl = document.createElement('style')
styl.textContent = `#vtoolkit {
    width:300px;
    top:10px;
    right:10px;
    border: #ffc810;
    background-color: #fffae6;
    padding:10px;
    border-radius: 3px;
    z-index:999999;
    position:fixed;
}
#vtoolkit p {
    margin:22px 0;
}
#vtoolkit textarea {
    width: 100%;
    min-height: 80px;
    padding: 10px;
    min-width: 100%;
    font-size: large;
    box-sizing: border-box;
    border: none;
    background-color: #fff;
}
#vtoolkit textarea::-webkit-scrollbar {
    width: 6px;
}
#vtoolkit textarea::-webkit-scrollbar-thumb {
    border-radius: 4px;
    -webkit-box-shadow: inset 0 0 6px rgb(0 0 0 / 50%);
}
#vtoolkit textarea::-webkit-scrollbar-track {
    -webkit-box-shadow: inset #fff;
    border-radius: 4px;
}
#vtoolsend {
    padding: 5px 15px;
    border: none;
    background-color: #2fa1b3;
    color: #fff;
    border-radius: 5px;
    font-weight: bold;
    font-size: large;
}
.vtoolkit {
    display:none;
}
.vtoolkit-show {
    display:block;
}`;
document.head.appendChild(styl)
var socket = null;
function initSocket() {
    var ws = new WebSocket('ws://127.0.0.1:9876')
    ws.onopen = function(e) {
        var el = document.querySelector('#vtool-alert');
        if (el) {
            el.innerText = 'Connected';
        } else {
            console.log('Connected');
        }
    }
    ws.onmessage = function(e) {
        var el = document.querySelector('#vtool-alert');
        if (el) {
            el.innerText = e.data || 'no data';
        } else {
            console.log(e.data || 'no data')
        }
    }
    ws.onclose = function(e) {
        var el = document.querySelector('#vtool-alert');
        if (el) {
            el.innerText = 'Closed';
        } else {
            console.log('Closed')
        }
    }
    ws.onerror = function(e) {
        var el = document.querySelector('#vtool-alert');
        if (el) {
            el.innerText = 'error';
        } else {
            console.log('error');
        }
    }
    return ws;
}
var div = document.createElement('div');
div.id = 'vtoolkit'
div.className = 'vtoolkit'
var p = document.createElement('p');
var textarea = document.createElement('textarea')
textarea.name = 'sentence'
p.appendChild(textarea)
div.appendChild(p);
var button = document.createElement('button');
button.id = "vtoolsend"
button.innerText = 'Send'
button.addEventListener('click', function(e) {
    e.preventDefault();
    var text = textarea.value.trim();
    if (text.length == 0) {
        return false;
    }
    var delay = 1;
    if (socket == null || socket.readyState != socket.OPEN) {
        socket = initSocket();
        delay = 100;
    }
    setTimeout(function(ws) {
        if (ws.readyState == ws.OPEN) {
            ws.send(text)
        }
    }, delay, socket);
    return false;
});
var p2 = document.createElement('p');
p2.appendChild(button)
div.appendChild(p2);
var p3 = document.createElement('p');
p3.id = "vtool-alert"
div.appendChild(p3);
document.body.appendChild(div)
document.addEventListener('mouseup', function(e) {
    const selection = window.getSelection().toString();
    if (selection.trim().length > 0) {
        textarea.value = selection.trim();
        if (div.className.indexOf('vtoolkit-show') == -1) {
            div.className = 'vtoolkit-show'
        }
    }
});
