import os
import sys
import wx
import wx.aui as aui
from cantolyrics import Character, Word, Mojim

mojim_lang = 0

class LyricsGUI(wx.Frame):
    def __init__(self, parent, title, size=(640, 800)):
        super().__init__(
            parent, title=title, size=size,
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
            )
        self.CenterOnScreen()
        self.notebook = aui.AuiNotebook(self)

        # ----- add main page -----
        page1 = MainPage(self)
        self.notebook.AddPage(page1, 'Main')

        # ----- add dictionary page -----
        page2 = DictionaryPage(self)
        self.notebook.AddPage(page2, 'Dictionary')

        # ----- main contianer -----
        main_sizer = wx.BoxSizer()
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        wx.CallAfter(self.notebook.SendSizeEvent)

        # ----- menu bar -----
        menubar = MyMenuBar(self)
        self.SetMenuBar(menubar)

        # ----- status bar -----
        self.CreateStatusBar()
        self.SetStatusText('Hello World.')

class MyMenuBar(wx.MenuBar):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame

        menu1 = wx.Menu()
        menu1.Append(101, 'Open on left editor')
        menu1.Append(102, 'Open on right editor')
        menu1.Append(103, 'Save left file')
        menu1.Append(104, 'Save right file')
        menu1.AppendSeparator()
        menu1.Append(105, 'Close', 'Exit')

        menu3 = wx.Menu()
        menu3.Append(301, 'Use Simplified Chinese', '', wx.ITEM_RADIO)
        menu3.Append(302, 'Use Traditional Chinese', '', wx.ITEM_RADIO)
 
        menu4 = wx.Menu()
        menu4.Append(401, 'Main')
        menu4.Append(402, 'Dictionary')

        help_menu = wx.Menu()
        about = help_menu.Append(wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU, self.file_dialog, id=101)
        self.Bind(wx.EVT_MENU, self.file_dialog, id=102)
        self.Bind(wx.EVT_MENU, self.save_dialog, id=103)
        self.Bind(wx.EVT_MENU, self.save_dialog, id=104)
        self.Bind(wx.EVT_MENU, self.exit_program, id=105)
        self.Bind(wx.EVT_MENU, self.change_lang, id=301)
        self.Bind(wx.EVT_MENU, self.change_lang, id=302)
        self.Bind(wx.EVT_MENU, self.append_page, id=401)
        self.Bind(wx.EVT_MENU, self.append_page, id=402)
        self.Bind(wx.EVT_MENU, self.about_dialog, about)

        self.Append(menu1, '&File')
        self.Append(menu3, 'Mojim')
        self.Append(menu4, 'Pages')
        self.Append(help_menu, '&Help')

    def file_dialog(self, event):
        if event.GetId() == 101:
            editor = self.frame.left_editor
        if event.GetId() == 102:
            editor = self.frame.right_editor
        
        wildcards = 'Text file (*.txt)|*.txt|' \
                'Lyrics file (*.lyrics)|*.lyrics|' \
                'All files (*.*)|*.*'

        with wx.FileDialog(
            self, 
            message='Choose a lyrics file',
            defaultDir=os.getcwd(),
            defaultFile='',
            wildcard=wildcards,
            style=wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_CHANGE_DIR | 
            wx.FD_FILE_MUST_EXIST | wx.FD_PREVIEW
            ) as dialog:

            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                with open(path, 'r') as file:
                    editor.Clear()
                    editor.write(''.join(file))
        return None

    def save_dialog(self, event):
        if event.GetId() == 103:
            editor = self.frame.left_editor
        else:
            editor = self.frame.right_editor

        wildcards = 'Text file (*.txt)|*.txt|' \
                'Lyrics file (*.lyrics)|*.lyrics|' \
                'All files (*.*)|*.*'

        with wx.FileDialog(
            self, 
            message='Save lyrics as ...', 
            defaultDir=os.getcwd(),
            defaultFile=f'{self.frame.artist_field.GetValue()} - {self.frame.song_field.GetValue()}.txt', 
            wildcard=wildcards, 
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
            ) as dialog:

            if dialog.ShowModal() == wx.ID_OK:
                path = dialog.GetPath()
                with open(path, 'w') as fout:
                    fout.write(editor.GetValue())
                self.SetStatusText(f'lyrics save to {path}.')
            else:
                self.SetStatusText('save cancelled.')
        return None

    def exit_program(self, event):
        sys.exit()

    def change_lang(self, event):
        global mojim_lang 
        if event.GetId() == 301:
            mojim_lang = 0
            self.frame.SetStatusText('Mojim language set to Simplified Chinese.')
        elif event.GetId() == 302:
            mojim_lang = 1
            self.frame.SetStatusText('Mojim language set to Traditional Chinese.')

        return None

    def append_page(self, event):
        if event.GetId() == 401:
            page = MainPage(self.frame)
            label = 'Main'
        else:
            page = DictionaryPage(self.frame)
            label = 'Dictionary'
        self.frame.notebook.AddPage(page, label)
        return None
                                            
    def about_dialog(self, event):
        """about dialog box"""

        info = wx.adv.AboutDialogInfo()
        info.Name = 'Canto Lyrics Helper'
        info.Version = 'v0.0.7'
        info.Copyright = '(c) 2019 Wenbin Wu\n' 
        info.Description = '' + \
            'Email: dev@wuwenb.in\n' + \
            'Github: https://github.com/wenbinwu85/'     
        wx.adv.AboutBox(info)
        return None


class MainPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.frame = parent
        self.mojim = Mojim()

        # ----- search field container -----
        download_sizer = wx.BoxSizer(wx.HORIZONTAL)
        song_label = wx.StaticText(self, label='Song:', size=(40, -1))
        self.song_field = wx.TextCtrl(self, size=(200, -1))
        artist_label = wx.StaticText(self, label='Artist:', size=(40, -1))
        self.artist_field = wx.TextCtrl(self, size=(200, -1))
        download_button = wx.Button(self, label='Download')
        download_button.Bind(wx.EVT_BUTTON, self.download_lyrics)
        download_sizer.Add(song_label, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(self.song_field, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(artist_label, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(self.artist_field, 0, wx.ALL | wx.CENTER, 3)
        download_sizer.Add(download_button, 0, wx.ALL | wx.CENTER, 5)

        # ----- editor container -----
        lyrics_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self, label='Lyrics Editors')
        self.left_editor = wx.TextCtrl(
            self, -1, size=(320, 600), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
            )
        self.right_editor = wx.TextCtrl(
            self, -1, size=(320, 600), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
            )
        lyrics_sizer.Add(self.left_editor)
        lyrics_sizer.Add(self.right_editor)

        # ----- main container -----
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(download_sizer, 0, wx.ALL | wx.ALIGN_CENTER,)
        self.main_sizer.Add(wx.StaticLine(self, style=wx.LI_HORIZONTAL))
        self.main_sizer.Add(lyrics_sizer)
        self.main_sizer.Fit(self)
        self.SetSizer(self.main_sizer)

    def download_lyrics(self, event):
        self.mojim.lang = mojim_lang
        song = self.song_field.GetValue()
        artist = self.artist_field.GetValue()
        file = f'{artist} - {song}.txt'
        if self.mojim.save(artist, song):
            with open(file, 'r') as lyrics:
                self.left_editor.Clear()
                self.left_editor.write(''.join(lyrics))
            self.frame.SetStatusText(f'lyrics for {artist} - {song} saved.')
        else:
            self.frame.SetStatusText(f'unable to download lyrics for {artist} - {song}.')
        return None


class DictionaryPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        choicebook = wx.Choicebook(self)

        # ----- search field container -----
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_field = wx.SearchCtrl(self, size=(400, -1))
        self.search_field.ShowCancelButton(True)
        self.search_field.ShowSearchButton(True)
        self.search_field.Bind(wx.EVT_TEXT, self.search_corpus)
        self.words_cb = wx.CheckBox(self, label='Words')
        self.idioms_cb = wx.CheckBox(self, label='Idioms')
        self.homophones_cb = wx.CheckBox(self, label='Homophones')
        search_sizer.Add(self.search_field, 0, wx.ALL | wx.CENTER, 2)
        search_sizer.Add(self.words_cb, wx.ALL | wx.CENTER, 2)
        search_sizer.Add(self.idioms_cb, wx.ALL | wx.CENTER, 2)
        search_sizer.Add(self.homophones_cb, wx.ALL | wx.CENTER, 2)

        # self.result_list = wx.TextCtrl(
        #     self, -1, size=(640, 600), style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER
        #     )
        # self.result_list.SetEditable(False)

        choicebook = ListChoicebook(self)

        # ----- main container -----
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(search_sizer, 0, wx.ALL | wx.EXPAND, 3)
        self.main_sizer.Add(choicebook, 0, wx.ALL | wx.EXPAND, 3)
        self.main_sizer.Fit(self)
        self.main_sizer.Layout()
        self.SetSizer(self.main_sizer)

    def search_corpus(self, event):
        query = self.search_field.GetValue()
        words = self.words_cb.IsChecked()
        idioms = self.idioms_cb.IsChecked()
        homophones = self.homophones_cb.IsChecked()
        char = Character(query)
        self.result_list.Clear()
        if words:
            self.result_list.write(' '.join(char.words()) + '\n')
        if idioms:
            self.result_list.write(' '.join(char.idioms()) + '\n')
        if homophones:
            self.result_list.write(' '.join(char.homophones()) + '\n')
        return None


class ListChoicebook(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent)
        labels = ['hello', 'world', 'ahben', 'loves', 'jennifer']
        # Now make a bunch of panels for the choice book
        count = 1
        for txt in labels:
            win = self.make_subpage()
            self.AddPage(win, txt)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def make_subpage(self):
        panel = wx.Panel(self)
        list_ctrl = wx.ListCtrl(panel, size=(640, 600), style=wx.LC_REPORT)
        list_ctrl.InsertColumn(0, 'Name', width=200)
        list_ctrl.InsertColumn(1, 'Age', width=200)
        return panel

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    myframe = DictionaryPage()
    myframe.Show()
    app.MainLoop()
