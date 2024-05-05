import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QTextEdit, QListWidget

class Sporcu:
    def __init__(self, adi, spor_dali):
        self.adi = adi
        self.spor_dali = spor_dali
        self.antrenmanlar = {}

    def program_olustur(self, antrenman_adi, antrenman_detaylari):
        self.antrenmanlar[antrenman_adi] = antrenman_detaylari

    def ilerleme_kaydet(self, antrenman_adi, ilerleme):
        if antrenman_adi in self.antrenmanlar:
            self.antrenmanlar[antrenman_adi] += f"\n{ilerleme}"
        else:
            print("Antrenman bulunamadı.")

    def rapor_al(self):
        rapor = f"Sporcu Adı: {self.adi}\nSpor Dalı: {self.spor_dali}\nAntrenmanlar:"
        for adi, detaylar in self.antrenmanlar.items():
            rapor += f"\n{adi}: {detaylar}"
        return rapor

class Antrenman:
    def __init__(self, adi, detaylar):
        self.adi = adi
        self.detaylar = detaylar

class Takip:
    def __init__(self):
        self.sporcular = []

    def sporcu_ekle(self, sporcu):
        self.sporcular.append(sporcu)

class SporTakipUygulamasi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Spor Takip Uygulaması")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.label_adi = QLabel("Sporcu Adı:")
        self.layout.addWidget(self.label_adi)

        self.adi_input = QTextEdit()
        self.layout.addWidget(self.adi_input)

        self.label_spor_dali = QLabel("Spor Dalı:")
        self.layout.addWidget(self.label_spor_dali)

        self.spor_dali_input = QTextEdit()
        self.layout.addWidget(self.spor_dali_input)

        self.label_antrenman_adi = QLabel("Antrenman Adı:")
        self.layout.addWidget(self.label_antrenman_adi)

        self.antrenman_adi_input = QTextEdit()
        self.layout.addWidget(self.antrenman_adi_input)

        self.label_antrenman_detaylari = QLabel("Antrenman Detayları:")
        self.layout.addWidget(self.label_antrenman_detaylari)

        self.antrenman_detaylari_input = QTextEdit()
        self.layout.addWidget(self.antrenman_detaylari_input)

        self.button_program_olustur = QPushButton("Program Oluştur")
        self.button_program_olustur.clicked.connect(self.program_olustur)
        self.layout.addWidget(self.button_program_olustur)

        self.button_ilerleme_kaydet = QPushButton("İlerleme Kaydet")
        self.button_ilerleme_kaydet.clicked.connect(self.ilerleme_kaydet)
        self.layout.addWidget(self.button_ilerleme_kaydet)

        self.button_rapor_al = QPushButton("Rapor Al")
        self.button_rapor_al.clicked.connect(self.rapor_al)
        self.layout.addWidget(self.button_rapor_al)

        self.list_widget = QListWidget()
        self.layout.addWidget(self.list_widget)

        self.central_widget.setLayout(self.layout)

        self.takip = Takip()
        self.baglanti_kur()

    def baglanti_kur(self):
        self.baglanti = sqlite3.connect('spor_takip.db')
        self.cursor = self.baglanti.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sporcular (
                adi TEXT,
                spor_dali TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS antrenmanlar (
                sporcu_adi TEXT,
                adi TEXT,
                detaylar TEXT
            )
        ''')
        self.baglanti.commit()

    def program_olustur(self):
        adi = self.adi_input.toPlainText()
        spor_dali = self.spor_dali_input.toPlainText()
        antrenman_adi = self.antrenman_adi_input.toPlainText()
        antrenman_detaylari = self.antrenman_detaylari_input.toPlainText()

        sporcu = Sporcu(adi, spor_dali)
        sporcu.program_olustur(antrenman_adi, antrenman_detaylari)
        self.takip.sporcu_ekle(sporcu)

        self.cursor.execute("INSERT INTO sporcular (adi, spor_dali) VALUES (?, ?)", (adi, spor_dali))
        self.cursor.execute("INSERT INTO antrenmanlar (sporcu_adi, adi, detaylar) VALUES (?, ?, ?)", (adi, antrenman_adi, antrenman_detaylari))
        self.baglanti.commit()

        print("Program oluşturuldu.")

    def ilerleme_kaydet(self):
        adi = self.adi_input.toPlainText()
        antrenman_adi = self.antrenman_adi_input.toPlainText()
        ilerleme = self.antrenman_detaylari_input.toPlainText()

        for sporcu in self.takip.sporcular:
            if sporcu.adi == adi:
                sporcu.ilerleme_kaydet(antrenman_adi, ilerleme)
                self.cursor.execute("UPDATE antrenmanlar SET detaylar = ? WHERE sporcu_adi = ? AND adi = ?", (sporcu.antrenmanlar[antrenman_adi], adi, antrenman_adi))
                self.baglanti.commit()
                print("İlerleme kaydedildi.")
                return

        print("Sporcu bulunamadı.")

    def rapor_al(self):
        adi = self.adi_input.toPlainText()
        self.list_widget.clear()

        self.cursor.execute("SELECT * FROM antrenmanlar WHERE sporcu_adi = ?", (adi,))
        antrenmanlar = self.cursor.fetchall()
        if antrenmanlar:
            for antrenman in antrenmanlar:
                rapor = f"Sporcu Adı: {adi}\nSpor Dalı: {antrenman[1]}\nAntrenmanlar:\n{antrenman[2]}"
                self.list_widget.addItem(rapor)
        else:
            print("Sporcu bulunamadı.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SporTakipUygulamasi()
    window.show()
    sys.exit(app.exec_())
