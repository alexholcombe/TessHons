#https://stackoverflow.com/questions/13384749/how-to-display-html-using-qwebview-python#13386109
import sys
sys.path.append("/Applications/PsychoPy2_1.90.2.app/Contents/Resources/lib/python2.7")
#import psychopy
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebView


class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.loadFinished.connect(self._result_available)

    def _result_available(self, ok):
        frame = self.page().mainFrame()
        #print unicode(frame.toHtml()).encode('utf-8')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = Browser()
    view.load(QUrl('http://www.example.com'))
    app.exec_()