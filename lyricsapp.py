import wx
import wx.adv
from gui import LyricsGUI


class LyricsApp(wx.App):
    """Custom app class"""

    def OnInit(self):
        self.frame = LyricsGUI(None, title='Lyrics Helper')
        self.frame.Show()
        return True


if __name__ == '__main__':
    app = LyricsApp()
    app.MainLoop()