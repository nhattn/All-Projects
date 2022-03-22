# -*- coding: utf-8 -*-

import re
import markdown
import zipfile
import os
import json
from xml.dom import minidom
from markdown import Extension
from markdown.util import etree
from markdown.inlinepatterns import IMAGE_LINK_RE
from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import LinkInlineProcessor
from markdown.extensions.attr_list import AttrListTreeprocessor

class ImageInlineProcessor(LinkInlineProcessor):
    def handleMatch(self, m, data):
        text, index, handled = self.getText(data, m.end(0))
        if not handled:
            return None, None, None

        src, title, index, handled = self.getLink(data, index)
        if not handled:
            return None, None, None

        fig = etree.Element('figure')
        img = etree.SubElement(fig, 'img')
        img.set('src', src)

        if title is not None:
            img.set("title", self.unescape(title))

        if '::cap::' in text:
            alt, caption = [ v.strip() for v in text.split("::cap::")]
            if caption:
                cap = etree.SubElement(fig, 'figcaption')
                cap.text = caption
            img.set('alt', self.unescape(alt))
        else:
            img.set('alt', self.unescape(text))

        if 'attr_list' in self.md.treeprocessors:
            curly = re.match(AttrListTreeprocessor.BASE_RE, data[index:])
            if curly:
                fig[-1].tail = '\n'
                fig[-1].tail += curly.group()
                index += curly.endpos
        return fig, m.start(0), index

class FigureTreeprocessor(Treeprocessor):
    def run(self, root):
        for p in root.iterfind('p'):
            figure = p.find("figure")
            if figure is not None:
                p.tag = None
                p.attrib = None

class FigureCaption(Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.register(ImageInlineProcessor(IMAGE_LINK_RE, md), 'caption', 151)
        md.treeprocessors.register(FigureTreeprocessor(md), 'fig_cap', 7)

def get_all_filenames(the_dir,extensions=[]):
    all_files = [x for x in os.listdir(the_dir)]
    all_files = [x for x in all_files if x.split(".")[-1] in extensions]
    return all_files

def get_packageOPF_XML(md_filenames=[],image_filenames=[],css_filenames=[],description_data=None):
    doc = minidom.Document()

    package = doc.createElement('package')
    package.setAttribute('xmlns',"http://www.idpf.org/2007/opf")
    package.setAttribute('version',"3.0")
    package.setAttribute('xml:lang',"en")
    package.setAttribute("unique-identifier","pub-id")

    metadata = doc.createElement('metadata')
    metadata.setAttribute('xmlns:dc', 'http://purl.org/dc/elements/1.1/')

    manifest = doc.createElement('manifest')

    x = doc.createElement('item')
    x.setAttribute('id',"toc")
    x.setAttribute('properties',"nav")
    x.setAttribute('href',"TOC.xhtml")
    x.setAttribute('media-type',"application/xhtml+xml")
    manifest.appendChild(x)

    x = doc.createElement('item')
    x.setAttribute('id',"ncx")
    x.setAttribute('href',"toc.ncx")
    x.setAttribute('media-type',"application/x-dtbncx+xml")
    manifest.appendChild(x)

    x = doc.createElement('item')
    x.setAttribute('id',"titlepage")
    x.setAttribute('href',"titlepage.xhtml")
    x.setAttribute('media-type',"application/xhtml+xml")
    manifest.appendChild(x)

    for i,md_filename in enumerate(md_filenames):
        x = doc.createElement('item')
        x.setAttribute('id',"s{:05d}".format(i))
        x.setAttribute('href',"s{:05d}-{}.xhtml".format(i,md_filename.split(".")[0]))
        x.setAttribute('media-type',"application/xhtml+xml")
        manifest.appendChild(x)

    for i,image_filename in enumerate(image_filenames):
        x = doc.createElement('item')
        x.setAttribute('id',"image-{:05d}".format(i))
        x.setAttribute('href',"images/{}".format(image_filename))
        if "gif" in image_filename:
            x.setAttribute('media-type',"image/gif")
        elif "jpg" in image_filename:
            x.setAttribute('media-type',"image/jpeg")
        elif "jpeg" in image_filename:
            x.setAttribute('media-type',"image/jpg")
        elif "png" in image_filename:
            x.setAttribute('media-type',"image/png")
        if image_filename==description_data["cover_image"]:
            x.setAttribute('properties',"cover-image")
            y = doc.createElement('meta')
            y.setAttribute('name',"cover")
            y.setAttribute('content',"image-{:05d}".format(i))
            metadata.appendChild(y)
        manifest.appendChild(x)

    for i,css_filename in enumerate(css_filenames):
        x = doc.createElement('item')
        x.setAttribute('id',"css-{:05d}".format(i))
        x.setAttribute('href',"css/{}".format(css_filename))
        x.setAttribute('media-type',"text/css")
        manifest.appendChild(x)

    spine = doc.createElement('spine')
    spine.setAttribute('toc', "ncx")

    x = doc.createElement('itemref')
    x.setAttribute('idref',"titlepage")
    x.setAttribute('linear',"yes")
    spine.appendChild(x)
    for i,md_filename in enumerate(md_filenames):
        x = doc.createElement('itemref')
        x.setAttribute('idref',"s{:05d}".format(i))
        x.setAttribute('linear',"yes")
        spine.appendChild(x)

    guide = doc.createElement('guide')
    x = doc.createElement('reference')
    x.setAttribute('type',"cover")
    x.setAttribute('title',"Cover image")
    x.setAttribute('href',"titlepage.xhtml")
    guide.appendChild(x)


    package.appendChild(metadata)
    package.appendChild(manifest)
    package.appendChild(spine)
    package.appendChild(guide)
    doc.appendChild(package)

    return doc.toprettyxml()

def get_container_XML():
    container_data = """<?xml version="1.0" encoding="UTF-8" ?>\n"""
    container_data += """<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n"""
    container_data += """<rootfiles>\n"""
    container_data += """<rootfile full-path="OPS/package.opf" media-type="application/oebps-package+xml"/>\n"""
    container_data += """</rootfiles>\n</container>"""
    return container_data

def get_coverpage_XML(cover_image_path):
    all_xhtml = """<?xml version="1.0" encoding="utf-8"?>\n"""
    all_xhtml += """<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr">\n"""
    all_xhtml += """<head>\n</head>\n<body>\n"""
    all_xhtml += """<img src="images/{}" style="height:100%;max-width:100%;"/>\n""".format(cover_image_path)
    all_xhtml += """</body>\n</html>"""
    return all_xhtml

def get_TOC_XML(default_css_filenames,markdown_filenames):
    toc_xhtml = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    toc_xhtml += """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">\n"""
    toc_xhtml += """<head>\n<meta http-equiv="default-style" content="text/html; charset=utf-8"/>\n"""
    toc_xhtml += """<title>Contents</title>\n"""

    for css_filename in default_css_filenames:
        toc_xhtml += """<link rel="stylesheet" href="css/{}" type="text/css"/>\n""".format(css_filename)

    toc_xhtml += """</head>\n<body>\n"""
    toc_xhtml += """<nav epub:type="toc" role="doc-toc" id="toc">\n<h2>Contents</h2>\n<ol epub:type="list">"""
    for i,md_filename in enumerate(markdown_filenames):
        toc_xhtml += """<li><a href="s{:05d}-{}.xhtml">{}</a></li>""".format(i,md_filename.split(".")[0],md_filename.split(".")[0])
    toc_xhtml += """</ol>\n</nav>\n</body>\n</html>"""

    return toc_xhtml

def get_TOCNCX_XML(markdown_filenames):
    toc_ncx = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    toc_ncx += """<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" xml:lang="fr" version="2005-1">\n"""
    toc_ncx += """<head>\n</head>\n"""
    toc_ncx += """<navMap>\n"""
    for i,md_filename in enumerate(markdown_filenames):
        toc_ncx += """<navPoint id="navpoint-{}">\n""".format(i)
        toc_ncx += """<navLabel>\n<text>{}</text>\n</navLabel>""".format(md_filename.split(".")[0])
        toc_ncx += """<content src="s{:05d}-{}.xhtml"/>""".format(i,md_filename.split(".")[0])
        toc_ncx += """ </navPoint>"""
    toc_ncx += """</navMap>\n</ncx>"""
    return toc_ncx

def get_chapter_XML(md_filename,css_filenames):
    with open(os.path.join(md_filename),"r",encoding="utf-8") as f:
        markdown_data = f.read()
    html_text = markdown.markdown(
        markdown_data,
        extensions=[
            "codehilite",
            "tables",
            "fenced_code",
            FigureCaption()
        ],
        extension_configs={
            "codehilite":{
                "guess_lang":False
            }
        }
    )

    all_xhtml = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    all_xhtml += """<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">\n"""
    all_xhtml += """<head>\n<meta http-equiv="default-style" content="text/html; charset=utf-8"/>\n"""

    for css_filename in css_filenames:
        all_xhtml += """<link rel="stylesheet" href="css/{}" type="text/css"/>\n""".format(css_filename)

    all_xhtml += """</head>\n<body>\n"""

    all_xhtml += html_text
    all_xhtml += """\n</body>\n</html>"""

    return all_xhtml
