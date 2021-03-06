var chapter = {
    title:"",
    index : 1,
    content : ''
}
/* https://gist.github.com/hu2di/e80d99051529dbaa7252922baafd40e3 */
var story = (function(str) {
    str = str.replace(/à|á|ạ|ả|ã|â|ầ|ấ|ậ|ẩ|ẫ|ă|ằ|ắ|ặ|ẳ|ẵ/g, "a");
    str = str.replace(/è|é|ẹ|ẻ|ẽ|ê|ề|ế|ệ|ể|ễ/g, "e");
    str = str.replace(/ì|í|ị|ỉ|ĩ/g, "i");
    str = str.replace(/ò|ó|ọ|ỏ|õ|ô|ồ|ố|ộ|ổ|ỗ|ơ|ờ|ớ|ợ|ở|ỡ/g, "o");
    str = str.replace(/ù|ú|ụ|ủ|ũ|ư|ừ|ứ|ự|ử|ữ/g, "u");
    str = str.replace(/ỳ|ý|ỵ|ỷ|ỹ/g, "y");
    str = str.replace(/đ/g, "d");
    str = str.replace(/À|Á|Ạ|Ả|Ã|Â|Ầ|Ấ|Ậ|Ẩ|Ẫ|Ă|Ằ|Ắ|Ặ|Ẳ|Ẵ/g, "A");
    str = str.replace(/È|É|Ẹ|Ẻ|Ẽ|Ê|Ề|Ế|Ệ|Ể|Ễ/g, "E");
    str = str.replace(/Ì|Í|Ị|Ỉ|Ĩ/g, "I");
    str = str.replace(/Ò|Ó|Ọ|Ỏ|Õ|Ô|Ồ|Ố|Ộ|Ổ|Ỗ|Ơ|Ờ|Ớ|Ợ|Ở|Ỡ/g, "O");
    str = str.replace(/Ù|Ú|Ụ|Ủ|Ũ|Ư|Ừ|Ứ|Ự|Ử|Ữ/g, "U");
    str = str.replace(/Ỳ|Ý|Ỵ|Ỷ|Ỹ/g, "Y");
    str = str.replace(/Đ/g, "D");
    str = str.replace(/\u0300|\u0301|\u0303|\u0309|\u0323/g, "");
    str = str.replace(/\u02C6|\u0306|\u031B/g, "");
    str = str.replace(/!|@|%|\^|\*|\(|\)|\+|\=|\<|\>|\?|\/|,|\.|\:|\;|\'|\"|\&|\#|\[|\]|~|\$|_|`|-|{|}|\||\\/g," ");
    str = str.replace(/\s+/g,' ').trim().replace(/ /g,'_');
    return str;
})(chapter.title)
function sendData(ws, data) {
    ws.send(data);
}
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
var parts = []
var lines = chapter.content.split('\n')
/* Remove duplicate title in content */
if (lines[0].toLowerCase().trim() == chapter.title.toLowerCase().trim()) {
    chapter.content = lines.slice(1).join('\n').trim()
}
/* Append title to content and make parts 72 charactors per line */
var paragraphs = ('# '+chapter.title+'\n\n'+chapter.content).split('\n')
for (var i = 0; i < paragraphs.length; i++) {
    var ch = 't:';
    if (i == 0) {
        ch = 'b:';
    } else if (i == paragraphs.length - 1) {
        ch = 'c:';
    }
    if (paragraphs[i].trim() == '') {
        parts.push({
            story : story,
            chapter:chapter.chapter,
            content:ch+'newline'
        });
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
        /* Escape markdown orderlist or numberlist in praragraph
         * because the story not required it
         */
        if (/^\-/.test(lines[j]) == true) { /* orderlist */
            lines[j] = '\\'+lines[j];
        }
        if (/^[0-9]+\./.test(lines[j]) == true) { /* numberlist */
            lines[j] = '\\'+lines[j];
        }
        parts.push({
            story : story,
            chapter:chapter.index.toString(),
            content:ch+lines[j]
        });
    }
}
var name = null;
var ws = new WebSocket('ws://127.0.0.1:9876')
function response(text) {
    console.log(text)
}
ws.onopen = function(e) {
    console.log('Ready');
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
    response('Closed')
    name = '';
}
ws.onerror = function(e) {
    response('Error');
    name = '';
}
var iid = setInterval(function() {
    if (name && name.length == 0) {
        ws.close();
        clearInterval(iid);
        return;
    }
    if (parts.length > 0) {
        var part = parts.shift();
        sendData(ws, 'c'+JSON.stringify(part));
    } else {
        clearInterval(iid)
        ws.close();
        response('All done');
    }
}, 500);
