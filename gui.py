import os
import sys
import wx
import wx.aui as aui
from cantolyrics import Corpus, Mojim

CORPUS = Corpus()

class MainGUI(wx.Frame):
    def __init__(self, parent, title, size=(640, 800)):
        super().__init__(
            parent, title=title, size=size,
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
            )
        self.CenterOnScreen()
        self.notebook = aui.AuiNotebook(self)

        # ----- add main page -----
        page1 = LyricsPage(self)
        self.notebook.AddPage(page1, 'Lyrics')

        # ----- add dictionary page -----
        page2 = DictionaryPage(self)
        self.notebook.AddPage(page2, 'Dictionary')

        # ----- main contianer -----
        main_sizer = wx.BoxSizer(wx.VERTICAL)
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
 
        menu4 = wx.Menu()
        menu4.Append(401, 'Lyrics')
        menu4.Append(402, 'Dictionary')

        help_menu = wx.Menu()
        about = help_menu.Append(wx.ID_ABOUT)

        self.Bind(wx.EVT_MENU, self.file_dialog, id=101)
        self.Bind(wx.EVT_MENU, self.file_dialog, id=102)
        self.Bind(wx.EVT_MENU, self.save_dialog, id=103)
        self.Bind(wx.EVT_MENU, self.save_dialog, id=104)
        self.Bind(wx.EVT_MENU, self.exit_program, id=105)
        self.Bind(wx.EVT_MENU, self.append_page, id=401)
        self.Bind(wx.EVT_MENU, self.append_page, id=402)
        self.Bind(wx.EVT_MENU, self.about_dialog, about)

        self.Append(menu1, 'File')
        self.Append(menu4, 'Pages')
        self.Append(help_menu, 'Help')

    def file_dialog(self, event):
        try:        
            page = self.frame.notebook.GetCurrentPage()
            editor = page.left_editor if event.GetId() == 101 else page.right_editor
        except AttributeError:
            return None

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
        try:
            page = self.frame.notebook.GetCurrentPage()
            editor = page.left_editor if event.GetId() == 103 else page.right_editor
        except AttributeError:
            return None

        wildcards = 'Text file (*.txt)|*.txt|' \
                'Lyrics file (*.lyrics)|*.lyrics|' \
                'All files (*.*)|*.*'

        with wx.FileDialog(
            self, 
            message='Save lyrics as ...', 
            defaultDir=os.getcwd(),
            defaultFile='', 
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

    def append_page(self, event):
        page = LyricsPage(self.frame) if event.GetId() == 401 else DictionaryPage(self.frame)
        label = 'Lyrics' if event.GetId() == 401 else 'Dictionary'
        self.frame.notebook.AddPage(page, label)
        return None
                                            
    def about_dialog(self, event):
        info = wx.adv.AboutDialogInfo()
        info.Name = 'Canto Lyrics Helper'
        info.Version = 'Alpha v0.0.8'
        info.Copyright = '(c) 2019 Wenbin Wu\n' 
        info.Description = '' + \
            'Email: dev@wuwenb.in\n' + \
            'Github: https://github.com/wenbinwu85/'     
        wx.adv.AboutBox(info)
        return None


class LyricsPage(wx.Panel):
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
        download_sizer.Add(song_label, 0, wx.ALL | wx.CENTER, 2)
        download_sizer.Add(self.song_field, 0, wx.ALL | wx.CENTER, 2)
        download_sizer.Add(artist_label, 0, wx.ALL | wx.CENTER, 2)
        download_sizer.Add(self.artist_field, 0, wx.ALL | wx.CENTER, 2)
        download_sizer.Add(download_button, 0, wx.ALL | wx.CENTER, 2)

        # ----- editor container -----
        lyrics_sizer = wx.BoxSizer(wx.HORIZONTAL)
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
        self.main_sizer.Add(lyrics_sizer, 0, wx.ALL | wx.EXPAND)
        self.main_sizer.Add(download_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        self.main_sizer.Fit(self)
        self.SetSizer(self.main_sizer)

    def download_lyrics(self, event):
        song = self.song_field.GetValue()
        artist = self.artist_field.GetValue()
        lyrics = self.mojim.save(artist, song)
        if not lyrics:
            self.frame.SetStatusText(f'unable to download lyrics for {artist} - {song}.')
            return None
        self.left_editor.Clear()
        self.left_editor.write(lyrics)
        self.frame.SetStatusText(f'lyrics for {artist} - {song} saved.')
        return None


class DictionaryPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.choicebook = ListChoicebook(self)

        # ----- search field container -----
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_field = wx.SearchCtrl(self, size=(500, -1), style=wx.TE_PROCESS_ENTER)
        self.search_field.ShowCancelButton(True)
        self.search_field.ShowSearchButton(True)
        self.recent_menu = self.make_menu()
        self.search_field.SetMenu(self.recent_menu)
        self.search_field.Bind(wx.EVT_TEXT, self.search_corpus)
        self.idioms_cb = wx.CheckBox(self, label='Idioms')
        search_sizer.Add(self.search_field, 0, wx.ALL | wx.CENTER, 2)
        search_sizer.Add(self.idioms_cb, wx.ALL | wx.CENTER, 2)

        # ----- main container -----
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(search_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 2)
        self.main_sizer.Add(self.choicebook, 0, wx.ALL | wx.EXPAND, 2)
        self.main_sizer.Fit(self)
        self.main_sizer.Layout()
        self.SetSizer(self.main_sizer)

    def search_corpus(self, event):
        query = self.search_field.GetValue()
        
        if not query:
            return None
        include_idioms = self.idioms_cb.IsChecked()
        words = CORPUS.search(query)
        if include_idioms:
            idioms = CORPUS.search_idioms(query)
        
        for w in words:
            page_index = len(w)-2
            page = self.choicebook.GetPage(page_index)
            list_ctrl = page.GetChildren()[0]
            item_index = list_ctrl.GetItemCount()
            list_ctrl.InsertItem(item_index, w)
        return None

    def make_menu(self):
        queries = ['hello', 'world', 'hahaha']
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)
        for q in queries:
            menu.Append(-1, q)
        return menu


class ListChoicebook(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent)
        labels = ['Two', 'Three', 'Four', 'Five+', 'Idioms']
        for text in labels:
            subpage = self.make_subpage()
            self.AddPage(subpage, text)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.page_change)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.page_change)

    def make_subpage(self):
        panel = wx.Panel(self)
        list_ctrl = wx.ListCtrl(panel, size=(640, 600), style=wx.LC_REPORT)
        list_ctrl.InsertColumn(0, 'Results', width=640)
        return panel

    def page_change(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        event.Skip()


if __name__ == '__main__':
    app = wx.App()
    myframe = DictionaryPage()
    myframe.Show()
    app.MainLoop()
