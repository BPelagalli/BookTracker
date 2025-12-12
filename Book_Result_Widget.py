import requests
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtWidgets import (QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy, )


class BookResultWidget(QWidget):
    def __init__(self, book, add_callback, network_manager):
        super().__init__()
        self.book = book
        self.add_callback = add_callback
        self.network_manager = network_manager
        self.replies = []
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(10)

        # Thumbnail
        self.thumb_label = QLabel()
        self.thumb_label.setFixedSize(60, 90)
        layout.addWidget(self.thumb_label)

        if self.book["thumbnail"]:
            url = self.book["thumbnail"]
            request = QNetworkRequest(QUrl(url))
            reply = self.network_manager.get(request)
            self.replies.append(reply)
            reply.finished.connect(lambda: self.handle_image_reply(reply)) 
        else:
            self.thumb_label.setText("No Cover")
            self.thumb_label.setStyleSheet("background-color: #d2d4d3; border-radius: 6px;")

        # Title and Author
        text_box = QWidget()
        text_box.setMaximumWidth(200)
        text_layout = QVBoxLayout(text_box)
        title_label = QLabel(self.book["title"])
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        author_label = QLabel(self.book["author"])
        author_label.setStyleSheet("font-size: 12px; color: gray;")
        text_layout.addWidget(title_label)
        text_layout.addWidget(author_label)
        layout.addWidget(text_box, 2)
    
        # + Read button 
        read_button = QPushButton("+Read")
        read_button.setCursor(Qt.PointingHandCursor)
        read_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        read_button.setStyleSheet("""
            QPushButton{
                background-color: #5478ab;
                color: white;
                padding: 2px 10px 2px;
                border-radius: 10px; 
                border: none;               
            }               
            QPushButton:hover{
                background-color: rgba(84, 120, 171, 0.9);                   
            }
        """)
        read_button.clicked.connect(lambda: self.add_callback(self.book))
        layout.addWidget(read_button) 
            
    def handle_image_reply(self, reply):
        if reply.error() == reply.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            self.thumb_label.setPixmap(pixmap.scaled(60, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.thumb_label.setText("No Cover")
            self.thumb_label.setStyleSheet("background-color: #d2d4d3; border-radius: 6px;")
        reply.deleteLater()
                
            

            






        

