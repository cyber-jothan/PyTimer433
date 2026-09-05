import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtMultimedia import *
import serial
import os

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile("C:\\Users\\Admin\\Desktop\\TIMER433\\CARTING\\PyCarting\\sound_beep.wav"))
        self.sound.setVolume(0.5)
        
        self.setWindowTitle("ПУЛЬТ для картинга  by Jothan Cyber")
        self.showFullScreen()

        class OverflowGrid(QGridLayout):
            """Размещение элементов в виде сетки, с автоматическим
            смещением элементов в следующий ряд при добавлении
            и удалении (с максимальнsм количеством элементов)
            в ряде) а"""
            
            widget_added = pyqtSignal(QWidget)
            widget_removed = pyqtSignal(QWidget)
            
            def __init__(self, max_columns=8):
                super().__init__()
                self.setSpacing(5)
                self.max_columns = max_columns
                self._widgets = []
                
            def add_widget(self, widget):
                self._widgets.append(widget)
                self._reflow()
                self.widget_added.emit(widget)
                
            def remove_widget(self, widget):
                if widget in self._widgets:
                    self._widgets.remove(widget)
                    widget.setParent(None)
                    self._reflow()
                    self.widget_removed.emit(widget)
                    
            def _reflow(self):
                while self.count():
                    child = self.takeAt(0)
                    if child.widget():
                        child.widget().setParent(None) 
                for idx, widget in enumerate(self._widgets):
                    row = idx // self.max_columns
                    col = idx % self.max_columns
                    self.addWidget(widget, row, col, alignment=Qt.AlignmentFlag.AlignLeft)
        
        
        class PropertyButton(QPushButton):
            def __init__(
                self,
                cart_text:str,
                cart_number:int,
                cart_name:str,
                cart_code:str,
                cart_timing:str):
                
                super().__init__(cart_text)
                
                self.cart_number = cart_number
                self.cart_name = cart_name
                self.cart_code = cart_code
                self.cart_timing = cart_timing

        class SplitButton(QFrame):
            def __init__(self,
                        cart_number:int,
                        cart_name:str,
                        cart_code:str,
                        cart_timing:str,
                        current_area = "park",
                        button_size = 70,
                        label_top = "Button",
                        label_left = "《《《",
                        label_right = "》》》"):
 
                super().__init__()
                # Принадлежность определенной машины к кнопке ------ #
                self.cart_number = cart_number
                self.cart_name = cart_name
                self.cart_code = cart_code
                self.cart_timing = cart_timing
                self.current_area = current_area
                # ------- #
                
                self.setFrameStyle(QFrame.Shape.Box)
                self.setLineWidth(3)
                self.setFixedWidth(button_size)
                self.setFixedHeight(int(button_size*1.25))
                
                
                layout = QVBoxLayout(self)
                layout.setContentsMargins(0,0,0,0)
                layout.setSpacing(0)
                
                self.button_top = QPushButton(label_top)
                self.button_top.setFixedHeight(int(button_size*0.75))
                self.button_top.setContentsMargins(0,0,0,0)
                layout.addWidget(self.button_top)
                
                row_bottom = QHBoxLayout()
                row_bottom.setContentsMargins(0,0,0,0)
                row_bottom.setSpacing(0)
                
                self.button_left = QPushButton(label_left)
                self.button_left.setFixedHeight(int(button_size*0.45))
                self.button_right = QPushButton(label_right)
                self.button_right.setFixedHeight(int(button_size*0.45))
                
                row_bottom.addWidget(self.button_left)
                row_bottom.addWidget(self.button_right)
                
                layout.addLayout(row_bottom)
                
                style = """
                    QPushButton {
                        border: 0px solid #888;
                        border-radius: 0px;
                        padding: 0px 0px;
                    }
                """
                style_top = """
                    QPushButton {
                        font-size: 23px;
                    }
                """
                style_self = """
                    QWidget {
                        border-radius: 4px;
                    }
                """
                
                self.button_top.setStyleSheet(style)
                self.button_top.setStyleSheet(style_top)
                self.button_left.setStyleSheet(style)
                self.button_right.setStyleSheet(style)
                self.setStyleSheet(style_self)

        # ПОСТОЯННЫЕ ЗНАЧЕНИЯ
        number_of_carts = 45
        dict_code = {
        "1д": "111110101000111101101000",
        "1": "110111111000100000001000",
        "2д": "110100001100010100101000",
        "2": "000110110110100100101000",
        "3д": "011100100111010100101000",
        "3": "101010011111000010001000",
        "4д": "001000010001001000001000",
        "4": "000110000001110101101000",
        "5д": "011101011010100010001000",
        "5": "000000010000100010001000",
        "6д": "000000111011010101101000",
        "6": "100001110100110000001000",
        "7д": "100000101111111000101000",
        "7": "001100011100101100101000",
        "8д": "100111010001000100101000",
        "8": "100001000000110000001000",
        "9д": "101111010000010100101000",
        "9": "011001110001000100101000",
        "10д": "110110110001000000101000",
        "10": "100000100111011111101000",
        "11": "010101011000010100101000",
        "11д": "100011111001010101101000",
        "12": "110100111001001000001000",
        "12д": "001000010010001100101000",
        "13": "101101011010110000001000",
        "13д": "000111001001001100101000",
        "14": "010000111001101101101000",
        "14д": "101001001101110100101000",
        "15": "011010100000010100101000",
        "15д": "101010101110001011101000",
        "16": "001000010100010100101000",
        "17": "100011010111110101101000",
        "18": "111001101000110100101000",
        "19": "001011000001100101101000",
        "20": "001011001101111111101000",
        "21": "111010011110000000001000",
        "22": "001000110011010100101000",
        "23": "001001110100101100101000",
        "24": "101011101101100101101000",
        "25": "011101101000000010001000",
        "26": "100001110011010100101000",
        "27": "001111001110000000101000",
        "28": "100111110100001100101000",
        "29": "101010010011110100101000",
        "30": "111010111110100000001000"
        }
        dict_timing = {
        "1д": "346",
        "1": "376",
        "2д": "364",
        "2": "363",
        "3д": "370",
        "3": "373",
        "4д": "376",
        "4": "341",
        "5д": "368",
        "5": "378",
        "6д": "350",
        "6": "380",
        "7д": "365",
        "7": "364",
        "8д": "366",
        "8": "362",
        "9д": "368",
        "9": "367",
        "10д": "372",
        "10": "368",
        "11": "370",
        "11д": "346",
        "12": "371",
        "12д": "362",
        "13": "375",
        "13д": "361",
        "14": "352",
        "14д": "373",
        "15": "367",
        "15д": "348",
        "16": "365",
        "17": "342",
        "18": "366",
        "19": "348",
        "20": "366",
        "21": "362",
        "22": "373",
        "23": "366",
        "24": "366",
        "25": "372",
        "26": "372",
        "27": "364",
        "28": "369",
        "29": "360",
        "30": "373"
        }
        
        svetofor__code_green = "111101010101111111010010"
        svetofor__code_red =   "111101010101111111010001"
        svetofor__code_off =   "111101010101111111010011"
        svetofor__timing =     "290"
        
        
        # ФУНКЦИОНАЛ ОТПРАВКИ СООБЩЕНИЙ НА USB-ПОРТ д ARDUINO
        PORT = "COM5"
        BAUD = 9600 
        ser = serial.Serial(PORT, BAUD, timeout=1)
        
        
            
            
        def on(current_cart):
            code = f"{current_cart.cart_code}:{current_cart.cart_timing}\n"
            ser.write(code.encode('utf-8'))
            print("launched ", current_cart.cart_name)
            self.sound.play()
            
        def transfer_layout(current_cart, layout_from: OverflowGrid, layout_to: OverflowGrid, new_area):
            layout_from.remove_widget(current_cart)
            layout_to.add_widget(current_cart)
            current_cart.current_area = new_area
            
        def launch_race_carts(button_cart_list, button_launch):
            # Выключить кнопку, пока машины запускаются
            try:
                button_launch.clicked.disconnect()
            except TypeError:
                pass
            delay = 0
            i = 0
            for current_cart in button_cart_list:
                if current_cart.current_area == "race":
                    add = 600
                    delay = 600 + i*600
                    i += 1
                    QTimer.singleShot(
                        delay, 
                        lambda cart=current_cart:
                            on(cart))
            print("delay: ", delay)
                    
            print('activated')
            QTimer.singleShot(
                delay, 
                lambda button = button_launch:
                            button.clicked.connect(
                                lambda checked=False,
                                cart_list=button_cart_list,
                                button = button_launch:
                                    launch_race_carts(cart_list, button)))
                
        def reset(button_cart_list, grid_from: OverflowGrid, grid_to: OverflowGrid):
            for cart in button_cart_list:
                if cart.current_area == "race":
                    transfer_layout(cart, grid_from, grid_to, "park")
                    
        def detskiy(button_cart_list, grid_from: OverflowGrid, grid_to: OverflowGrid):
            reset(button_cart_list, grid_from, grid_to)
            for cart in button_cart_list:
                if cart.cart_name.endswith("д"):
                    transfer_layout(cart, grid_to, grid_from, "race")
                    
        def vzrosliy(button_cart_list, grid_from: OverflowGrid, grid_to: OverflowGrid):
            reset(button_cart_list, grid_from, grid_to)
            for cart in button_cart_list:
                if not cart.cart_name.endswith("д"):
                    transfer_layout(cart, grid_to, grid_from, "race")
        
                
                
        
        # Добавление планировки окна

        layout__main = QVBoxLayout()
        
        
        layout__row_labels = QVBoxLayout()
        layout__column_empty_left = QVBoxLayout()
        layout__grid_carts_park = OverflowGrid()
        layout__column_empty_middle = QVBoxLayout()
        layout__grid_carts_race = OverflowGrid()
        layout__row_svetofor = QHBoxLayout()
        layout__column_empty_right = QVBoxLayout()


        label_park = QLabel("""
        Экран не сенсорный, управление мышкой!
        Парковка 》》》 Трасса
        Парковка 《《《 Трасса
        Кнопка запуска включает все машины на трассе；если сигнал не прошёл, можно запустить эти машины по отдельности""")
        label_park.setContentsMargins(0,0,0,0)
        label_park.setFixedHeight(100)

        # layout__row_labels.addWidget(label_park)
        
        layout__main.addLayout(layout__row_labels)

        layout__main.addLayout(layout__column_empty_left)
        
        # Добавление кнопок для включения машин и светофора ------------------- #
        button_cart_list = []
        cart_name_list = list(dict_code.keys()) 
        cart_code_list = list(dict_code.values())
        cart_timing_list = list(dict_timing.values())

        
        # Инициализация машин #
        for i in range(number_of_carts):
            button_cart = SplitButton(
                i+1, 
                cart_name_list[i], 
                cart_code_list[i], 
                cart_timing_list[i],
                current_area = "park", 
                label_top = cart_name_list[i])
            
            button_cart.button_top.clicked.connect(
                lambda checked=False,
                cart=button_cart:
                    on(cart))
            
            button_cart.button_right.clicked.connect(
                lambda checked=False,
                cart=button_cart:
                    transfer_layout(
                        cart,
                        layout__grid_carts_park,
                        layout__grid_carts_race,
                        new_area = "race"))
            
            button_cart.button_left.clicked.connect(
                lambda checked=False, 
                cart=button_cart:
                    transfer_layout(
                        cart,
                        layout__grid_carts_race,
                        layout__grid_carts_park,
                        new_area = "park"))
            
            button_cart_list.append(button_cart)
            layout__grid_carts_park.add_widget(button_cart)
            
        

        # СВЕТОФОР

        svetofor__button_green = PropertyButton(
            "ЗЕЛ", 0, "ЗЕЛ", 
            svetofor__code_green, 
            svetofor__timing)
        svetofor__button_red = PropertyButton(
            "КРАС", 0, "КРАС", 
            svetofor__code_red, 
            svetofor__timing)
        svetofor__button_off = PropertyButton(
            "выкл", 0, "выкл", 
            svetofor__code_off, 
            svetofor__timing)

        svetofor__button_width = 180
        svetofor__button_height = 90

        svetofor__button_green.setFixedWidth(svetofor__button_width)
        svetofor__button_red.setFixedWidth(svetofor__button_width)
        svetofor__button_off.setFixedWidth(svetofor__button_width)
        svetofor__button_green.setFixedHeight(svetofor__button_height)
        svetofor__button_red.setFixedHeight(svetofor__button_height)
        svetofor__button_off.setFixedHeight(svetofor__button_height)
        
        button_cart.button_top.clicked.connect(
            lambda checked=False, cart=button_cart: on(cart)
        )

        svetofor__button_green.clicked.connect(
            lambda checked=False, cart=svetofor__button_green: on(cart)
        )
        svetofor__button_red.clicked.connect(
            lambda checked=False, cart=svetofor__button_red: on(cart)
        )
        svetofor__button_off.clicked.connect(
            lambda checked=False, cart=svetofor__button_off: on(cart)
        )
        
        #
        button__launch_race_carts = PropertyButton(
            "ПУСК\nМАШИН", 0, "ПУСК", 
            svetofor__code_green, 
            svetofor__timing)
        
        button__launch_race_carts.clicked.connect(
            lambda checked=False, 
            cart_list=button_cart_list: 
            launch_race_carts(cart_list, button__launch_race_carts))
        
        button__launch_race_carts.setFixedWidth(svetofor__button_width)
        button__launch_race_carts.setFixedHeight(svetofor__button_height+50)
        #
        #
        #
        button__reset = QPushButton("СБРОС")
        button__reset.clicked.connect(
            lambda checked = False,
            cart_list = button_cart_list:
                reset(button_cart_list, 
                      layout__grid_carts_race, 
                      layout__grid_carts_park)
        )
        button__reset.setFixedHeight(svetofor__button_height+30)
        #
        #
        #
        button__detskiy = QPushButton("ДЕТСКИЙ")
        button__detskiy.clicked.connect(
            lambda checked = False,
            cart_list = button_cart_list:
                detskiy(button_cart_list, 
                      layout__grid_carts_race, 
                      layout__grid_carts_park)
        )
        
        button__detskiy.setFixedHeight(svetofor__button_height+20)
        #
        #
        #
        button__vzrosliy = QPushButton("ВЗРОСЛЫЙ")
        button__vzrosliy.clicked.connect(
            lambda checked = False,
            cart_list = button_cart_list:
                vzrosliy(button_cart_list, 
                      layout__grid_carts_race, 
                      layout__grid_carts_park)
        )
        
        button__vzrosliy.setFixedHeight(svetofor__button_height+20)
        #
        svetofor__label = QLabel("УПРАВЛЕНИЕ→\nСВЕТОФОРОМ→")
        svetofor__label.setFixedWidth(svetofor__button_width)
        svetofor__label.setFixedHeight(svetofor__button_height)
        
        layout__row_svetofor.addWidget(button__launch_race_carts)
        layout__row_svetofor.addWidget(button__reset)
        layout__row_svetofor.addWidget(button__detskiy)
        layout__row_svetofor.addWidget(button__vzrosliy)
        layout__row_svetofor.addWidget(svetofor__label)
        layout__row_svetofor.addWidget(svetofor__button_red)
        layout__row_svetofor.addWidget(svetofor__button_green)
        layout__row_svetofor.addWidget(svetofor__button_off)
        



        # --------------------------------------------------------------------- #
        
        # Пустой промежуток между двумя колоннами
        emptiness = QWidget()
        emptiness.setFixedWidth(30)
        layout__column_empty_left.addWidget(emptiness)
        layout__column_empty_middle.addWidget(emptiness)
        layout__column_empty_right.addWidget(emptiness)
        

        # Инициализация интерфейса
        widget = QWidget()
        widget.setLayout(layout__main)
        self.setCentralWidget(widget)
        
        layout__main.addLayout(layout__grid_carts_park)
        layout__main.addLayout(layout__column_empty_middle)
        layout__main.addLayout(layout__grid_carts_race)
        layout__main.addLayout(layout__row_svetofor)
        layout__main.addLayout(layout__column_empty_right)
        
        
        # СТИЛИЗАЦИЯ КНОПОК И ИНТЕРФЕЙСА -------------------------------------------------------- #
        # Стилизация кнопок картинга -- Чередующиеся цвета границ кнопок
        def increment_color(color: str, increment: int):
            i = int(color, 16)
            i += increment
            color = hex(i)
            return color
        
        button_cart_border_color = '0xA61697' # Цвет границы первой кнопки
        
        for button_cart in button_cart_list:
            button_cart_border_color = increment_color(button_cart_border_color, 2)
            stylesheet_red = f"""
                    QFrame {{
                        background-color: red;
                        border: 2px solid #{button_cart_border_color[2:]};
                        border-radius: 4px;
                    }}
                    QPushButton {{
                        background-color: red;
                        border: 2px solid #{button_cart_border_color[2:]};
                        border-radius: 4px;
                        padding: 8px;
                    }}
                    QPushButton:hover {{
                        background-color: #c00;
                        border: 2px solid #{button_cart_border_color[2:]};
                    }}
                    QPushButton:pressed {{
                        background-color: #900;
                        border: 2px solid #{button_cart_border_color[2:]};
                    }}
                """
            stylesheet_green =f"""
                    QFrame {{
                        background-color: #0e0;
                        border: 2px solid #{button_cart_border_color[2:]};
                        border-radius: 4px;
                    }}
                    QPushButton {{
                        background-color: #0e0;
                        border: 2px solid #{button_cart_border_color[2:]};
                        border-radius: 4px;
                        padding: 8px;
                    }}
                    QPushButton:hover {{
                        background-color: #0c0;
                        border: 3px solid #{button_cart_border_color[2:]};
                    }}
                    QPushButton:pressed {{
                        background-color: #090;
                        border: 2px solid #{button_cart_border_color[2:]};
                    }}
                """
            stylesheet_blue =f"""
                QFrame {{
                    background-color: blue;
                    border: 2px solid #{button_cart_border_color[2:]};
                    border-radius: 4px;
                }}
                QPushButton {{
                    background-color: blue;
                    border: 2px solid #{button_cart_border_color[2:]};
                    border-radius: 4px;
                    padding: 8px;
                }}
                QPushButton:hover {{
                    background-color: #00c;
                    border: 3px solid #{button_cart_border_color[2:]};
                }}
                QPushButton:pressed {{
                    background-color: #009;
                    border: 2px solid #{button_cart_border_color[2:]};
                }}
            """
            stylesheet_yellow =f"""
                    QFrame {{
                        background-color: yellow;
                        border: 2px solid #{button_cart_border_color[2:]};
                        border-radius: 4px;
                    }}
                    QPushButton {{
                        background-color: yellow;
                        border: 2px solid #{button_cart_border_color[2:]};
                        border-radius: 4px;
                        padding: 8px;
                    }}
                    QPushButton:hover {{
                        background-color: #cc0;
                        border: 2px solid #{button_cart_border_color[2:]};
                    }}
                    QPushButton:pressed {{
                        background-color: #990;
                        border: 2px solid #{button_cart_border_color[2:]};
                    }}
                """
            if 1 <= button_cart.cart_number <= 10 and (
                button_cart.cart_name.endswith("д")):
                    button_cart.setStyleSheet(stylesheet_red)
            elif 1 <= button_cart.cart_number <= 10 and (
            not button_cart.cart_name.endswith("д")):
                    button_cart.setStyleSheet(stylesheet_yellow)
            elif 11 <= button_cart.cart_number <= 20 and (
                button_cart.cart_name.endswith("д")):
                    button_cart.setStyleSheet(stylesheet_blue)
            elif 11 <= button_cart.cart_number <= 20 and (
            not button_cart.cart_name.endswith("д")):
                    button_cart.setStyleSheet(stylesheet_yellow)
            elif 21 <= button_cart.cart_number <= 30 and (
                button_cart.cart_name.endswith("д")):
                    button_cart.setStyleSheet(stylesheet_green)
            elif 21 <= button_cart.cart_number <= 30 and (
            not button_cart.cart_name.endswith("д")):
                    button_cart.setStyleSheet(stylesheet_blue)
            elif 31 <= button_cart.cart_number <= 35:
                    button_cart.setStyleSheet(stylesheet_blue)
            elif 36 <= button_cart.cart_number <= 45:
                    button_cart.setStyleSheet(stylesheet_green)

        
        # Стилизация кнопок светофора 
            
        stylesheet_launch = """
        QPushButton {
            color: #eee;
            font-size: 40px;
            background: #f11;
            border: 5px solid #d22;
            border-radius: 35px;
        }
        QPushButton:hover {
            background: #d11;
            border: 5px solid #911;
            border-radius: 35px;
        }
        QPushButton:pressed {
            background: #911;
            border: 8px solid #811;
            border-radius: 35px;
        }
        """
        button__launch_race_carts.setStyleSheet(stylesheet_launch)
        button__reset.setStyleSheet(stylesheet_launch)
        button__detskiy.setStyleSheet(stylesheet_launch)
        button__vzrosliy.setStyleSheet(stylesheet_launch)
        
        svetofor__label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        svetofor__label.setStyleSheet("""
        font-family: "Bahnschrift", Arial;
        font-size: 21px;
        color: #FFD700;
        border: 2px solid #FFD700;
        """)
        svetofor__button_green.setStyleSheet("""
        background-color: green;
        font-size: 60px;
        border: 2px solid #009900;
        border-radius: 4px;
        """)
        svetofor__button_red.setStyleSheet("""
        background-color: red;
        font-size: 60px;
        border: 2px solid #990000;
        border-radius: 4px;
        """)
        svetofor__button_off.setStyleSheet("""
        background-color: gray;
        font-size: 40px;
        border: 2px solid #444444;
        border-radius: 4px;
        """)
            
        # Стилизация шрифта
        label_park.setStyleSheet("""
        font-size: 15px;
        font-family: "Bahnschrift"
        """)
        self.setStyleSheet("""
        background-color: #7b16a6;
        font-size: 20px;
        color: #222222;
        font-weight: 900;
        font-family: "Comic Sans MS", Arial;
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())