import wx
import wx.adv
from gui import MainGUI


class LyricsApp(wx.App):
    """Custom app class"""

    def OnInit(self):
        self.frame = MainGUI(None, title='Canto Lyrics Helper')
        self.frame.Show()
        return True


if __name__ == '__main__':
    app = LyricsApp()
    app.MainLoop()