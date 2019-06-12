import wx
import wx.lib.intctrl
import wx.lib.mixins.listctrl as listmixins
from cantolyrics import Character, Word, Mojim

class MyGUI(wx.Frame, listmixins.ColumnSorterMixin):
    def __init__(self, parent, title, size=(600, 800)):
        wx.Frame.__init__(
            self, parent, title=title, size=size,
            style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
            )
        self.CenterOnScreen()
        self.panel = wx.Panel(self)

        # if wx.Platform == '__WXMSW__':
        #     self.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'courier'))
        # else:
        #     self.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Monaco'))

        # ----- search field container -----
        download_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self.panel, label='下载歌词')
        song_label = wx.StaticText(self.panel, label=' 歌名:', size=(50, -1))
        self.song_field = wx.TextCtrl(self.panel, size=(200, -1))
        artist_label = wx.StaticText(self.panel, label=' 歌手:', size=(50, -1))
        self.artist_field = wx.TextCtrl(self.panel, size=(140, -1))
        search_button = wx.Button(self.panel, label='下载')
        search_button.Bind(wx.EVT_BUTTON, self.search_mojim)
        download_sizer.Add(song_label, 0, wx.ALL | wx.EXPAND, 2)
        download_sizer.Add(self.song_field, 0, wx.ALL | wx.EXPAND, 2)
        download_sizer.Add(artist_label, 0, wx.ALL | wx.EXPAND, 2)
        download_sizer.Add(self.artist_field, 0, wx.ALL | wx.EXPAND, 2)
        download_sizer.Add(search_button, 0, wx.ALL | wx.EXPAND, 2)

        # ----- editor container -----
        self.lyrics_sizer = wx.StaticBoxSizer(wx.HORIZONTAL, self.panel, label='歌词')
        self.lyrics_original = wx.TextCtrl(self.panel, -1, size=(300, 600), 
                       style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        self.lyrics_new = wx.TextCtrl(self.panel, -1, size=(300, 600), 
                       style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
        # self.lyrics_original.SetEditable(True)
        self.lyrics_sizer.Add(self.lyrics_original, 0, wx.ALL)
        self.lyrics_sizer.Add(self.lyrics_new, 0, wx.ALL)

        # ----- buttons -----
        buttons_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_button = wx.Button(self.panel, label='保存', style=wx.ALIGN_RIGHT)
        save_button.Bind(wx.EVT_BUTTON, self.save_lyrics)
        buttons_sizer.Add(save_button, 0, wx.ALL)

        # ----- main container -----
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(download_sizer, 0, wx.ALL | wx.EXPAND, 2)
        self.main_sizer.Add(self.lyrics_sizer, 0, wx.ALL | wx.EXPAND, 2)
        self.main_sizer.Add(buttons_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
        self.main_sizer.Fit(self.panel)
        self.panel.SetSizer(self.main_sizer)

        # ----- status bar -----
        self.CreateStatusBar()
        self.SetStatusText('你好.')

    def search_mojim(self, event):
        song = self.song_field.GetValue()
        artist = self.artist_field.GetValue()
        mojim = Mojim()
        mojim.artist = artist
        if mojim.save(song):
            self.SetStatusText(f'{mojim.artist} - {song} 歌词已保存.')
            with open(f'{mojim.artist} - {song}.txt', 'r') as lyrics:
                self.lyrics_original.write(''.join(lyrics))
        else:
            self.SetStatusText(f'找不到 {song} 的歌詞')

    def save_lyrics(self, event):
        with open('new_lyrics.txt', 'w', encoding='utf-8') as fout:
            lyrics = self.lyrics_new.GetValue()
            fout.write(lyrics)


if __name__ == '__main__':
    app = wx.App()
    myframe = MyGUI(None, '歌词助手')
    myframe.Show()
    app.MainLoop()