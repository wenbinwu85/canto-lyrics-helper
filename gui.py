import os
import sys
import wx
from cantolyrics import Character, Word, Mojim


class LyricsGUI(wx.Frame):
    def __init__(self, parent, title, size=(640, 800)):
        wx.Frame.__init__(
            self, parent, title=title, size=size,
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
            )
        self.CenterOnScreen()
        self.panel = wx.Panel(self)
        self.mojim = Mojim()

        # ----- search field container -----
        download_sizer = wx.StaticBoxSizer(
            wx.HORIZONTAL, self.panel, label='Download Lyrics from Mojim'
            )
        song_label = wx.StaticText(self.panel, label='Song:', size=(40, -1))
        self.song_field = wx.TextCtrl(self.panel, size=(200, -1))
        artist_label = wx.StaticText(self.panel, label='Artist:', size=(40, -1))
        self.artist_field = wx.TextCtrl(self.panel, size=(200, -1))
        download_button = wx.Button(self.panel, label='Download')
        download_button.Bind(wx.EVT_BUTTON, self.download_lyrics)
        download_sizer.Add(song_label, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(self.song_field, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(artist_label, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(self.artist_field, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(download_button, 0, wx.ALL | wx.CENTER, 5)

        # ----- editor container -----
        lyrics_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self.panel, label='Lyrics')
        self.lyrics_original = wx.TextCtrl(
            self.panel, -1, size=(320, 600), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
            )
        self.lyrics_new = wx.TextCtrl(
            self.panel, -1, size=(320, 600), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
            )
        lyrics_sizer.Add(self.lyrics_original, 0, wx.ALL)
        lyrics_sizer.Add(self.lyrics_new, 0, wx.ALL)

        # ----- main container -----
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(download_sizer, 0, wx.ALL | wx.EXPAND, 2)
        self.main_sizer.Add(lyrics_sizer, 0, wx.ALL | wx.EXPAND, 2)
        self.main_sizer.Fit(self.panel)
        self.panel.SetSizer(self.main_sizer)

        # ----- menu bar -----
        menubar = MyMenuBar(self)
        self.SetMenuBar(menubar)

        # ----- status bar -----
        self.CreateStatusBar()
        self.SetStatusText('Hello World.')

    def download_lyrics(self, event):
        song = self.song_field.GetValue()
        self.mojim.artist = self.artist_field.GetValue()
        file = f'{self.mojim.artist} - {song}.txt'
        if self.mojim.save(song):
            with open(file, 'r') as lyrics:
                self.lyrics_original.Clear()
                self.lyrics_original.write(''.join(lyrics))
            self.SetStatusText(f'lyrics for {self.mojim.artist} - {song} saved.')
        else:
            self.SetStatusText(
                f'unable to download lyrics for {self.mojim.artist} - {song}.'
                )
        return None


class MyMenuBar(wx.MenuBar):
    def __init__(self, frame):
        wx.MenuBar.__init__(self)
        self.frame = frame

        menu1 = wx.Menu()
        menu1.Append(101, 'Open...')
        menu1.Append(102, 'Save')
        menu1.AppendSeparator()
        menu1.Append(103, 'Close', 'Exit')

        menu2 = wx.Menu()
        menu2.Append(201, 'Clear')

        menu3 = wx.Menu()
        menu3.Append(301, 'Use Simplified Chinese', '', wx.ITEM_RADIO)
        menu3.Append(302, 'Use Traditional Chinese', '', wx.ITEM_RADIO)
 
        menu4 = wx.Menu()
        menu4.Append(401, 'Dictionary')


        help_menu = wx.Menu()
        about = help_menu.Append(wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU, self.file_dialog, id=101)
        self.Bind(wx.EVT_MENU, self.save_lyrics, id=102)
        self.Bind(wx.EVT_MENU, self.exit_program, id=103)
        self.Bind(wx.EVT_MENU, self.clear_editors, id=201)
        self.Bind(wx.EVT_MENU, self.change_lang, id=301)
        self.Bind(wx.EVT_MENU, self.change_lang, id=302)
        self.Bind(wx.EVT_MENU, self.about_dialog, about)

        self.Append(menu1, 'File')
        self.Append(menu2, 'Edit')
        self.Append(menu3, 'Mojim')
        self.Append(menu4, 'Tools')
        self.Append(help_menu, 'Help')

    def file_dialog(self, event):
        """file dialog"""

        wildcards = 'Text file (*.txt)|*.txt|' \
                'Lyrics file (*.lyrics)|*.lyrics|' \
                'All files (*.*)|*.*'

        dialog = wx.FileDialog(
            self, 
            message='Choose a lyrics file',
            defaultDir=os.getcwd(),
            defaultFile='',
            wildcard=wildcards,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | 
            wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW
            )

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            with open(path, 'r') as file:
                self.frame.lyrics_original.Clear()
                self.frame.lyrics_original.write(''.join(file))
        return None

    def save_lyrics(self, event):
        wildcards = 'Text file (*.txt)|*.txt|' \
                'Lyrics file (*.lyrics)|*.lyrics|' \
                'All files (*.*)|*.*'

        dialog = wx.FileDialog(
            self, 
            message='Save lyrics as ...', 
            defaultDir=os.getcwd(),
            defaultFile=f'{self.frame.artist_field.GetValue()} - {self.frame.song_field.GetValue()}.txt', 
            wildcard=wildcards, 
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            with open(path, 'w') as fout:
                fout.write(self.frame.lyrics_new.GetValue())
            self.SetStatusText(f'lyrics save to {path}.')
        else:
            self.SetStatusText('save cancelled.')
        return None

    def exit_program(self, event):
        sys.exit()

    def clear_editors(self, event):
        self.frame.lyrics_original.Clear()
        self.frame.lyrics_new.Clear()
        self.SetStatusText('Editors cleard.')
        return None

    def change_lang(self, event):
        if event.GetId() == 301:
            self.frame.mojim.lang = 0
            self.frame.SetStatusText('Mojim language set to Simplified Chinese.')
        elif event.GetId() == 302:
            self.frame.mojim.lang = 1
            self.frame.SetStatusText('Mojim language set to Traditional Chinese.')
        return None
            
    def about_dialog(self, event):
        """about dialog box"""

        info = wx.adv.AboutDialogInfo()
        info.Name = '歌词助手'
        info.Version = 'v0.0.3'
        info.Copyright = '(c) 2019 Wenbin Wu\n' 
        info.Description = '' + \
            'Email: dev@wuwenb.in\n' + \
            'Github: https://github.com/wenbinwu85/'     
        wx.adv.AboutBox(info)
        return None


if __name__ == '__main__':
    app = wx.App()
    myframe = LyricsGUI(None, 'Lyrics Helper')
    myframe.Show()
    app.MainLoop()