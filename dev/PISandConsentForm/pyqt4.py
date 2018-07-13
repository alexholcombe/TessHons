from PyQt4.QtWebKit import QWebView
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl
import sys
import os

app = QApplication(sys.argv)

browser = QWebView()
file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "aa.html"))
local_url = QUrl.fromLocalFile(file_path)
browser.load(local_url)

browser.show()

from psychopy import event
while not event.getKeys():
    pass

