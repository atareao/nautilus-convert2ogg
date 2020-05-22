#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# This file is part of nautilus-convert2ogg
#
# Copyright (c) 2016 Lorenzo Carbonell Cerezo <a.k.a. atareao>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gi
try:
    gi.require_version('Gtk', '3.0')
    gi.require_version('GObject', '2.0')
    gi.require_version('Nautilus', '3.0')
except Exception as e:
    print(e)
    exit(-1)
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Nautilus as FileManager
import sys
import os
import locale
import gettext
from plumbum import local
try:
    sys.path.insert(1, '/usr/share/nanecalib')
    from nanecalib import DoItInBackground
except Exception as nanecalib_error:
    print(nanecalib_error)
    sys.exit(-1)

APP = '$APP$'
ICON = '$APP$'
VERSION = '$VERSION$'
LANGDIR = os.path.join('usr', 'share', 'locale-langpack')

current_locale, encoding = locale.getdefaultlocale()
language = gettext.translation(APP, LANGDIR, [current_locale])
language.install()
_ = language.gettext

EXTENSIONS_FROM = ['.acc', '.ac3', '.mp3', '.wav', '.mp4', '.flv', '.mkv']


class ConvertDIIB(DoItInBackground):
    def __init__(self, title, parent, files):
        DoItInBackground.__init__(self, title, parent, files, ICON)

    def process_item(self, file_in):
        head, tail = os.path.split(file_in)
        root, ext = os.path.splitext(tail)
        file_out = os.path.join(head, root + '.ogg')
        if os.path.exists(file_out):
            os.remove(file_out)
        ffmpeg = local['ffmpeg']
        ffmpeg['-i', '{}'.format(file_in), '-vn', '-acodec',
               'libvorbis', '-y', '{}'.format(file_out)]()


class MP3ConvereterMenuProvider(GObject.GObject, FileManager.MenuProvider):
    """
    Implements the 'Replace in Filenames' extension to the File Manager\
    right-click menu
    """

    def __init__(self):
        """
        File Manager crashes if a plugin doesn't implement the __init__\
        method
        """
        GObject.GObject.__init__(self)

    def process(self, menu, files, window):
        diib = ConvertDIIB(_('Convert file'), window, files)
        diib.run()

    def get_file_items(self, window, sel_items):
        """
        Adds the 'Replace in Filenames' menu item to the File Manager\
        right-click menu, connects its 'activate' signal to the 'run'\
        method passing the selected Directory/File
        """
        files = []
        for file_in in sel_items:
            if not file_in.is_directory():
                afile = file_in.get_location().get_path()
                filename, fileextension = os.path.splitext(afile)
                if fileextension in EXTENSIONS_FROM:
                    files.append(afile)
        if files:
            top_menuitem = FileManager.MenuItem(
                name='MP3ConverterMenuProvider::Gtk-convert2ogg-top',
                label=_('Convert to ogg'),
                tip=_('Tool to convert to ogg'))
            submenu = FileManager.Menu()
            top_menuitem.set_submenu(submenu)

            sub_menuitem_00 = FileManager.MenuItem(
                name='MP3ConverterMenuProvider::Gtk-convert2ogg-sub-01',
                label=_('Convert'),
                tip=_('Tool to convert to ogg'))
            sub_menuitem_00.connect('activate',
                                    self.process,
                                    files,
                                    window)
            submenu.append_item(sub_menuitem_00)
            sub_menuitem_01 = FileManager.MenuItem(
                name='MP3ConverterMenuProvider::Gtk-convert2ogg-sub-02',
                label=_('About'),
                tip=_('About'))
            sub_menuitem_01.connect('activate', self.about, window)
            submenu.append_item(sub_menuitem_01)
            return top_menuitem,
        return

    def about(self, widget, window):
        ad = Gtk.AboutDialog(parent=window)
        ad.set_name(APP)
        ad.set_version(VERSION)
        ad.set_copyright('Copyrignt (c) 2016\nLorenzo Carbonell')
        ad.set_comments(APP)
        ad.set_license('''
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''')
        ad.set_website('https://www.atareao.es')
        ad.set_website_label('atareao.es')
        ad.set_authors([
            'Lorenzo Carbonell <a.k.a. atareao>'])
        ad.set_documenters([
            'Lorenzo Carbonell <a.k.a. atareao>'])
        ad.set_icon_name(ICON)
        ad.set_logo_icon_name(APP)
        ad.run()
        ad.destroy()
