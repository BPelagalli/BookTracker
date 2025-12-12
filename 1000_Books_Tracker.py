import os
import sys
import csv
import requests
from dotenv import load_dotenv
from Book_Result_Widget import BookResultWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtGui import QPixmap, QColor, QIcon, QPainter, QPainterPath
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLineEdit, QPushButton, QLabel, QTextEdit, QStackedWidget, QListWidget, QVBoxLayout, QHBoxLayout, QSizePolicy, QScrollArea, QProgressBar, QGridLayout)



# User enters book via title, author, or ISBN
# GUI - tabs for home, search, notifications, etc - seeing list of thumbnails and number of times read, dates read
# SMS reminder notifications - Twilio, Keep Twilio credentials in env files. Make sure user consent and opt-out options are present
# Save report to a CSV file - Date, Title, Author, ISBN, Pages, Rating, Notes 

# Load environment variables
load_dotenv() 

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
OPEN_LIBRARY_URL = os.getenv("OPEN_LIBRARY_URL")
OPEN_LIBRARY_SEARCH = os.getenv("OPEN_LIBRARY_SEARCH")
OPEN_LIBRARY_COVER = os.getenv("OPEN_LIBRARY_COVER")

class BookTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("1000 Books Before Kindergarten Tracker")
        self.resize(500, 700)

        # Central widget and main layout
        central = QWidget()
        main = QVBoxLayout(central)
        main.setContentsMargins(0, 0, 0, 0)

        # Header label at top of app
        self.header = QLabel("Readers", alignment=Qt.AlignLeft)
        self.header.setObjectName("header")
        main.addWidget(self.header)
        
        self.setStyleSheet("""
            QLabel#header{
                font-size:60px; 
                font-weight:bold;
                height: 100px;
                width: 500px;
                padding-top: 70px;
            }
        """)

         # Dictionary to track each reader and count
        self.readers = {
            "Bellamy": {"count": 247, "image": "/Users/brettonpelagalli/Documents/VSC Projects/Python/images/bellamy.jpeg"},
            "Marceline": {"count": 500, "image": "/Users/brettonpelagalli/Documents/VSC Projects/Python/images/marceline.jpeg"}
        }

        self.books_read = []

        # Stacked widget to hold different pages/tabs
        self.stack = QStackedWidget()
        self.stack.insertWidget(0, self.readers_page())
        #self.stack.insertWidget(1, self.library_widget)
        self.stack.addWidget(self.library_page())
        self.stack.addWidget(self.notifications_page())
        self.stack.addWidget(self.about_page())
        main.addWidget(self.stack)

        # Footer nav bar
        self.footer_container = QWidget()
        footer = QHBoxLayout(self.footer_container)
        footer.setContentsMargins(0,0,0,0)
        footer.setSpacing(12)

        self.header.setFixedHeight(120)
        self.footer_container.setFixedHeight(80)

        # Nav buttons with icons 
        self.button_names = [
            ("Readers", 0, "icons/readers.svg"),
            ("Library", 1, "icons/library.svg"), 
            ("Notifications", 2, "icons/notifications.svg"), 
            ("About", 3, "icons/about.svg")
        ]

        # Create and style nav buttons
        for names, index, icon_path in self.button_names:
            button = QPushButton()
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(32, 32))
            button.setFixedSize(60, 60)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet("""
                QPushButton{
                    border-radius:30px;
                    background-color: none;
                    border: none;
                }
                
                QPushButton:hover {
                    background-color: #ede4e4;            
                }

                QPushButton:pressed {
                    background-color: #bfb6b6;            
                }
            """)

            button.clicked.connect(lambda _, i=index: self.switch_to(i))
            footer.addWidget(button)
        
        main.addWidget(self.footer_container)
        self.setCentralWidget(central)
        
        # Background colors for each tab
        self.tab_colors = {
            0: "#487347",
            1: "#5478ab",
            2: "#cf9851",
            3: "#ab616e"
        
        }
        # Always start on Readers tab
        self.switch_to(0)

        self.search_input.returnPressed.connect(self.perform_search)

    # Creates a placeholder page with centered text
    def _page(self, text):
        window = QWidget()
        layout = QVBoxLayout(window)
        layout.addWidget(QLabel(text, alignment=Qt.AlignCenter))
        return window

    # Switches between tabs and updates header and footer
    def switch_to(self, index):
        self.stack.setCurrentIndex(index)
        self.header.setText(self.button_names[index][0])
        color = self.tab_colors.get(index,"#999da1") # fallback color
        self.header.setStyleSheet(f"""
            font-size: 30px;
            font-weight: bold;
            height: 300px;
            width: 500px;
            background-color: {color};
             """)
        self.footer_container.setStyleSheet(f"background-color: {color};")












    # Readers page which shows name, progress bar, and add button
    def readers_page(self):

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)

        for name, data in self.readers.items():
            count = data["count"]
            image_path = data["image"]

            # Container for reader
            reader_box = QWidget()
            reader_layout = QVBoxLayout(reader_box)

            # Info box holds image, labels, and progress
            info_box = QWidget()
            info_layout = QVBoxLayout(info_box)
            info_layout.setSpacing(8)


            # Profile picture
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                size = 64
                pixmap = pixmap.scaled(size, size, Qt. KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                mask = QPixmap(size,size)
                mask.fill(Qt.transparent)

                rounded = QPixmap(size, size)
                rounded.fill(Qt.transparent)

                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)

                path = QPainterPath()
                path.addEllipse(0, 0, size, size)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
            
                image_label.setPixmap(rounded)

            else:
                image_label.setText("No Image")
            image_label.setFixedSize(64, 64)
            info_layout.addWidget(image_label)

            # Reader name
            name_label = QLabel(f"{name}")
            name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
            info_layout.addWidget(name_label)

            # Progress text
            progress_label = QLabel(f"{count}/1000 books read")
            info_layout.addWidget(progress_label)

            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setFixedHeight(20)
            progress_bar.setMaximum(1000)
            progress_bar.setValue(count)
            progress_bar.setTextVisible(False)
            progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #d2d4d3;
                    border-radius: 10px;
                }
                QProgressBar::chunk {
                    background-color: #487347;
                    border-radius: 10px;                    
                }     
            """)
            info_layout.addWidget(progress_bar)

            # Add book and book list buttons
            buttons_box = QWidget()
            buttons_layout = QHBoxLayout(buttons_box)
            buttons_layout.setSpacing(10)
            buttons_layout.setContentsMargins(0, 0, 0, 0)

            add_button = QPushButton("Finished A Book")
            add_button.setCursor(Qt.PointingHandCursor) 
            add_button.setStyleSheet("""
                QPushButton {
                    background-color: #487347;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(72, 115, 71, 0.9);           
                }
            """)
            add_button.clicked.connect(lambda _, r=name: self.add_books(r))
            buttons_layout.addWidget(add_button)

            book_list_button = QPushButton("Book List")
            book_list_button.setCursor(Qt.PointingHandCursor)
            book_list_button.setStyleSheet("""
                QPushButton {
                    background-color: white ;
                    color: #487347;
                    padding: 6px 12px;
                    border-radius: 14px;
                }
                QPushButton:hover {
                    background-color: #487347;
                    color: white;            
                }
            """)

            book_list_button.clicked.connect(lambda _, r=name: self.show_book_list(r))
            buttons_layout.addWidget(book_list_button)

            info_layout.addWidget(buttons_box)



            # Add info box to reader layout
            reader_layout.addWidget(info_box)

            # Add reader box to main layout
            layout.addWidget(reader_box)

        scroll_area.setWidget(content_widget)
        return scroll_area
    
    # Increases book count for reader and refreshes page
    def add_books(self, reader_name):
        self.current_reader = reader_name # Stores which child is active
        if not hasattr(self, "library_widget"):
            self.library_widget = self.library_page()
            self.stack.addWidget(self.library_widget)
        self.switch_to(self.stack.indexOf(self.library_widget))
        

    
    def library_page(self):
        self.library_widget = QWidget()
        main_layout = QVBoxLayout(self.library_widget)
        self.library_widget.setLayout(main_layout)

        # Horizontal row for search bar and button
        search_row = QWidget()
        search_layout = QHBoxLayout(search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(0)

        # Search bar and button
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, author, or ISBN")
        self.search_input.setStyleSheet("""
            font: 14px;
            height: 30px; 
            border-top-left-radius: 15px;
            border-bottom-left-radius: 15px;
            padding: 2px 15px;
        """)
        search_layout.addWidget(self.search_input)

        search_button = QPushButton("Search")
        search_button.setCursor(Qt.PointingHandCursor)
        search_button.setStyleSheet("""
            QPushButton{ 
                font: 14px;                       
                height: 30px;
                border-top-right-radius: 15px;
                border-bottom-right-radius: 15px;
                background-color: #5478ab;  
                padding: 2px 10px; 
                                   
            }
            QPushButton:hover{
                background-color: rgba(84, 120, 171, 0.9);                
            }
            QPushButton:pressed{
                background-color: rgba(84, 120, 171, 0.7);                     
            }
        """)
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(search_button)

        main_layout.addWidget(search_row, 0)

        # Scrollable results area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        results_container = QWidget()
        self.results_area = QVBoxLayout(results_container)
        results_container.setLayout(self.results_area)

        scroll_area.setWidget(results_container)

        main_layout.addWidget(scroll_area, 1)

        return self.library_widget
    
    def perform_search(self):
        query = self.search_input.text().strip().lower()
        if not query:
            return
        
        # Clear existing results
        while self.results_area.count():
            item = self.results_area.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        
        # Show loading message
        loading_label = QLabel("Loading results...")
        loading_label.setAlignment(Qt.AlignCenter)
        self.results_area.addWidget(loading_label)
        QApplication.processEvents()

        # Create network manager
        if not hasattr(self, 'network_manager'):
            self.network_manager = QNetworkAccessManager()
            
        try:
            url = f"{OPEN_LIBRARY_SEARCH}?q={requests.utils.quote(query)}&limit=20"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Remove loading message
            self.results_area.removeWidget(loading_label) 
            loading_label.deleteLater()

            docs = data.get("docs, []")
        
        for doc in data.get("docs", []):
            title = doc.get("title", "").lower()
            authors = [a.lower() for a in doc.get("author_name", [])]
            isbn_list = [i.lower() for i in doc.get ("isbn", [])]

            # Exact isbn match first
            if query in isbn_list:
                isbn_matches.append(doc)
            elif query in title or any (query in a for a in authors):
                filtered_results.append(doc)

        final_results = isbn_matches + filtered_results


        # Limit to 20 results
        for doc in final_results [:20]:
            title = doc.get("title", "Unknown Title")
            authors = ", ".join(doc.get("author_name", []))
            isbn = doc.get("isbn", [None])[0] if doc.get("isbn") else None
            cover_id = doc.get("cover_i")
            thumbnail = f"{OPEN_LIBRARY_COVER}/{cover_id}-M.jpg" if cover_id else None

            book = {
                "title": title,
                "author": authors,
                "isbn": isbn,
                "thumbnail": thumbnail
            }

            book_widget = BookResultWidget(book, self.add_book_to_reader)
            self.results_area.addWidget(book_widget)
        
            
    def add_book_to_reader(self, book):
        reader_name = self.current_reader
        self.readers[reader_name]["count"] += 1
    
        book_entry = {
            "title": book["title"],
            "author": book["author"],
            "isbn": book["isbn"],
            "reader": reader_name,
            "count": 1
        }

        self.books_read.append(book_entry)
        self.save_book_to_csv(book_entry)

        # Refresh readers page
        self.stack.removeWidget(self.readers_page_widget)
        self.readers_page_widget = self.readers_page()
        self.stack.insertWidget(0, self.readers_page_widget)
        self.switch_to(0)

    def book_list_page(self, reader_name):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        content = QWidget()
        grid = QGridLayout(content)

        # Filter books for this reader
        books = [b for b in self.books_read if b["reader"] == reader_name]

        for i, book in enumerate(books):
            # Thumbnail (placeholder for now)
            thumb = QLabel()
            thumb.setFixedSize(80, 120)
            thumb.setStyleSheet("background-color: #d2d4d3; border-radius: 6px;")
            thumb.setText(book["title"]) # replace with cover image later
            thumb.setWordWrap(True)
            
            grid.addWidget(thumb,i // 4, i % 4) # 4 per row

        content.setLayout(grid)
        scroll_area.setWidget(content)
        layout.addWidget(scroll_area)

        return widget
    
    def show_book_list(self, reader_name):
        self.stack.addWidget(self.book_list_page(reader_name))
        self.switch_to(self.stack.count() - 1)

    def save_book_to_csv(self,book):
        with open("books_read.csv", "a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["title", "author", "isbn", "reader", "count"])
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(book)



















    # Notifications page which shows SMS information and opt-out toggle
    def notifications_page(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)

        # Header
        title = QLabel("Summary")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Subscription Status
        subscribed_label = QLabel("✅ You're subscribed to daily reminders")
        subscribed_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(subscribed_label)

        # Recipients
        recipients = os.getenv("RECIPIENT_PHONE_NUMBER",     "")
        recipients_label = QLabel(f"📱 Messages are being sent to: {recipients}")
        recipients_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(recipients_label)

        # Reminder count
        reminder_count = 23
        count_label = QLabel(f"You've received {reminder_count} reminders this month")
        count_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(count_label)

        # Next reminder time
        next_reminder_label = QLabel("⏰ Next reminder: Today at 8:00PM")
        next_reminder_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(next_reminder_label)

        # Opt-out toggle
        opt_out_label = QLabel("🔕 SMS Notifications")
        opt_out_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(opt_out_label)

        self.opt_out_toggle = QPushButton("Opt-Out")
        self.opt_out_toggle.setCheckable(True)
        self.opt_out_toggle.setCursor(Qt.PointingHandCursor)
        self.opt_out_toggle.setStyleSheet("""
            QPushButton{
                background-color: #cf9851;
                color: white;
                padding: 8px;
                border-radius: 16px;                            
            }                                 
            QPushButton:checked {
                background-color: #999da1;
            }
        """)
        self.opt_out_toggle.setChecked(False)
        layout.addWidget(self.opt_out_toggle)

        scroll_area.setWidget(content_widget)
        return scroll_area

        
        # Notifications summary
        # You're subscribed to daily reminders
        # Messages being sent to: +17015705206, +14068531398
        # You've received 23 reminders this month
        # Next reminder: Today at 8pm
        # Opt out toggle

    # About page which shows app goal
    def about_page(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Add content to the About page
        logo_path = "/Users/brettonpelagalli/Documents/VSC Projects/Python/images/logo.png"
        pixmap = QPixmap(logo_path)
        logo_label = QLabel()
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(200, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
        else:
            logo_label.setText("Logo not found")
        logo_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(logo_label)

        title = QLabel("Program Overview")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        paragraph = QLabel("The concept is simple, the rewards are priceless. Read a book (any book) to your newborn infant, and/or toddler. The goal is to have read 1,000 books (yes you can repeat books) before your little one starts kindergarten. Does it sound hard? Not really, if you think about it. If you read just one (1) book a night, you will have read about three hundred sixty-five (365) books in a year. That is seven hundred thirty (730) books in two years and one thousand ninety-five (1,095) books in three years. If you consider that most children start kindergarten at around five (5) years of age, you have more time than you think!")
        paragraph.setWordWrap(True)
        paragraph.setAlignment(Qt.AlignTop)
        paragraph.setStyleSheet("font-size: 15px; line-height: 20px; padding-bottom: 20px")

        title_2 = QLabel("How To Participate")
        title_2.setAlignment(Qt.AlignLeft)
        title_2.setStyleSheet("font-size: 18px; font-weight: bold;")

        paragraph_2 = QLabel("Read with your child. Studies have shown that reading with your child provides a great opportunity for bonding. Reading together is fun and will create life-long memories for the both of you.\n\n"
                             
        "Use this app to keep track of the titles of the books that you read with your child. If you are able to, make sure to keep a record of any book that is being read to your child.\n\n"

        "For additional information, visit: 1000BooksBeforeKindergarten.Org")
        paragraph_2.setStyleSheet("font-size: 15px;")
        paragraph_2.setWordWrap(True)
        paragraph_2.setAlignment(Qt.AlignTop)
       
        content_layout.addWidget(logo_label)
        content_layout.addWidget(title)
        content_layout.addWidget(paragraph)
        content_layout.addWidget(title_2)
        content_layout.addWidget(paragraph_2)

        scroll_area.setWidget(content_widget)
        return scroll_area

# Run app if running code directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookTracker()
    window.show()
    sys.exit(app.exec_())