#!/usr/bin/env python3

import os
import re
import sys
import json
import markdown
import epub
from util import *
import config

def parse_markdown(filepath):
    if not os.path.isfile(filepath):
        return (None, None)
    try:
        with open(filepath, 'r', encoding='utf-8') as fin:
            content = fin.read().rstrip()
        paragraphs = content.split('\n\n')
        title = paragraphs[0].strip().strip('#')
        markdown_data = "\n\n".join(paragraphs).strip()
        html_text = markdown.markdown(
            markdown_data,
            extensions=[
                "codehilite",
                "tables",
                "fenced_code"
            ],
            extension_configs={
                "codehilite":{
                    "guess_lang":False
                }
            }
        )
        return (title, html_text)
    except:
        return (None, None)

if __name__ == '__main__':
    if len(sys.argv) < 1:
        print('Usage: %s <folder_name>' % sys.argv[0])
        sys.exit(0)
    folder = os.path.join(config.BOOK_DIRECTORY, sys.argv[1].strip())
    if not folder or not os.path.isdir(folder):
        print('Folder is not exists\nUsage: %s <folder>' % sys.argv[0])
        sys.exit(0)
    if not os.path.isfile("%s/metadata.json" % folder):
        print('File "metadata.json" not found in %s' % folder)
        sys.exit(0)
    try:
        with open("%s/metadata.json" % folder, 'r', encoding='utf-8') as fin:
            metadata = json.load(fin)
        book = epub.EpubBook()
        book.set_identifier(metadata["metadata"]["dc:identifier"])
        book.set_title(metadata["metadata"]['dc:title'])
        book.set_language(metadata["metadata"]['dc:language'])
        book.add_author(metadata["metadata"]['dc:creator'])
        has_cover = False
        if metadata['cover'].strip():
            cover_file = os.path.join(folder, metadata['cover'])
            if os.path.isfile(cover_file):
                has_cover = True
                print('Add cover "%s" file' % cover_file)
                book.set_cover("cover.jpg", open(cover_file, 'rb').read())
        style = '''body { font-size: 0.8em; } img { max-width: 100%; height: auto;   } table { border-collapse: collapse; width: 100%; font-size: 0.5em; } td,th { border: 1px solid #ddd; padding: 8px; } tr:nth-child(even){ background-color: #f2f2f2; } th { padding-top: 12px; padding-bottom: 12px; text-align: left; background-color: #444444; color: white; font-size: 0.8em; } figcaption { font-size: medium; padding:2% 5%; color:#888; font-style:italic; } code { color:brown; } pre { padding:10px; } pre > code { color:#000; } blockquote { border-left:2px solid #d0d7de; color:#57606a; background-color: #f2f2f2; padding: 0.1em 1em; margin:0; }'''
        default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=style)
        book.add_item(default_css)
        chapters = []
        for md in metadata['chapters']:
            title, html = parse_markdown(os.path.join(folder, md))
            if not title:
                continue
            chapter = epub.EpubHtml(title=title, file_name="%s" % md.replace('.md','.xhtml'), lang=metadata["metadata"]['dc:language'])
            chapter.content = html
            book.add_item(chapter)
            chapters.append(chapter)
        book.toc = chapters
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        style = '''@namespace epub "http://www.idpf.org/2007/ops"; body { font-family: Cambria, Liberation Serif, Bitstream Vera Serif, Georgia, Times, Times New Roman, serif; } h2 { text-align: left; text-transform: uppercase; font-weight: 200; } ol { list-style-type: none; } ol > li:first-child { margin-top: 0.3em; } nav[epub|type~='toc'] > ol > li > ol  { list-style-type:square; } nav[epub|type~='toc'] > ol > li > ol > li { margin-top: 0.3em; }'''
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
        book.add_item(nav_css)
        if has_cover:
            book.spine = ['cover','nav', *chapters]
        else:
            book.spine = ['nav', *chapters]
        epub_name = no_accent(unicode_replace(metadata["metadata"]['dc:title']))
        epub_name = re.sub(r'\s+',' ', epub_name)
        epub_name = epub_name.strip().replace(' ','_')
        epub.write_epub(os.path.join(config.EPUB_DIRECTORY, '%s.epub' % epub_name), book, {})
    except Exception as e:
        print('Error', e)
    sys.exit(0)
