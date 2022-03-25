var entries = (function(){
    var text = localStorage.entries || '[]';
    try {
        return JSON.parse(text);
    } catch(e) {
        return [];
    }
})();
document.querySelectorAll('.posts.main').forEach(function(node, i, all) {
    var clone = node.cloneNode(true);
    var link = clone.querySelector('a.notecount').href;
    clone.querySelectorAll('img').forEach(function(el) {
        var src = el.src;
        var sp = document.createElement('p')
        sp.innerHTML = '\n\n![]('+src +')&nbsp;\n\n<br />';
        el.parentNode.insertBefore(sp, el);
    });
    var link_wrap = clone.querySelector('a.link-wrap');
    if (link_wrap && link_wrap.href.indexOf('https://href.li/?') != -1) {
        var out = link_wrap.href.replace('https://href.li/?','');
        var sp = document.createElement('p')
        var tt = link_wrap.querySelector('div.title');
        var title = out;
        if (tt) {
            title = tt.textContent.trim();
        }
        sp.innerHTML = '\n\n['+title+']('+out +')&nbsp;\n\n<br />';
        link_wrap.parentNode.insertBefore(sp, link_wrap);
        link_wrap.remove();
    }
    clone.querySelectorAll('.infobg,.asker-wrap').forEach(function(el) {
        el.remove()
    })
    clone.querySelectorAll('br').forEach(function(el) {
        var sp = document.createElement('sp')
        sp.innerHTML = '\n\n&nbsp;\n\n';
        el.parentNode.insertBefore(sp, el);
        el.remove()
    })
    clone.querySelectorAll('p').forEach(function(el) {
        var sp = document.createElement('sp')
        sp.innerHTML = '\n\n&nbsp;\n\n';
        el.parentNode.insertBefore(sp, el);
    })
    var markdown = clone.textContent.replace(/\n{2,}/g,'\n').replace(/ {2,}/g,' ').trim();
    markdown = markdown.replace(/ \n \n \n \n /g,'\n\n').replace(/\n \n \n/g,'\n\n').trim();
    markdown = markdown.replace(/”/g,'"')
    markdown = markdown.replace(/“/g,'"')
    markdown = markdown.replace(/…/g,'...')
    entry = {
        id : Number(entries.length) + 1,
        content : markdown,
        link : link
    };
    entries.push(entry);
    if (i == all.length - 1) {
        var text = JSON.stringify(entries);
        localStorage.entries = text;
        console.log('Done', entries.length)
    }
})
