function sendData(ws, data) {
    ws.send(data);
}
/* Break line if length of paragraph greater than 72 charactors */
function line_break(s) {
    var words = s.split(' ').map(function(v) {
        return v.trim();
    }).filter(function(v) {
        return v.length > 0;
    });
    var lines = []
    var line = ''
    for (var i = 0; i < words.length; i++) {
        line += ' ' + words[i];
        if(line.trim().length >= 72) {
            lines.push(line.trim());
            line = '';
        }
    }
    if(line.trim().length > 0) {
        lines.push(line.trim());
    }
    return lines;
}
/* Initial story object */
var story = {
    title:"",
    intro:"",
    cover:"",
    author:"",
    categories:[]
}
/* Add data to parts */
var parts = []
parts.push({
    name:story.title
})
if (story.cover.length > 0) {
    parts.push({
        cover : story.cover
    });
}
parts.push({
    author : story.author
});
if (story.categories != undefined && story.categories.length > 0) {
    parts.push({
        categories : story.categories
    });
}
var paragraphs = ('# Introduction\n\n'+story.intro).split('\n')
for (var i = 0; i < paragraphs.length; i++) {
    var ch = 't:';
    if (i == 0) {
        ch = 'b:';
    } else if (i == paragraphs.length - 1) {
        ch = 'c:';
    }
    if (paragraphs[i].trim() == '') {
        parts.push({intro:ch+'newline'});
        continue;
    }
    var lines = line_break(paragraphs[i]);
    for(var j = 0; j < lines.length; j++) {
        if (ch == 'b:') {
            if (j > 0) {
                ch = 't:';
            }
        }
        lines[j] = lines[j].trim()
        if (/^\-/.test(lines[j]) == true) {
            lines[j] = '\\'+lines[j];
        }
        if (/^[0-9]+\./.test(lines[j]) == true) {
            lines[j] = '\\'+lines[j];
        }
        parts.push({intro:ch+lines[j]});
    }
}
var name = null;
var ws = new WebSocket('ws://127.0.0.1:9876')
function response(text) {
    console.log(text)
}
ws.onopen = function(e) {
    response('Ready');
};
ws.onmessage = function(e) {
    const obj = JSON.parse(e.data || '{}');
    if (obj['name'] != undefined && obj['name'].length > 0) {
        name = obj['name'].trim();
    }
    if (obj['message'] != undefined) {
        response(obj['message'])
        name = '';
    } else if (obj['error'] != undefined) {
        response(obj['error'])
        name = '';
    }
};
ws.onclose = function(e) {
    name = '';
    response('Closed')
}
ws.onerror = function(e) {
    name = '';
    response('Error');
}
var part = parts.shift();
sendData(ws, 's'+JSON.stringify(part));
var iid = setInterval(function() {
    if (name && name.length == 0) {
        ws.close();
        clearInterval(iid);
        return;
    }
    if (parts.length > 0) {
        var part = parts.shift();
        part.story = name;
        sendData(ws, 's'+JSON.stringify(part));
    } else {
        clearInterval(iid);
        ws.close();
        console.log('All done');
    }
}, 500);
