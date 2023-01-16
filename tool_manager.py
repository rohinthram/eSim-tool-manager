import sys
import json
import requests

import shutil
import os

import subprocess

#from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QMainWindow, QComboBox, QGridLayout, QScrollArea
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt

WIDTH = 700
HEIGHT = 500
X = 100
Y = 100
py_loc = r'C:\Users\rohin\AppData\Local\Programs\Python\Python38\python.exe'        

class ToolManagerWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mainWidget = QWidget()

        self.setWindowTitle('eSim - Tool Manager')
        self.setWindowIcon(QIcon('assets/esim.png'))

        self.setStyleSheet('background-color:;')

        self.mainLayout = QGridLayout(self.mainWidget)

        
        self.title = QLabel(self.mainWidget)
        self.title.setText('eSim Tool Manager')
        self.title.setFont(QFont('times new roman', 20))
        self.titleLogoLabel = QLabel(self.mainWidget)
        self.titleLogoLabel.setPixmap(QPixmap('assets/esim.png').scaled(64, 64))
        self.titleLogoLabel.setFont(QFont('', 10))
        
        self.mainLayout.addWidget(self.titleLogoLabel, 0, 0)
        self.mainLayout.addWidget(self.title, 0, 1)

        self.mainLayout.setSpacing(10)

        
        self.info = json.load(open('assets/packages_info.json'))
        self.pkgs = QComboBox(self)
        self.pkgs.addItem('Select required package')
        for i in self.info:
            self.pkgs.addItem(i)
        self.OPTION_COMPLETED_CKTS = 'Completed Circuits'
        self.pkgs.addItem(self.OPTION_COMPLETED_CKTS)
        
        
        b1 = QPushButton(self.mainWidget)
        b1.setObjectName(i)
        b1.setText('Details')
        b1.clicked.connect(self.show_info)
        
        self.mainLayout.addWidget(self.pkgs, 1, 0)
        self.mainLayout.addWidget(b1, 1, 1)

        self.content = QLabel(self)

        self.mainLayout.addWidget(self.content, 2, 0)

        self.installButton = QPushButton('Install')
        self.installButton.clicked.connect(self.process)

        self.uninstallButton = QPushButton('Uninstall')
        self.uninstallButton.clicked.connect(self.uninstall)

        self.mainLayout.addWidget(self.installButton, 3, 0)
        self.mainLayout.addWidget(self.uninstallButton, 3, 1)

        self.cktCategory = QComboBox(self)
        self.mainLayout.addWidget(self.cktCategory, 4, 0)

        self.fetchCircuitCategoryButton = QPushButton(self)
        self.fetchCircuitCategoryButton.setText('Fetch Category')
        self.fetchCircuitCategoryButton.clicked.connect(self.fetch_available_circuit)
        self.mainLayout.addWidget(self.fetchCircuitCategoryButton, 4, 1)

        self.ckt = QComboBox(self)
        self.mainLayout.addWidget(self.ckt, 5, 0)
        
        self.fetchCircuitButton = QPushButton(self)
        self.fetchCircuitButton.setText('Fetch Circuit Details')
        self.fetchCircuitButton.clicked.connect(self.fetch_required_circuit)
        self.mainLayout.addWidget(self.fetchCircuitButton, 5, 1)

        self.cktDescription = QLabel(self)
        self.mainLayout.addWidget(self.cktDescription, 6, 0, 1, 2)

        self.getCircuitButton = QPushButton(self)
        self.getCircuitButton.setText('Fetch Circuit')
        self.getCircuitButton.clicked.connect(self.get_required_circuit)
        self.mainLayout.addWidget(self.getCircuitButton, 7, 0, 1, 2)


        
        #self.installLog = QLabel()
        self.installLog = QScrollArea()
        self.installLogWidget = QWidget()
        self.installLogLayout = QVBoxLayout()

        self.installLogWidget.setLayout(self.installLogLayout)

        self.installLog.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.installLog.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.installLog.setWidgetResizable(True)
        self.installLog.setWidget(self.installLogWidget)
        

        self.mainLayout.addWidget(self.installLog, 10, 0, 1, 2)

        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        self.installButton.hide()
        self.uninstallButton.hide()
        self.cktCategory.hide()
        self.fetchCircuitCategoryButton.hide()
        self.ckt.hide()
        self.fetchCircuitButton.hide()
        self.cktDescription.hide()
        self.getCircuitButton.hide()


        self.feature = ''
        self.pkg_url = ''
        self._in_machine = {}


    def show_info(self):
        bt = self.pkgs.currentText()

        if bt == self.OPTION_COMPLETED_CKTS:
            try:
                self.installButton.hide()
                self.uninstallButton.hide()
            except:
                pass
            
            self.cktCategory.show()
            self.fetchCircuitCategoryButton.show()

            self.available_categories = json.load(open('assets/categories.json'))

            self.cktCategory.clear()
            for i in self.available_categories:
                self.cktCategory.addItem(i)

            self.content.setText('Select necessary category to be downloaded')

            return
        
        try:
            self.fetchCircuitCategoryButton.hide()
            self.cktCategory.hide()
            self.ckt.hide()
            self.fetchCircuitButton.hide()
            self.cktDescription.hide()
            self.getCircuitButton.hide()

        except:
            pass
        self.installButton.show()
        self.uninstallButton.show()

        self.feature = bt
        #r = requests.get('details_url')
        #cnt = r.json()

        #cnt = {'pkg' : {'details':'safasdf', 'versions': {'1.0':'url', '2.0':'url #2'}}}
        try:
            self.details, self.pkg_urls, self.installers = self.info[bt]
        except KeyError:
            if 'Select required package' in bt:
                self.feature = ''
                return
            txt = f'Unable to fetch package : {bt}'
            self.installLogLayout.addWidget(QLabel(txt))
            return
        
        txt = f'<h1>{self.feature}</h1> {self.details} <br/>URL : {", ".join(self.pkg_urls[:-1])+self.pkg_urls[-1]}' 
        self.content.setText(txt)

        self._in_machine = json.load(open('assets/in_machine.json'))
        

    def process(self):
        if not self.feature:
            txt = 'Feature not selected'
            self.installLogLayout.addWidget(QLabel(txt))
            return

        if self.feature in self._in_machine:
            txt = 'Feature already installed'
            self.installLogLayout.addWidget(QLabel(txt))
            return 

        txt = f'Fetch {self.feature}'
        self.installLogLayout.addWidget(QLabel(txt))
        
        txt = 'Installing .. '
        self.installLogLayout.addWidget(QLabel(txt))

        try:
            txt = subprocess.Popen(f"{py_loc} tool_mnr.py install {self.feature}", shell=True, stdout=subprocess.PIPE).stdout
            txt = txt.read().decode('utf-8')
            self.installLogLayout.addWidget(QLabel(txt))
    
            if 'Error' not in txt:
                self.installLogLayout.addWidget(QLabel('Successfully installed !!!'))
                self._in_machine[self.feature] = 'installed'
                val = json.dumps(self._in_machine)
                with open('assets/in_machine.json', 'w') as file:
                    file.write(val)
            else:
                self.installLogLayout.addWidget(QLabel('[Error]'))

        except Exception as e:
            self.installLogLayout.addWidget(QLabel(str(e)))    

    def uninstall(self):
        if not self.feature:
            txt = 'Feature not selected'
            self.installLogLayout.addWidget(QLabel(txt))
            return
        try:
            self._in_machine[self.feature]
        except KeyError:
            txt = 'Feature not installed!'
            self.installLogLayout.addWidget(QLabel(txt))
            return 
            
        txt = 'Uninstalling ...'
        self.installLogLayout.addWidget(QLabel(txt))

        try:
            txt = subprocess.Popen(f"{py_loc} tool_mnr.py uninstall {self.feature}", shell=True, stdout=subprocess.PIPE).stdout
            txt = txt.read().decode('utf-8')
            self.installLogLayout.addWidget(QLabel(txt))
        
            if 'Error' not in txt:
                self.installLogLayout.addWidget(QLabel('Successfully uninstalled !!!'))
                del self._in_machine[self.feature]

                val = json.dumps(self._in_machine)
                with open('assets/in_machine.json', 'w') as file:
                    file.write(val)
            else:
                self.installLogLayout.addWidget(QLabel('[Error]'))

        except Exception as e:
            self.installLogLayout.addWidget(QLabel('sdfsf'))
        
    def fetch_available_circuit(self):
        self.ckt.show()
        self.fetchCircuitButton.show()

        self.content.setText('Select necessary circuit to be downloaded')

        name = self.cktCategory.currentText()
        self.ckts = json.load(open(f'assets/completed_circuits_{name}.json'))

        self.ckt.clear()
        for i in self.ckts:
                self.ckt.addItem(i)
        '''
        out_file = f'{name}.zip'
        with requests.get(url, stream=True) as r:
            total_length = int(r.headers.get("Content-Length"))

            with tqdm.wrapattr(r.raw, "read", total=total_length) as raw:
                with open(out_file, 'wb')as output:
                    shutil.copyfileobj(raw, output)
        
        path_to_extract = '.'.join(out_file.split('.')[:-1])
        shutil.unpack_archive(out_file, path_to_extract)
        '''


    def fetch_required_circuit(self):
        self.cktDescription.show()
        name = self.ckt.currentText()
        txt = self.ckts[name]["description"]
        self.cktDescription.setText(txt)
        self.getCircuitButton.show()

    def get_required_circuit(self):
        name = self.ckt.currentText()
        url = self.ckts[name]["url"]

        txt = f'Circuit fethed : {name}'
        self.installLogLayout.addWidget(QLabel(txt))

app = QApplication(sys.argv)
window = ToolManagerWindow()
window.show()

sys.exit(app.exec_())
