import xbmc
import xbmcgui
import xbmcaddon
import os

ADDON = xbmcaddon.Addon(id="service.telerising")
ADDON_PATH = xbmc.translatePath(ADDON.getAddonInfo('profile'))
ACTION_SELECT = 7
ACTION_NAV_BACK = 92
BaseWindow = xbmcgui.WindowXMLDialog
datapath = xbmc.translatePath(ADDON.getAddonInfo('profile'))
runpath = os.path.join(datapath, "bin")
mute_notify = ADDON.getSetting('hide-osd-messages')
logfile = os.path.join(runpath, 'log.txt')
temp = os.path.join(datapath, "temp")

class textViewer(BaseWindow):
    TITLE_WINDOW_ID = 1
    TEXT_WINDOW_ID = 5

    def __init__(self, *args, **kwargs):
        self.text = None
        self.status = None
        self.title = None

    @staticmethod
    def createTextViewer():
        return textViewer('DialogTextViewer.xml', ADDON_PATH)

    def onAction(self, action):
        if (action == ACTION_NAV_BACK or action == ACTION_SELECT):
            self.close()

    def onInit(self):
        self.getControl(textViewer.TEXT_WINDOW_ID).setText(self.text)

    def close(self):
        BaseWindow.close(self)
        self.status = 'closed'

    def update(self, text):
        self.text = text
        self.title = text
        self.getControl(textViewer.TEXT_WINDOW_ID).setText(self.text)

    def settitle(self, title):
        self.title = title
        try:
            self.getControl(textViewer.TITLE_WINDOW_ID).setLabel(self.title)
        except RuntimeError as e:
            xbmc.log(str(e), xbmc.LOGERROR)

def createWindowContent(logfile):
    t_window = list()
    with open(logfile) as fo:
        lines = fo.readlines()
    if len(lines) > 10:
        lnr = range(len(lines) - 10, len(lines))
    else:
        lnr = range(0, len(lines))
    for line in lnr: t_window.append(lines[line].replace('\n', ''))
    return '[CR]'.join(t_window)

# --- START ---


tv = textViewer.createTextViewer()
mon = xbmc.Monitor()
tv.show()
tv.settitle('Telerising live Log')

while not mon.waitForAbort(1):
    if mon.abortRequested() or tv.status == 'closed': break
    tw = createWindowContent(logfile)
    tv.update(tw)

# Abort requested
xbmc.log('Abort requested')
tv.close()