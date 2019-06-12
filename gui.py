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

        # ----- buttons container -----
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        clear_button = wx.Button(self.panel, label='Clear')
        clear_button.Bind(wx.EVT_BUTTON, self.clear_editors)
        buttons_sizer.Add(clear_button, 0, wx.ALL)

        # ----- main container -----
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(download_sizer, 0, wx.ALL | wx.EXPAND, 2)
        self.main_sizer.Add(lyrics_sizer, 0, wx.ALL | wx.EXPAND, 2)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 5)
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

    def clear_editors(self, event):
        self.lyrics_original.Clear()
        self.lyrics_new.Clear()
        self.SetStatusText('Editors cleard.')
        return None

    def save_lyrics(self, event):
        wildcards = 'Text file (*.txt)|*.txt|' \
                'Lyrics file (*.lyrics)|*.lyrics|' \
                'All files (*.*)|*.*'

        dialog = wx.FileDialog(
            self.panel, 
            message='Save lyrics as ...', 
            defaultDir=os.getcwd(),
            defaultFile=f'{self.artist_field.GetValue()} - {self.song_field.GetValue()}.txt', 
            wildcard=wildcards, 
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            )

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
            with open(path, 'w') as fout:
                fout.write(self.lyrics_new.GetValue())
            self.SetStatusText(f'lyrics save to {path}.')
        else:
            self.SetStatusText('save cancelled.')
        return None


class MyMenuBar(wx.MenuBar):
    def __init__(self, frame):
        wx.MenuBar.__init__(self)
        self.frame = frame

        menu1 = wx.Menu()
        menu1_open = menu1.Append(101, 'Open...')
        menu1_save = menu1.Append(102, 'Save')
        menu1.AppendSeparator()
        menu1_exit = menu1.Append(103, 'Close', 'Exit')

        menu2 = wx.Menu()
        menu2_simplified = menu2.Append(201, 'Simplified Chinese', '', wx.ITEM_RADIO)
        menu2_traditional = menu2.Append(202, 'Traditional Chinese', '', wx.ITEM_RADIO)
 
        help_menu = wx.Menu()
        about = help_menu.Append(wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU, self.file_dialog, menu1_open)
        self.Bind(wx.EVT_MENU, self.frame.save_lyrics, menu1_save)
        self.Bind(wx.EVT_MENU, self.exit_program, menu1_exit)
        self.Bind(wx.EVT_MENU, self.change_lang, menu2_simplified)
        self.Bind(wx.EVT_MENU, self.change_lang, menu2_traditional)
        self.Bind(wx.EVT_MENU, self.about_dialog, about)

        self.Append(menu1, 'File')
        self.Append(menu2, 'Options')
        self.Append(help_menu, 'Help')

    def exit_program(self, event):
        sys.exit()

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

    def change_lang(self, event):
        if event.GetId() == 201:
            self.frame.mojim.lang = 0
            self.frame.SetStatusText('Mojim language set to Simplified Chinese.')
        elif event.GetId() == 202:
            self.frame.mojim.lang = 1
            self.frame.SetStatusText('Mojim language set to Traditional Chinese.')
        return None
            


if __name__ == '__main__':
    app = wx.App()
    myframe = LyricsGUI(None, 'Lyrics Helper')
    myframe.Show()
    app.MainLoop()