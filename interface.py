import sys
import math
import random
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QDoubleSpinBox, QSpinBox, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QDialog,
    QPlainTextEdit, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal

# --- DÉPENDANCES GÉOMÉTRIQUES (pip install shapely matplotlib) ---
from shapely.geometry import Polygon, Point
from shapely.affinity import translate, rotate, scale
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# --- PARTIE 3 : INTERFACES GRAPHIQUES (PyQt6) ---

class Calepinage1DApp(QMainWindow):
    retour_au_choix = pyqtSignal()
    """Interface graphique pour l'optimisation de barres (1D)."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimisation de Découpe de Barres (1D)")
        self.setGeometry(150, 150, 800, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        params_layout = QGridLayout()
        params_layout.addWidget(QLabel("<b>Longueur standard de la barre (mm):</b>"), 0, 0)
        self.longueur_standard = QDoubleSpinBox(minimum=100, maximum=20000, value=6000, singleStep=100)
        params_layout.addWidget(self.longueur_standard, 0, 1)
        params_layout.addWidget(QLabel("<b>Épaisseur de la lame (mm):</b>"), 1, 0)
        self.epaisseur_lame = QDoubleSpinBox(minimum=0, maximum=100, value=3)
        params_layout.addWidget(self.epaisseur_lame, 1, 1)
        main_layout.addLayout(params_layout)
        main_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))

        saisie_layout = QHBoxLayout()
        saisie_layout.addWidget(QLabel("Longueur à découper:"))
        self.longueur_piece = QDoubleSpinBox(minimum=1, maximum=20000, value=500)
        saisie_layout.addWidget(self.longueur_piece)
        saisie_layout.addWidget(QLabel("Quantité:"))
        self.quantite_piece = QSpinBox(minimum=1, maximum=1000, value=1)
        saisie_layout.addWidget(self.quantite_piece)
        self.btn_ajouter_1d = QPushButton("Ajouter à la liste")
        saisie_layout.addWidget(self.btn_ajouter_1d)
        main_layout.addLayout(saisie_layout)

        self.table_pieces_1d = QTableWidget()
        self.table_pieces_1d.setColumnCount(2)
        self.table_pieces_1d.setHorizontalHeaderLabels(["Longueur", "Quantité"])
        self.table_pieces_1d.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table_pieces_1d)

        gestion_liste_layout = QHBoxLayout()
        self.btn_charger_1d = QPushButton("Charger...")
        gestion_liste_layout.addWidget(self.btn_charger_1d)
        self.btn_sauvegarder_1d = QPushButton("Sauvegarder...")
        gestion_liste_layout.addWidget(self.btn_sauvegarder_1d)
        gestion_liste_layout.addStretch()
        self.btn_supprimer_1d = QPushButton("Supprimer la sélection")
        gestion_liste_layout.addWidget(self.btn_supprimer_1d)
        main_layout.addLayout(gestion_liste_layout)

        self.btn_calculer_1d = QPushButton("Lancer le Calcul d'Optimisation")
        self.btn_calculer_1d.setStyleSheet("background-color: #008CBA; color: white; font-weight: bold; padding: 10px;")
        main_layout.addWidget(self.btn_calculer_1d)

        main_layout.addWidget(QLabel("<b>Résultats du Plan de Découpe :</b>"))
        self.resultats_text = QPlainTextEdit()
        self.resultats_text.setReadOnly(True)
        self.resultats_text.setStyleSheet("font-family: Consolas, Courier New;")
        main_layout.addWidget(self.resultats_text)

        btn_retour = QPushButton("Retour au Choix du Mode")
        main_layout.addWidget(btn_retour)
        btn_retour.clicked.connect(self.retour)

        self.btn_ajouter_1d.clicked.connect(self.ajouter_piece_1d)
        self.btn_supprimer_1d.clicked.connect(self.supprimer_piece_1d)
        self.btn_calculer_1d.clicked.connect(self.lancer_calcul_1d)
        self.btn_charger_1d.clicked.connect(self.charger_liste_1d)
        self.btn_sauvegarder_1d.clicked.connect(self.sauvegarder_liste_1d)
        btn_retour.clicked.connect(self.retour)

    def ajouter_piece_1d(self):
        longueur = self.longueur_piece.value()
        quantite = self.quantite_piece.value()
        row = self.table_pieces_1d.rowCount()
        self.table_pieces_1d.insertRow(row)
        self.table_pieces_1d.setItem(row, 0, QTableWidgetItem(str(longueur)))
        self.table_pieces_1d.setItem(row, 1, QTableWidgetItem(str(quantite)))

    def supprimer_piece_1d(self):
        selected_row = self.table_pieces_1d.currentRow()
        if selected_row >= 0:
            self.table_pieces_1d.removeRow(selected_row)

    def sauvegarder_liste_1d(self):
        if self.table_pieces_1d.rowCount() == 0:
            QMessageBox.warning(self, "Liste Vide", "Il n'y a aucune pièce à sauvegarder.")
            return
        chemin_fichier, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la liste 1D", "",
                                                        "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
        if not chemin_fichier:
            return
        try:
            with open(chemin_fichier, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['longueur', 'quantite'])
                for row in range(self.table_pieces_1d.rowCount()):
                    writer.writerow(
                        [self.table_pieces_1d.item(row, 0).text(), self.table_pieces_1d.item(row, 1).text()])
            QMessageBox.information(self, "Succès", f"Liste sauvegardée dans\n{chemin_fichier}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Sauvegarde", f"Impossible de sauvegarder le fichier :\n{e}")

    def charger_liste_1d(self):
        chemin_fichier, _ = QFileDialog.getOpenFileName(self, "Charger une liste 1D", "",
                                                        "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
        if not chemin_fichier:
            return
        try:
            with open(chemin_fichier, mode='r', newline='', encoding='utf-8') as f:
                lecteur = csv.reader(f)
                next(lecteur, None)
                self.table_pieces_1d.setRowCount(0)
                for ligne in lecteur:
                    if len(ligne) == 2:
                        longueur, quantite = ligne
                        row = self.table_pieces_1d.rowCount()
                        self.table_pieces_1d.insertRow(row)
                        self.table_pieces_1d.setItem(row, 0, QTableWidgetItem(longueur))
                        self.table_pieces_1d.setItem(row, 1, QTableWidgetItem(quantite))
            QMessageBox.information(self, "Succès", "La liste a été chargée.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Chargement", f"Impossible de lire le fichier :\n{e}")

    def lancer_calcul_1d(self):
        if self.table_pieces_1d.rowCount() == 0:
            QMessageBox.warning(self, "Aucune pièce",
                                "Veuillez ajouter au moins une pièce.")
            return
        longueur_barre = self.longueur_standard.value()
        epaisseur_coupe = self.epaisseur_lame.value()
        liste_pieces = []
        for row in range(self.table_pieces_1d.rowCount()):
            liste_pieces.extend(
                [float(self.table_pieces_1d.item(row, 0).text())] * int(self.table_pieces_1d.item(row, 1).text()))
        plan, perte = calepinage_barres(liste_pieces, longueur_barre, epaisseur_coupe)
        if plan is None:
            QMessageBox.critical(self, "Erreur de Calcul", perte)
            return
        output = [f"--- PLAN DE DÉCOUPE OPTIMISÉ ---",
                  f"Longueur barre: {longueur_barre} mm, Épaisseur lame: {epaisseur_coupe} mm\n"]
        for i, barre in enumerate(plan):
            longueur_pieces = sum(barre)
            cout_coupes = len(barre) * epaisseur_coupe
            longueur_consommee = longueur_pieces + cout_coupes
            chute = longueur_barre - longueur_consommee
            output.extend(
                [f"** Barre n°{i + 1} **", f"  Découpes : {barre}", f"  Consommé : {longueur_consommee:.2f} mm",
                 f"  Chute : {chute:.2f} mm", "-" * 30])
        output.extend([f"\n✅ Total barres à utiliser : {len(plan)}", f"📉 Perte totale : {perte:.2f}%"])
        self.resultats_text.setPlainText("\n".join(output))

    def retour(self):
        self.hide()
        self.retour_au_choix.emit()

    def closeEvent(self, event):
        self.selection_window.show()
        event.accept()


class Calepinage2DApp(QMainWindow):
    retour_au_choix = pyqtSignal()
    """Interface graphique pour l'optimisation de panneaux (2D)."""

    def __init__(self):
        super().__init__()
        self.btn_calculer = None
        self.btn_sauvegarder = None
        self.btn_charger = None
        self.btn_supprimer = None
        self.table_pieces = None
        self.btn_ajouter = None
        self.spin_quantite = None
        self.stacked_widget_main = None
        self.combo_forme_principale = None
        self.kerf = None
        self.panel_h = None
        self.panel_w = None
        self.setWindowTitle("Optimisation de Découpe de Panneaux (2D)")
        self.setGeometry(100, 100, 1100, 800)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.creer_panneau_parametres()
        top_layout = QHBoxLayout()
        self.creer_panneau_saisie(top_layout)
        self.creer_panneau_liste(top_layout)
        self.main_layout.addLayout(top_layout)
        self.creer_panneau_actions()
        self.btn_retour = QPushButton("Retour au Choix du Mode")
        self.main_layout.addWidget(self.btn_retour)
        self.connect_signals()

    def creer_panneau_parametres(self):
        params_widget = QFrame()
        params_widget.setFrameShape(QFrame.Shape.StyledPanel)
        params_layout = QHBoxLayout(params_widget)
        params_layout.addWidget(QLabel("<b>Paramètres Généraux (Panneau 2D) :</b>"))
        params_layout.addWidget(QLabel("L. Panneau:"))
        self.panel_w = QDoubleSpinBox(minimum=100, maximum=10000, value=2500, singleStep=100)
        params_layout.addWidget(self.panel_w)
        params_layout.addWidget(QLabel("H. Panneau:"))
        self.panel_h = QDoubleSpinBox(minimum=100, maximum=10000, value=1250, singleStep=100)
        params_layout.addWidget(self.panel_h)
        params_layout.addWidget(QLabel("L. Lame:"))
        self.kerf = QDoubleSpinBox(minimum=0, maximum=100, value=3)
        params_layout.addWidget(self.kerf)
        self.main_layout.addWidget(params_widget)

    def creer_panneau_saisie(self, parent_layout):
        saisie_widget = QWidget()
        saisie_layout = QVBoxLayout(saisie_widget)
        saisie_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        saisie_layout.addWidget(QLabel("<b>1. Choisir la catégorie :</b>"))
        self.combo_forme_principale = QComboBox()
        self.combo_forme_principale.addItems(["Rectangle", "Trapèze", "Triangle", "Forme Circulaire"])
        saisie_layout.addWidget(self.combo_forme_principale)
        self.stacked_widget_main = QStackedWidget()
        self.stacked_widget_main.addWidget(self._create_rectangle_page())
        self.stacked_widget_main.addWidget(self._create_trapeze_page())
        self.stacked_widget_main.addWidget(self._create_triangle_page())
        self.stacked_widget_main.addWidget(self._create_circulaire_page())
        saisie_layout.addWidget(QLabel("<b>2. Définir la pièce :</b>"))
        saisie_layout.addWidget(self.stacked_widget_main)
        saisie_layout.addWidget(QLabel("<b>3. Quantité :</b>"))
        self.spin_quantite = QSpinBox(minimum=1, maximum=1000, value=1)
        saisie_layout.addWidget(self.spin_quantite)
        self.btn_ajouter = QPushButton("Ajouter à la liste →")
        self.btn_ajouter.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        saisie_layout.addWidget(self.btn_ajouter)
        parent_layout.addWidget(saisie_widget, 2)

    def _create_rectangle_page(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(QLabel("Largeur (mm):"), 0, 0)
        self.rect_largeur = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
        layout.addWidget(self.rect_largeur, 0, 1)
        layout.addWidget(QLabel("Hauteur (mm):"), 1, 0)
        self.rect_hauteur = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
        layout.addWidget(self.rect_hauteur, 1, 1)
        return page

    def _create_trapeze_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        combo = QComboBox()
        combo.addItems(["Isocèle", "Rectangle"])
        layout.addWidget(QLabel("Type de Trapèze :"))
        layout.addWidget(combo)
        stacked = QStackedWidget()
        sub_iso = QWidget()
        l_iso = QGridLayout(sub_iso)
        l_iso.addWidget(QLabel("Grande Base:"), 0, 0)
        self.trap_iso_gb = QDoubleSpinBox(minimum=1, maximum=10000, value=600)
        l_iso.addWidget(self.trap_iso_gb, 0, 1)
        l_iso.addWidget(QLabel("Petite Base:"), 1, 0)
        self.trap_iso_pb = QDoubleSpinBox(minimum=1, maximum=10000, value=400)
        l_iso.addWidget(self.trap_iso_pb, 1, 1)
        l_iso.addWidget(QLabel("Hauteur:"), 2, 0)
        self.trap_iso_h = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
        l_iso.addWidget(self.trap_iso_h, 2, 1)
        stacked.addWidget(sub_iso)
        sub_rect = QWidget()
        l_rect = QGridLayout(sub_rect)
        l_rect.addWidget(QLabel("Grande Base:"), 0, 0)
        self.trap_rect_gb = QDoubleSpinBox(minimum=1, maximum=10000, value=650)
        l_rect.addWidget(self.trap_rect_gb, 0, 1)
        l_rect.addWidget(QLabel("Petite Base:"), 1, 0)
        self.trap_rect_pb = QDoubleSpinBox(minimum=1, maximum=10000, value=450)
        l_rect.addWidget(self.trap_rect_pb, 1, 1)
        l_rect.addWidget(QLabel("Hauteur:"), 2, 0)
        self.trap_rect_h = QDoubleSpinBox(minimum=1, maximum=10000, value=350)
        l_rect.addWidget(self.trap_rect_h, 2, 1)
        stacked.addWidget(sub_rect)
        layout.addWidget(stacked)
        combo.currentIndexChanged.connect(stacked.setCurrentIndex)
        page.setProperty("combo", combo)
        return page

    def _create_triangle_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        self.combo_tri_type = QComboBox()
        self.combo_tri_type.addItems(["Équilatéral", "Isocèle", "Rectangle", "Quelconque"])
        layout.addWidget(QLabel("Type de Triangle :"))
        layout.addWidget(self.combo_tri_type)
        self.stacked_tri = QStackedWidget()
        sub_equi = QWidget()
        l_equi = QGridLayout(sub_equi)
        l_equi.addWidget(QLabel("Côté (mm):"), 0, 0)
        self.tri_equi_cote = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
        l_equi.addWidget(self.tri_equi_cote, 0, 1)
        self.stacked_tri.addWidget(sub_equi)
        sub_iso = QWidget()
        l_iso = QVBoxLayout(sub_iso)
        self.combo_tri_iso_methode = QComboBox()
        self.combo_tri_iso_methode.addItems(["Par base et hauteur", "Par 3 côtés"])
        l_iso.addWidget(QLabel("Méthode :"))
        l_iso.addWidget(self.combo_tri_iso_methode)
        self.stacked_tri_iso = QStackedWidget()
        page_iso_bh = QWidget()
        l_iso_bh = QGridLayout(page_iso_bh)
        l_iso_bh.addWidget(QLabel("Base:"), 0, 0)
        self.tri_iso_base = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
        l_iso_bh.addWidget(self.tri_iso_base, 0, 1)
        l_iso_bh.addWidget(QLabel("Hauteur:"), 1, 0)
        self.tri_iso_hauteur = QDoubleSpinBox(minimum=1, maximum=10000, value=400)
        l_iso_bh.addWidget(self.tri_iso_hauteur, 1, 1)
        self.stacked_tri_iso.addWidget(page_iso_bh)
        page_iso_sss = QWidget()
        l_iso_sss = QGridLayout(page_iso_sss)
        l_iso_sss.addWidget(QLabel("Côté égal 1:"), 0, 0)
        self.tri_iso_s1 = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
        l_iso_sss.addWidget(self.tri_iso_s1, 0, 1)
        l_iso_sss.addWidget(QLabel("Côté égal 2:"), 1, 0)
        self.tri_iso_s2 = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
        l_iso_sss.addWidget(self.tri_iso_s2, 1, 1)
        l_iso_sss.addWidget(QLabel("Base:"), 2, 0)
        self.tri_iso_s3 = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
        l_iso_sss.addWidget(self.tri_iso_s3, 2, 1)
        self.stacked_tri_iso.addWidget(page_iso_sss)
        l_iso.addWidget(self.stacked_tri_iso)
        self.combo_tri_iso_methode.currentIndexChanged.connect(self.stacked_tri_iso.setCurrentIndex)
        self.stacked_tri.addWidget(sub_iso)
        sub_rect = QWidget()
        l_rect = QVBoxLayout(sub_rect)
        self.combo_tri_rect_methode = QComboBox()
        self.combo_tri_rect_methode.addItems(["Par 2 côtés", "Par 1 côté et 1 angle"])
        l_rect.addWidget(QLabel("Méthode :"))
        l_rect.addWidget(self.combo_tri_rect_methode)
        self.stacked_tri_rect = QStackedWidget()
        page_rect_2c = QWidget()
        l_rect_2c = QGridLayout(page_rect_2c)
        l_rect_2c.addWidget(QLabel("Remplissez 2 des 3 champs :"), 0, 0, 1, 2)
        l_rect_2c.addWidget(QLabel("Adjacent:"), 1, 0)
        self.tri_rect_2c_adj = QDoubleSpinBox(minimum=0, maximum=10000, value=300)
        self.tri_rect_2c_adj.setSpecialValueText(" ")
        l_rect_2c.addWidget(self.tri_rect_2c_adj, 1, 1)
        l_rect_2c.addWidget(QLabel("Opposé:"), 2, 0)
        self.tri_rect_2c_opp = QDoubleSpinBox(minimum=0, maximum=10000, value=400)
        self.tri_rect_2c_opp.setSpecialValueText(" ")
        l_rect_2c.addWidget(self.tri_rect_2c_opp, 2, 1)
        l_rect_2c.addWidget(QLabel("Hypoténuse:"), 3, 0)
        self.tri_rect_2c_hyp = QDoubleSpinBox(minimum=0, maximum=10000, value=0)
        self.tri_rect_2c_hyp.setSpecialValueText(" ")
        l_rect_2c.addWidget(self.tri_rect_2c_hyp, 3, 1)
        self.stacked_tri_rect.addWidget(page_rect_2c)
        page_rect_1a = QWidget()
        l_rect_1a = QGridLayout(page_rect_1a)
        l_rect_1a.addWidget(QLabel("Côté connu:"), 0, 0)
        self.tri_rect_1a_cote = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
        l_rect_1a.addWidget(self.tri_rect_1a_cote, 0, 1)
        l_rect_1a.addWidget(QLabel("Angle (degrés):"), 1, 0)
        self.tri_rect_1a_angle = QDoubleSpinBox(minimum=1, maximum=89, value=30)
        l_rect_1a.addWidget(self.tri_rect_1a_angle, 1, 1)
        self.combo_rect_1a_type = QComboBox()
        self.combo_rect_1a_type.addItems(["Adjacent", "Opposé", "Hypoténuse"])
        l_rect_1a.addWidget(self.combo_rect_1a_type, 2, 0, 1, 2)
        self.stacked_tri_rect.addWidget(page_rect_1a)
        l_rect.addWidget(self.stacked_tri_rect)
        self.combo_tri_rect_methode.currentIndexChanged.connect(self.stacked_tri_rect.setCurrentIndex)
        self.stacked_tri.addWidget(sub_rect)
        sub_quel = QWidget()
        l_quel = QVBoxLayout(sub_quel)
        self.combo_tri_quel_methode = QComboBox()
        self.combo_tri_quel_methode.addItems(
            ["Par 3 côtés (SSS)", "Par 2 côtés et 1 angle (SAS)", "Par 1 côté et 2 angles (ASA)"])
        l_quel.addWidget(QLabel("Méthode :"))
        l_quel.addWidget(self.combo_tri_quel_methode)
        self.stacked_tri_quel = QStackedWidget()
        page_quel_sss = QWidget()
        l_quel_sss = QGridLayout(page_quel_sss)
        l_quel_sss.addWidget(QLabel("Côté A:"), 0, 0)
        self.tri_quel_sss_a = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
        l_quel_sss.addWidget(self.tri_quel_sss_a, 0, 1)
        l_quel_sss.addWidget(QLabel("Côté B:"), 1, 0)
        self.tri_quel_sss_b = QDoubleSpinBox(minimum=1, maximum=10000, value=600)
        l_quel_sss.addWidget(self.tri_quel_sss_b, 1, 1)
        l_quel_sss.addWidget(QLabel("Côté C:"), 2, 0)
        self.tri_quel_sss_c = QDoubleSpinBox(minimum=1, maximum=10000, value=700)
        l_quel_sss.addWidget(self.tri_quel_sss_c, 2, 1)
        self.stacked_tri_quel.addWidget(page_quel_sss)
        page_quel_sas = QWidget()
        l_quel_sas = QGridLayout(page_quel_sas)
        l_quel_sas.addWidget(QLabel("Côté B:"), 0, 0)
        self.tri_quel_sas_b = QDoubleSpinBox(minimum=1, maximum=10000, value=600)
        l_quel_sas.addWidget(self.tri_quel_sas_b, 0, 1)
        l_quel_sas.addWidget(QLabel("Côté C:"), 1, 0)
        self.tri_quel_sas_c = QDoubleSpinBox(minimum=1, maximum=10000, value=700)
        l_quel_sas.addWidget(self.tri_quel_sas_c, 1, 1)
        l_quel_sas.addWidget(QLabel("Angle A inclus (°):"), 2, 0)
        self.tri_quel_sas_angle = QDoubleSpinBox(minimum=1, maximum=179, value=45)
        l_quel_sas.addWidget(self.tri_quel_sas_angle, 2, 1)
        self.stacked_tri_quel.addWidget(page_quel_sas)
        page_quel_asa = QWidget()
        l_quel_asa = QGridLayout(page_quel_asa)
        l_quel_asa.addWidget(QLabel("Côté C:"), 0, 0)
        self.tri_quel_asa_c = QDoubleSpinBox(minimum=1, maximum=10000, value=700)
        l_quel_asa.addWidget(self.tri_quel_asa_c, 0, 1)
        l_quel_asa.addWidget(QLabel("Angle A adj. (°):"), 1, 0)
        self.tri_quel_asa_angle_a = QDoubleSpinBox(minimum=1, maximum=178, value=45)
        l_quel_asa.addWidget(self.tri_quel_asa_angle_a, 1, 1)
        l_quel_asa.addWidget(QLabel("Angle B adj. (°):"), 2, 0)
        self.tri_quel_asa_angle_b = QDoubleSpinBox(minimum=1, maximum=178, value=65)
        l_quel_asa.addWidget(self.tri_quel_asa_angle_b, 2, 1)
        self.stacked_tri_quel.addWidget(page_quel_asa)
        l_quel.addWidget(self.stacked_tri_quel)
        self.combo_tri_quel_methode.currentIndexChanged.connect(self.stacked_tri_quel.setCurrentIndex)
        self.stacked_tri.addWidget(sub_quel)
        layout.addWidget(self.stacked_tri)
        self.combo_tri_type.currentIndexChanged.connect(self.stacked_tri.setCurrentIndex)
        return page

    def _create_circulaire_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        combo = QComboBox()
        combo.addItems(["Cercle", "Ellipse"])
        layout.addWidget(QLabel("Type de Forme :"))
        layout.addWidget(combo)
        stacked = QStackedWidget()
        sub_cercle = QWidget()
        l_cercle = QGridLayout(sub_cercle)
        l_cercle.addWidget(QLabel("Rayon (mm):"), 0, 0)
        self.cercle_rayon = QDoubleSpinBox(minimum=1, maximum=5000, value=250)
        l_cercle.addWidget(self.cercle_rayon, 0, 1)
        stacked.addWidget(sub_cercle)
        sub_ellipse = QWidget()
        l_ellipse = QGridLayout(sub_ellipse)
        l_ellipse.addWidget(QLabel("Rayon X (mm):"), 0, 0)
        self.ellipse_rx = QDoubleSpinBox(minimum=1, maximum=5000, value=300)
        l_ellipse.addWidget(self.ellipse_rx, 0, 1)
        l_ellipse.addWidget(QLabel("Rayon Y (mm):"), 1, 0)
        self.ellipse_ry = QDoubleSpinBox(minimum=1, maximum=5000, value=200)
        l_ellipse.addWidget(self.ellipse_ry, 1, 1)
        stacked.addWidget(sub_ellipse)
        layout.addWidget(stacked)
        combo.currentIndexChanged.connect(stacked.setCurrentIndex)
        page.setProperty("combo", combo)
        return page

    def creer_panneau_liste(self, parent_layout):
        liste_widget = QWidget()
        liste_layout = QVBoxLayout(liste_widget)
        liste_layout.addWidget(QLabel("<b>Liste des Pièces à Découper :</b>"))
        self.table_pieces = QTableWidget()
        self.table_pieces.setColumnCount(3)
        self.table_pieces.setHorizontalHeaderLabels(["Quantité", "Type", "Description"])
        self.table_pieces.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_pieces.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_pieces.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        liste_layout.addWidget(self.table_pieces)
        btn_layout = QHBoxLayout()
        self.btn_supprimer = QPushButton("Supprimer la sélection")
        self.btn_supprimer.setEnabled(False)
        btn_layout.addWidget(self.btn_supprimer)
        liste_layout.addLayout(btn_layout)
        parent_layout.addWidget(liste_widget, 3)

    def creer_panneau_actions(self):
        actions_widget = QFrame()
        actions_widget.setFrameShape(QFrame.Shape.StyledPanel)
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.btn_charger = QPushButton("Charger...")
        self.btn_sauvegarder = QPushButton("Sauvegarder...")
        self.btn_calculer = QPushButton("LANCER LE CALCUL")
        self.btn_calculer.setStyleSheet("background-color: #008CBA; color: white; font-weight: bold; padding: 15px;")
        actions_layout.addWidget(self.btn_charger)
        actions_layout.addWidget(self.btn_sauvegarder)
        actions_layout.addStretch()
        actions_layout.addWidget(self.btn_calculer)
        self.main_layout.addWidget(actions_widget)

    def connect_signals(self):
        self.combo_forme_principale.currentIndexChanged.connect(self.stacked_widget_main.setCurrentIndex)
        self.btn_ajouter.clicked.connect(self.ajouter_piece)
        self.btn_supprimer.clicked.connect(self.supprimer_piece)
        self.table_pieces.itemSelectionChanged.connect(self.maj_boutons_liste)
        self.btn_calculer.clicked.connect(self.lancer_calcul)
        self.btn_charger.clicked.connect(self.charger_liste_2d)
        self.btn_sauvegarder.clicked.connect(self.sauvegarder_liste_2d)
        self.btn_retour.clicked.connect(self.retour)

    def ajouter_piece(self):
        forme_principale = self.combo_forme_principale.currentText()
        quantite = self.spin_quantite.value()
        description = "Erreur de saisie"
        piece_data = {}
        valide = True
        if forme_principale == "Rectangle":
            largeur = self.rect_largeur.value()
            hauteur = self.rect_hauteur.value()
            description = f"Rectangle - L: {largeur}, H: {hauteur}"
            piece_data = {'forme': 'rectangle', 'largeur': largeur, 'hauteur': hauteur}
        elif forme_principale == "Trapèze":
            page = self.stacked_widget_main.currentWidget()
            combo = page.property("combo")
            type_forme = combo.currentText()
            if type_forme == "Isocèle":
                gb = self.trap_iso_gb.value()
                pb = self.trap_iso_pb.value()
                h = self.trap_iso_h.value()
                description = f"Trapèze Isocèle - GB: {gb}, PB: {pb}, H: {h}"
                piece_data = {'forme': 'trapeze_isocele', 'grande_base': gb, 'petite_base': pb, 'hauteur': h}
            elif type_forme == "Rectangle":
                gb = self.trap_rect_gb.value()
                pb = self.trap_rect_pb.value()
                h = self.trap_rect_h.value()
                description = f"Trapèze Rectangle - GB: {gb}, PB: {pb}, H: {h}"
                piece_data = {'forme': 'trapeze_rectangle', 'grande_base': gb, 'petite_base': pb, 'hauteur': h}
        elif forme_principale == "Triangle":
            type_tri = self.combo_tri_type.currentText()
            if type_tri == "Équilatéral":
                cote = self.tri_equi_cote.value()
                description = f"T. Équilatéral - Côté: {cote}"
                piece_data = {'forme': 'triangle_equilateral', 'cote': cote}
            elif type_tri == "Isocèle":
                methode = self.combo_tri_iso_methode.currentText()
                if "base et hauteur" in methode:
                    base = self.tri_iso_base.value()
                    h = self.tri_iso_hauteur.value()
                    description = f"T. Isocèle (B/H) - B: {base}, H: {h}"
                    piece_data = {'forme': 'triangle_isocele_bh', 'base': base, 'hauteur': h}
                else:
                    s1 = self.tri_iso_s1.value()
                    s2 = self.tri_iso_s2.value()
                    s3 = self.tri_iso_s3.value()
                    if s1 != s2:
                        QMessageBox.warning(self, "Erreur",
                                            "Les deux côtés égaux doivent avoir la même longueur.")
                        valide = False
                    description = f"T. Isocèle (SSS) - Côtés: {s1}, {s1}, {s3}"
                    piece_data = {'forme': 'triangle_isocele_sss', 'cote_egal': s1, 'base': s3}
            elif type_tri == "Rectangle":
                methode = self.combo_tri_rect_methode.currentText()
                if "2 côtés" in methode:
                    adj = self.tri_rect_2c_adj.value()
                    opp = self.tri_rect_2c_opp.value()
                    hyp = self.tri_rect_2c_hyp.value()
                    sides = {'adj': adj, 'opp': opp, 'hyp': hyp}
                    known_sides = {k: v for k, v in sides.items() if v > 0}
                    if len(known_sides) != 2:
                        QMessageBox.warning(self, "Erreur",
                                            "Veuillez remplir exactement 2 des 3 champs.")
                        valide = False
                    description = \
                        f"T. Rectangle (2C) - {', '.join([f'{k.capitalize()}:{v}' for k,v in known_sides.items()])}"
                    piece_data = {'forme': 'triangle_rectangle_2c', **known_sides}
                else:
                    cote = self.tri_rect_1a_cote.value()
                    angle = self.tri_rect_1a_angle.value()
                    type_cote = self.combo_rect_1a_type.currentText()
                    description = f"T. Rectangle (1A1C) - Côté({type_cote}): {cote}, Angle: {angle}°"
                    piece_data = {'forme': 'triangle_rectangle_1a1c', 'cote': cote, 'angle': angle,
                                  'type_cote': type_cote}
            elif type_tri == "Quelconque":
                methode = self.combo_tri_quel_methode.currentText()
                if "SSS" in methode:
                    a = self.tri_quel_sss_a.value()
                    b = self.tri_quel_sss_b.value()
                    c = self.tri_quel_sss_c.value()
                    description = f"T. Quelconque (SSS) - Côtés: {a}, {b}, {c}"
                    piece_data = {'forme': 'triangle_quelconque_sss', 'a': a, 'b': b, 'c': c}
                elif "SAS" in methode:
                    b = self.tri_quel_sas_b.value()
                    c = self.tri_quel_sas_c.value()
                    angle = self.tri_quel_sas_angle.value()
                    description = f"T. Quelconque (SAS) - B: {b}, C: {c}, Angle A: {angle}°"
                    piece_data = {'forme': 'triangle_quelconque_sas', 'b': b, 'c': c, 'angle_a': angle}
                elif "ASA" in methode:
                    c = self.tri_quel_asa_c.value()
                    angle_a = self.tri_quel_asa_angle_a.value()
                    angle_b = self.tri_quel_asa_angle_b.value()
                    description = f"T. Quelconque (ASA) - Côté C: {c}, Angle A: {angle_a}°, Angle B: {angle_b}°"
                    piece_data = {'forme': 'triangle_quelconque_asa', 'c': c, 'angle_a': angle_a, 'angle_b': angle_b}
        elif forme_principale == "Forme Circulaire":
            page = self.stacked_widget_main.currentWidget()
            combo_circ = page.property("combo")
            type_circ = combo_circ.currentText()
            if type_circ == "Cercle":
                rayon = self.cercle_rayon.value()
                description = f"Cercle - Rayon: {rayon}"
                piece_data = {'forme': 'cercle', 'rayon': rayon}
            elif type_circ == "Ellipse":
                rx = self.ellipse_rx.value()
                ry = self.ellipse_ry.value()
                description = f"Ellipse - Rayons: {rx}x{ry}"
                piece_data = {'forme': 'ellipse', 'rayon_x': rx, 'rayon_y': ry}

        if valide:
            row = self.table_pieces.rowCount()
            self.table_pieces.insertRow(row)
            q_item = QTableWidgetItem(str(quantite))
            d_item = QTableWidgetItem(description)
            type_item_text = description.split(' - ')[0] if ' - ' in description else forme_principale
            f_item = QTableWidgetItem(type_item_text)
            d_item.setData(Qt.ItemDataRole.UserRole, piece_data)
            self.table_pieces.setItem(row, 0, q_item)
            self.table_pieces.setItem(row, 1, f_item)
            self.table_pieces.setItem(row, 2, d_item)

    def supprimer_piece(self):
        selected_row = self.table_pieces.currentRow()
        if selected_row >= 0:
            self.table_pieces.removeRow(selected_row)

    def maj_boutons_liste(self):
        self.btn_supprimer.setEnabled(bool(self.table_pieces.selectedItems()))

    def sauvegarder_liste_2d(self):
        if self.table_pieces.rowCount() == 0:
            QMessageBox.warning(self, "Liste Vide", "Il n'y a aucune pièce à sauvegarder.")
            return
        chemin_fichier, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la liste 2D", "",
                                                        "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
        if not chemin_fichier:
            return
        try:
            with open(chemin_fichier, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in range(self.table_pieces.rowCount()):
                    quantite = self.table_pieces.item(row, 0).text()
                    description = self.table_pieces.item(row, 2).text()
                    data = self.table_pieces.item(row, 2).data(Qt.ItemDataRole.UserRole)
                    writer.writerow([quantite, description, repr(data)])
            QMessageBox.information(self, "Succès", f"Liste sauvegardée dans\n{chemin_fichier}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Sauvegarde", f"Impossible de sauvegarder le fichier :\n{e}")

    def charger_liste_2d(self):
        chemin_fichier, _ = QFileDialog.getOpenFileName(self, "Charger une liste 2D", "",
                                                        "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
        if not chemin_fichier:
            return
        try:
            with open(chemin_fichier, mode='r', newline='', encoding='utf-8') as f:
                lecteur_csv = csv.reader(f)
                self.table_pieces.setRowCount(0)
                for i, ligne in enumerate(lecteur_csv):
                    if len(ligne) < 3:
                        continue
                    quantite = int(ligne[0])
                    description = ligne[1]
                    piece_data = eval(ligne[2])
                    type_forme = description.split(' - ')[0] if ' - ' in description else "Inconnu"
                    row = self.table_pieces.rowCount()
                    self.table_pieces.insertRow(row)
                    q_item = QTableWidgetItem(str(quantite))
                    f_item = QTableWidgetItem(type_forme)
                    d_item = QTableWidgetItem(description)
                    d_item.setData(Qt.ItemDataRole.UserRole, piece_data)
                    self.table_pieces.setItem(row, 0, q_item)
                    self.table_pieces.setItem(row, 1, f_item)
                    self.table_pieces.setItem(row, 2, d_item)
            QMessageBox.information(self, "Succès", "La liste de pièces a été chargée.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur de Chargement", f"Impossible de lire le fichier :\n{e}")

    def lancer_calcul(self):
        if self.table_pieces.rowCount() == 0:
            QMessageBox.warning(self, "Aucune pièce",
                                "Veuillez ajouter au moins une pièce à la liste.")
            return
        panneau_dims = (self.panel_w.value(), self.panel_h.value())
        largeur_coupe = self.kerf.value()
        pieces_a_creer = []
        for row in range(self.table_pieces.rowCount()):
            quantite = int(self.table_pieces.item(row, 0).text())
            data = self.table_pieces.item(row, 2).data(Qt.ItemDataRole.UserRole)
            if not data:
                continue
            poly = None
            vertices = None
            forme = data.get('forme')
            try:
                if forme == 'rectangle':
                    vertices = creer_trapeze_isocele(data['largeur'], data['largeur'], data['hauteur'])
                elif forme == 'trapeze_isocele':
                    vertices = creer_trapeze_isocele(data['grande_base'], data['petite_base'], data['hauteur'])
                elif forme == 'trapeze_rectangle':
                    vertices = creer_trapeze_rectangle(data['grande_base'], data['petite_base'], data['hauteur'])
                elif forme == 'triangle_equilateral':
                    cote = data['cote']
                    hauteur = (math.sqrt(3) / 2) * cote
                    vertices = [(0, 0), (cote, 0), (cote / 2, hauteur)]
                elif forme == 'triangle_isocele_bh':
                    base = data['base']
                    h = data['hauteur']
                    vertices = [(0, 0), (base, 0), (base / 2, h)]
                elif forme == 'triangle_isocele_sss':
                    s1 = data['cote_egal']
                    base = data['base']
                    if not (2 * s1 > base):
                        raise ValueError("Inégalité triangulaire non respectée")
                        h = math.sqrt(s1 ** 2 - (base / 2) ** 2)
                        vertices = [(0, 0), (base, 0), (base / 2, h)]
                elif forme == 'triangle_rectangle_2c':
                    adj = data.get('adj')
                    opp = data.get('opp')
                    hyp = data.get('hyp')
                    if adj and opp:
                        pass
                    elif adj and hyp:
                        opp = math.sqrt(hyp ** 2 - adj ** 2)
                    elif opp and hyp:
                        adj = math.sqrt(hyp ** 2 - opp ** 2)
                    vertices = [(0, 0), (adj, 0), (0, opp)]
                elif forme == 'triangle_rectangle_1a1c':
                    cote = data['cote']
                    angle_rad = math.radians(data['angle'])
                    type_cote = data['type_cote']
                    if type_cote == 'Adjacent':
                        adj = cote
                        opp = adj * math.tan(angle_rad)
                    elif type_cote == 'Opposé':
                        opp = cote
                        adj = opp / math.tan(angle_rad)
                    elif type_cote == 'Hypoténuse':
                        opp = cote * math.sin(angle_rad)
                        adj = cote * math.cos(angle_rad)
                    vertices = [(0, 0), (adj, 0), (0, opp)]
                elif forme == 'triangle_quelconque_sss':
                    a, b, c = data['a'], data['b'], data['c']
                    if not (a + b > c and a + c > b and b + c > a):
                        raise ValueError("Inégalité triangulaire non respectée")
                    angle_b_rad = math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))
                    vertices = [(0, 0), (c, 0), (a * math.cos(angle_b_rad), a * math.sin(angle_b_rad))]
                elif forme == 'triangle_quelconque_sas':
                    b, c, angle_a_deg = data['b'], data['c'], data['angle_a']
                    angle_a_rad = math.radians(angle_a_deg)
                    vertices = [(0, 0), (c, 0), (b * math.cos(angle_a_rad), b * math.sin(angle_a_rad))]
                elif forme == 'triangle_quelconque_asa':
                    c, angle_a_deg, angle_b_deg = data['c'], data['angle_a'], data['angle_b']
                    if angle_a_deg + angle_b_deg >= 180:
                        raise ValueError("La somme des angles doit être < 180°")
                    angle_a_rad = math.radians(angle_a_deg)
                    angle_b_rad = math.radians(angle_b_deg)
                    angle_c_rad = math.pi - angle_a_rad - angle_b_rad
                    b = c * math.sin(angle_b_rad) / math.sin(angle_c_rad)
                    vertices = [(0, 0), (c, 0), (b * math.cos(angle_a_rad), b * math.sin(angle_a_rad))]
                elif forme == 'cercle':
                    r = data['rayon']
                    poly = Point(r, r).buffer(r, quad_segs=16)
                elif forme == 'ellipse':
                    rx = data['rayon_x']
                    ry = data['rayon_y']
                    cercle_unitaire = Point(rx, ry).buffer(1, quad_segs=16)
                    poly = scale(
                        cercle_unitaire, xfact=rx, yfact=ry)
                if vertices:
                    poly = Polygon(vertices)
                if poly:
                    pieces_a_creer.extend([poly] * quantite)
            except (ValueError, KeyError, ZeroDivisionError) as e:
                QMessageBox.critical(self, "Erreur de Données", f"Erreur de création à la ligne {row + 1}: {e}")
                return
        if not pieces_a_creer:
            QMessageBox.critical(self, "Erreur", "Aucune pièce valide n'a pu être créée.")
            return
        QMessageBox.information(self, "Calcul en cours...", "Le calcul est lancé. L'interface peut se figer.")
        QApplication.processEvents()
        panneaux_finaux = placer_pieces(panneau_dims, pieces_a_creer, largeur_coupe)
        if panneaux_finaux:
            QMessageBox.information(self, "Calcul Terminé",
                                    f"""{len(panneaux_finaux)} panneau(x) nécessaire(s).
Les fichiers de sortie vont être générés.""")
            dessiner_plan_png(panneaux_finaux, panneau_dims[0], panneau_dims[1])
        else:
            QMessageBox.warning(self, "Calcul Terminé", "Aucune solution trouvée.")

    def retour(self):
        self.hide()
        self.retour_au_choix.emit()

    def closeEvent(self, event):
        self.retour_au_choix.show()
        event.accept()


class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # On crée les trois fenêtres une seule fois
        self.selection_dialog = ModeSelectionDialog()
        self.window_1d = Calepinage1DApp()
        self.window_2d = Calepinage2DApp()

        # On connecte les signaux
        self.selection_dialog.btn_1d.clicked.connect(self.show_1d_window)
        self.selection_dialog.btn_2d.clicked.connect(self.show_2d_window)
        self.window_1d.retour_au_choix.connect(self.show_selection_dialog)
        self.window_2d.retour_au_choix.connect(self.show_selection_dialog)

    def run(self):
        self.selection_dialog.show()
        # On lance l'application UNE SEULE FOIS
        sys.exit(self.app.exec())

    def show_1d_window(self):
        self.selection_dialog.hide()
        self.window_1d.show()

    def show_2d_window(self):
        self.selection_dialog.hide()
        self.window_2d.show()

    def show_selection_dialog(self):
        # On s'assure que les autres fenêtres sont bien masquées
        self.window_1d.hide()
        self.window_2d.hide()
        self.selection_dialog.show()


class ModeSelectionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Choisir le type d'optimisation")
        self.selected_mode = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Quel type de calepinage souhaitez-vous effectuer ?"))
        self.btn_1d = QPushButton("Optimisation de Barres (1D)")
        self.btn_1d.clicked.connect(lambda: self.select_mode("1D"))
        self.btn_2d = QPushButton("Optimisation de Panneaux (2D)")
        self.btn_2d.clicked.connect(lambda: self.select_mode("2D"))
        layout.addWidget(self.btn_1d)
        layout.addWidget(self.btn_2d)

    def select_mode(self, mode):
        self.selected_mode = mode
        self.accept()


if __name__ == '__main__':
    # --- PARTIE 1 : LOGIQUE DE CALCUL (Backend) ---

    def calepinage_barres(longueurs_a_decouper, longueur_barre_standard=3000, epaisseur_coupe=0):
        """Optimise la découpe de barres (1D)."""
        longueurs_a_decouper.sort(reverse=True)
        barres_utilisees = []
        for longueur in longueurs_a_decouper:
            place_trouvee = False
            for barre in barres_utilisees:
                longueur_consommee = sum(barre) + (len(barre) * epaisseur_coupe)
                if longueur_consommee + longueur + epaisseur_coupe <= longueur_barre_standard:
                    barre.append(longueur)
                    place_trouvee = True
                    break
            if not place_trouvee:
                if longueur <= longueur_barre_standard:
                    barres_utilisees.append([longueur])
                else:
                    return None,\
                        f"La pièce de {longueur}mm est trop grande pour une barre de {longueur_barre_standard}mm."
        if not barres_utilisees:
            return [], 0
        longueur_totale_utilisee = len(barres_utilisees) * longueur_barre_standard
        longueur_totale_pieces = sum(sum(b) for b in barres_utilisees)
        pertes = longueur_totale_utilisee - longueur_totale_pieces
        pourcentage_perte = (pertes / longueur_totale_utilisee) * 100 if longueur_totale_utilisee > 0 else 0
        return barres_utilisees, pourcentage_perte


    def creer_trapeze_isocele(grande_base, petite_base, hauteur):
        decalage = (grande_base - petite_base) / 2
        return [(0, 0), (grande_base, 0), (grande_base - decalage, hauteur), (decalage, hauteur)]


    def creer_trapeze_rectangle(grande_base, petite_base, hauteur):
        return [(0, 0), (grande_base, 0), (petite_base, hauteur), (0, hauteur)]


    def placer_pieces(panneau_dims, pieces_a_placer, largeur_coupe):
        """Place les pièces 2D sur les panneaux."""
        print("\n📦 Tri des pièces à placer...")
        pieces_a_placer.sort(key=lambda p: p.area, reverse=True)
        panneaux = []
        total_pieces = len(pieces_a_placer)
        for i, piece in enumerate(pieces_a_placer):
            print(f"  -> Placement de la pièce {i + 1}/{total_pieces}...", end='\r')
            piece_placee = False
            for panneau in panneaux:
                resultat = trouver_meilleure_position(panneau, piece, largeur_coupe)
                if resultat:
                    piece_tournee, meilleure_pos = resultat
                    piece_deplacee = translate(piece_tournee, xoff=meilleure_pos[0], yoff=meilleure_pos[1])
                    panneau['pieces_placees'].append(piece_deplacee)
                    piece_placee = True
                    break
            if not piece_placee:
                nouveau_panneau = {'dims': panneau_dims, 'pieces_placees': []}
                resultat = trouver_meilleure_position(nouveau_panneau, piece, largeur_coupe)
                if resultat:
                    piece_tournee, meilleure_pos = resultat
                    piece_deplacee = translate(piece_tournee, xoff=meilleure_pos[0], yoff=meilleure_pos[1])
                    nouveau_panneau['pieces_placees'].append(piece_deplacee)
                    panneaux.append(nouveau_panneau)
                else:
                    print(
                        f"\n⚠️  AVERTISSEMENT : La pièce {i + 1} est trop grande pour un panneau vide et sera ignorée.")
        print("\n\n-> Placement terminé.")
        return panneaux


    def trouver_meilleure_position(panneau, piece, largeur_coupe):
        """Trouve la meilleure position pour une pièce 2D sur un panneau."""
        panneau_poly = Polygon(
            [(0, 0), (panneau['dims'][0], 0), (panneau['dims'][0], panneau['dims'][1]), (0, panneau['dims'][1])])
        pas = 10.0
        for angle in [0, 90, 180, 270]:
            piece_tournee = rotate(piece, angle, origin='center')
            bounds = piece_tournee.bounds
            piece_normalisee = translate(piece_tournee, xoff=-bounds[0], yoff=-bounds[1])
            if piece_normalisee.bounds[2] > panneau['dims'][0] or piece_normalisee.bounds[3] > panneau['dims'][1]:
                continue
            for y in range(0, int(panneau['dims'][1] - piece_normalisee.bounds[3] + pas), int(pas)):
                for x in range(0, int(panneau['dims'][0] - piece_normalisee.bounds[2] + pas), int(pas)):
                    piece_test = translate(piece_normalisee, xoff=x, yoff=y)
                    if not panneau_poly.contains(piece_test):
                        continue
                    position_valide = True
                    for piece_deja_placee in panneau['pieces_placees']:
                        if piece_test.distance(piece_deja_placee) < largeur_coupe:
                            position_valide = False
                            break
                    if position_valide:
                        return piece_normalisee, (x, y)
        return None


    def dessiner_plan_png(panneaux_places, largeur_panneau, hauteur_panneau):
        """Génère les aperçus PNG 2D avec cotes."""
        print("\n🎨 Génération des images PNG avec cotes...")
        for i, panneau in enumerate(panneaux_places):
            try:
                fig, ax = plt.subplots(1, figsize=(15, 10))
                ax.set_aspect('equal', adjustable='box')
                panneau_patch = patches.Rectangle((0, 0), largeur_panneau, hauteur_panneau, linewidth=2,
                                                  edgecolor='black',
                                                  facecolor='whitesmoke')
                ax.add_patch(panneau_patch)
                offset = max(largeur_panneau, hauteur_panneau) * 0.05
                ax.arrow(0, -offset, largeur_panneau, 0, head_width=offset * 0.1, head_length=offset * 0.2, fc='black',
                         ec='black')
                ax.arrow(largeur_panneau, -offset, -largeur_panneau, 0, head_width=offset * 0.1,
                         head_length=offset * 0.2,
                         fc='black', ec='black')
                ax.text(largeur_panneau / 2, -offset * 1.2, f"{largeur_panneau} mm", ha='center', va='bottom',
                        fontsize=10)
                ax.arrow(-offset, 0, 0, hauteur_panneau, head_width=offset * 0.1, head_length=offset * 0.2, fc='black',
                         ec='black')
                ax.arrow(-offset, hauteur_panneau, 0, -hauteur_panneau, head_width=offset * 0.1,
                         head_length=offset * 0.2,
                         fc='black', ec='black')
                ax.text(-offset * 1.2, hauteur_panneau / 2, f"{hauteur_panneau} mm", ha='right', va='center',
                        fontsize=10,
                        rotation='vertical')
                for piece in panneau['pieces_placees']:
                    couleur_piece = f"#{random.randint(0, 0xFFFFFF):06x}"
                    piece_patch = patches.Polygon(list(piece.exterior.coords), closed=True, facecolor=couleur_piece,
                                                  edgecolor='black', alpha=0.8)
                    ax.add_patch(piece_patch)
                    bounds = piece.bounds
                    minx, miny, maxx, maxy = bounds
                    largeur_piece = maxx - minx
                    hauteur_piece = maxy - miny
                    angle_texte = 0
                    if hauteur_piece > largeur_piece:
                        angle_texte = 90
                    centre_piece = piece.centroid
                    annotation = f"L:{largeur_piece:.0f} x H:{hauteur_piece:.0f}\nPos: ({minx:.0f}, {miny:.0f})"
                    ax.text(centre_piece.x, centre_piece.y, annotation, ha='center', va='center', fontsize=7,
                            color='black',
                            weight='bold', rotation=angle_texte)
                ax.set_xlim(-offset * 2, largeur_panneau + offset)
                ax.set_ylim(-offset * 2, hauteur_panneau + offset)
                ax.invert_yaxis()
                ax.set_title(f"Aperçu avec Cotes - Panneau N°{i + 1}", fontsize=14)
                ax.set_xlabel("Largeur (mm)")
                ax.set_ylabel("Hauteur (mm)")
                plt.grid(True, linestyle='--', alpha=0.6)
                nom_fichier = f"plan_final_2D_{i + 1}_cotes.png"
                plt.savefig(nom_fichier, dpi=200, bbox_inches='tight')
                plt.close(fig)
                print(f"✅ Image avec cotes du panneau {i + 1} sauvegardée : {nom_fichier}")
            except Exception as e:
                print(f"❌ Erreur lors de la génération du PNG {i + 1}: {e}")


    class Calepinage1DApp(QMainWindow):

        retour_au_choix = pyqtSignal()

        def __init__(self):
            super().__init__()
            self.setWindowTitle("Optimisation de Découpe de Barres (1D)")
            self.setGeometry(150, 150, 800, 700)
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            main_layout = QVBoxLayout(central_widget)
            params_layout = QGridLayout()
            params_layout.addWidget(QLabel("<b>Longueur standard (mm):</b>"), 0, 0)
            self.longueur_standard = QDoubleSpinBox(minimum=100, maximum=20000, value=6000, singleStep=100)
            params_layout.addWidget(self.longueur_standard, 0, 1)
            params_layout.addWidget(QLabel("<b>Épaisseur lame (mm):</b>"), 1, 0)
            self.epaisseur_lame = QDoubleSpinBox(minimum=0, maximum=100, value=3)
            params_layout.addWidget(self.epaisseur_lame, 1, 1)
            main_layout.addLayout(params_layout)
            main_layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))
            saisie_layout = QHBoxLayout()
            saisie_layout.addWidget(QLabel("Longueur:"))
            self.longueur_piece = QDoubleSpinBox(minimum=1, maximum=20000, value=500)
            saisie_layout.addWidget(self.longueur_piece)
            saisie_layout.addWidget(QLabel("Quantité:"))
            self.quantite_piece = QSpinBox(minimum=1, maximum=1000, value=1)
            saisie_layout.addWidget(self.quantite_piece)
            self.btn_ajouter_1d = QPushButton("Ajouter")
            saisie_layout.addWidget(self.btn_ajouter_1d)
            main_layout.addLayout(saisie_layout)
            self.table_pieces_1d = QTableWidget()
            self.table_pieces_1d.setColumnCount(2)
            self.table_pieces_1d.setHorizontalHeaderLabels(["Longueur", "Quantité"])
            self.table_pieces_1d.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            main_layout.addWidget(self.table_pieces_1d)
            gestion_liste_layout = QHBoxLayout()
            self.btn_charger_1d = QPushButton("Charger...")
            gestion_liste_layout.addWidget(self.btn_charger_1d)
            self.btn_sauvegarder_1d = QPushButton("Sauvegarder...")
            gestion_liste_layout.addWidget(self.btn_sauvegarder_1d)
            gestion_liste_layout.addStretch()
            self.btn_supprimer_1d = QPushButton("Supprimer")
            gestion_liste_layout.addWidget(self.btn_supprimer_1d)
            main_layout.addLayout(gestion_liste_layout)
            self.btn_calculer_1d = QPushButton("Lancer le Calcul")
            self.btn_calculer_1d.setStyleSheet(
                "background-color: #008CBA; color: white; font-weight: bold; padding: 10px;")
            main_layout.addWidget(self.btn_calculer_1d)
            main_layout.addWidget(QLabel("<b>Résultats :</b>"))
            self.resultats_text = QPlainTextEdit()
            self.resultats_text.setReadOnly(True)
            self.resultats_text.setStyleSheet("font-family: Consolas, Courier New;")
            main_layout.addWidget(self.resultats_text)
            btn_retour = QPushButton("Retour au Choix du Mode")
            main_layout.addWidget(btn_retour)
            self.btn_ajouter_1d.clicked.connect(self.ajouter_piece_1d)
            self.btn_supprimer_1d.clicked.connect(self.supprimer_piece_1d)
            self.btn_calculer_1d.clicked.connect(self.lancer_calcul_1d)
            self.btn_charger_1d.clicked.connect(self.charger_liste_1d)
            self.btn_sauvegarder_1d.clicked.connect(self.sauvegarder_liste_1d)
            btn_retour.clicked.connect(self.retour)

        def ajouter_piece_1d(self):
            longueur = self.longueur_piece.value()
            quantite = self.quantite_piece.value()
            row = self.table_pieces_1d.rowCount()
            self.table_pieces_1d.insertRow(row)
            self.table_pieces_1d.setItem(row, 0, QTableWidgetItem(str(longueur)))
            self.table_pieces_1d.setItem(row, 1, QTableWidgetItem(str(quantite)))

        def supprimer_piece_1d(self):
            selected_row = self.table_pieces_1d.currentRow()
            if selected_row >= 0:
                self.table_pieces_1d.removeRow(selected_row)

        def sauvegarder_liste_1d(self):
            if self.table_pieces_1d.rowCount() == 0:
                QMessageBox.warning(self, "Liste Vide", "Il n'y a aucune pièce à sauvegarder.")
                return
            chemin_fichier, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la liste 1D", "",
                                                            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
            if not chemin_fichier:
                return
            try:
                with open(chemin_fichier, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['longueur', 'quantite'])
                    for row in range(self.table_pieces_1d.rowCount()):
                        writer.writerow(
                            [self.table_pieces_1d.item(row, 0).text(), self.table_pieces_1d.item(row, 1).text()])
                QMessageBox.information(self, "Succès", f"Liste sauvegardée dans\n{chemin_fichier}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur de Sauvegarde", f"Impossible de sauvegarder le fichier :\n{e}")

        def charger_liste_1d(self):
            chemin_fichier, _ = QFileDialog.getOpenFileName(self, "Charger une liste 1D", "",
                                                            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
            if not chemin_fichier:
                return
            try:
                with open(chemin_fichier, mode='r', newline='', encoding='utf-8') as f:
                    lecteur = csv.reader(f)
                    next(lecteur, None)
                    self.table_pieces_1d.setRowCount(0)
                    for ligne in lecteur:
                        if len(ligne) == 2:
                            longueur, quantite = ligne
                            row = self.table_pieces_1d.rowCount()
                            self.table_pieces_1d.insertRow(row)
                            self.table_pieces_1d.setItem(row, 0, QTableWidgetItem(longueur))
                            self.table_pieces_1d.setItem(row, 1, QTableWidgetItem(quantite))
                QMessageBox.information(self, "Succès", "La liste a été chargée.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur de Chargement", f"Impossible de lire le fichier :\n{e}")

        def lancer_calcul_1d(self):
            if self.table_pieces_1d.rowCount() == 0:
                QMessageBox.warning(self, "Aucune pièce",
                                    "Veuillez ajouter au moins une pièce.")
                return
            longueur_barre = self.longueur_standard.value()
            epaisseur_coupe = self.epaisseur_lame.value()
            liste_pieces = []
            for row in range(self.table_pieces_1d.rowCount()):
                liste_pieces.extend(
                    [float(self.table_pieces_1d.item(row, 0).text())] * int(self.table_pieces_1d.item(row, 1).text()))
            plan, perte = calepinage_barres(liste_pieces, longueur_barre, epaisseur_coupe)
            if plan is None:
                QMessageBox.critical(self, "Erreur de Calcul", perte)
                return
            output = [f"--- PLAN DE DÉCOUPE OPTIMISÉ ---",
                      f"Longueur barre: {longueur_barre} mm, Épaisseur lame: {epaisseur_coupe} mm\n"]
            for i, barre in enumerate(plan):
                longueur_pieces = sum(barre)
                cout_coupes = len(barre) * epaisseur_coupe
                longueur_consommee = longueur_pieces + cout_coupes
                chute = longueur_barre - longueur_consommee
                output.extend(
                    [f"** Barre n°{i + 1} **", f"  Découpes : {barre}", f"  Consommé : {longueur_consommee:.2f} mm",
                     f"  Chute : {chute:.2f} mm", "-" * 30])
            output.extend([f"\n✅ Total barres à utiliser : {len(plan)}", f"📉 Perte totale : {perte:.2f}%"])
            self.resultats_text.setPlainText("\n".join(output))

        def retour(self):
            self.hide()  # On masque la fenêtre au lieu de la fermer
            self.retour_au_choix.emit()  # On envoie un signal


    class Calepinage2DApp(QMainWindow):
        retour_au_choix = pyqtSignal()
        """Interface graphique pour l'optimisation de panneaux (2D)."""

        def __init__(self):
            super().__init__()
            self.btn_calculer = None
            self.btn_sauvegarder = None
            self.btn_charger = None
            self.btn_supprimer = None
            self.table_pieces = None
            self.btn_ajouter = None
            self.spin_quantite = None
            self.stacked_widget_main = None
            self.combo_forme_principale = None
            self.kerf = None
            self.panel_h = None
            self.panel_w = None
            self.setWindowTitle("Optimisation de Découpe de Panneaux (2D)")
            self.setGeometry(100, 100, 1100, 800)
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)
            self.creer_panneau_parametres()
            top_layout = QHBoxLayout()
            self.creer_panneau_saisie(top_layout)
            self.creer_panneau_liste(top_layout)
            self.main_layout.addLayout(top_layout)
            self.creer_panneau_actions()
            self.btn_retour = QPushButton("Retour au Choix du Mode")
            self.main_layout.addWidget(self.btn_retour)
            self.connect_signals()

        def creer_panneau_parametres(self):
            params_widget = QFrame()
            params_widget.setFrameShape(QFrame.Shape.StyledPanel)
            params_layout = QHBoxLayout(params_widget)
            params_layout.addWidget(QLabel("<b>Paramètres Généraux (Panneau 2D) :</b>"))
            params_layout.addWidget(QLabel("L. Panneau:"))
            self.panel_w = QDoubleSpinBox(minimum=100, maximum=10000, value=2500, singleStep=100)
            params_layout.addWidget(self.panel_w)
            params_layout.addWidget(QLabel("H. Panneau:"))
            self.panel_h = QDoubleSpinBox(minimum=100, maximum=10000, value=1250, singleStep=100)
            params_layout.addWidget(self.panel_h)
            params_layout.addWidget(QLabel("L. Lame:"))
            self.kerf = QDoubleSpinBox(minimum=0, maximum=100, value=3)
            params_layout.addWidget(self.kerf)
            self.main_layout.addWidget(params_widget)

        def creer_panneau_saisie(self, parent_layout):
            saisie_widget = QWidget()
            saisie_layout = QVBoxLayout(saisie_widget)
            saisie_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            saisie_layout.addWidget(QLabel("<b>1. Choisir la catégorie :</b>"))
            self.combo_forme_principale = QComboBox()
            self.combo_forme_principale.addItems(["Rectangle", "Trapèze", "Triangle", "Forme Circulaire"])
            saisie_layout.addWidget(self.combo_forme_principale)
            self.stacked_widget_main = QStackedWidget()
            self.stacked_widget_main.addWidget(self._create_rectangle_page())
            self.stacked_widget_main.addWidget(self._create_trapeze_page())
            self.stacked_widget_main.addWidget(self._create_triangle_page())
            self.stacked_widget_main.addWidget(self._create_circulaire_page())
            saisie_layout.addWidget(QLabel("<b>2. Définir la pièce :</b>"))
            saisie_layout.addWidget(self.stacked_widget_main)
            saisie_layout.addWidget(QLabel("<b>3. Quantité :</b>"))
            self.spin_quantite = QSpinBox(minimum=1, maximum=1000, value=1)
            saisie_layout.addWidget(self.spin_quantite)
            self.btn_ajouter = QPushButton("Ajouter à la liste →")
            self.btn_ajouter.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
            saisie_layout.addWidget(self.btn_ajouter)
            parent_layout.addWidget(saisie_widget, 2)

        def _create_rectangle_page(self):
            page = QWidget()
            layout = QGridLayout(page)
            layout.setContentsMargins(0, 10, 0, 0)
            layout.addWidget(QLabel("Largeur (mm):"), 0, 0)
            self.rect_largeur = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
            layout.addWidget(self.rect_largeur, 0, 1)
            layout.addWidget(QLabel("Hauteur (mm):"), 1, 0)
            self.rect_hauteur = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
            layout.addWidget(self.rect_hauteur, 1, 1)
            return page

        def _create_trapeze_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(0, 10, 0, 0)
            combo = QComboBox()
            combo.addItems(["Isocèle", "Rectangle"])
            layout.addWidget(QLabel("Type de Trapèze :"))
            layout.addWidget(combo)
            stacked = QStackedWidget()
            sub_iso = QWidget()
            l_iso = QGridLayout(sub_iso)
            l_iso.addWidget(QLabel("Grande Base:"), 0, 0)
            self.trap_iso_gb = QDoubleSpinBox(minimum=1, maximum=10000, value=600)
            l_iso.addWidget(self.trap_iso_gb, 0, 1)
            l_iso.addWidget(QLabel("Petite Base:"), 1, 0)
            self.trap_iso_pb = QDoubleSpinBox(minimum=1, maximum=10000, value=400)
            l_iso.addWidget(self.trap_iso_pb, 1, 1)
            l_iso.addWidget(QLabel("Hauteur:"), 2, 0)
            self.trap_iso_h = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
            l_iso.addWidget(self.trap_iso_h, 2, 1)
            stacked.addWidget(sub_iso)
            sub_rect = QWidget()
            l_rect = QGridLayout(sub_rect)
            l_rect.addWidget(QLabel("Grande Base:"), 0, 0)
            self.trap_rect_gb = QDoubleSpinBox(minimum=1, maximum=10000, value=650)
            l_rect.addWidget(self.trap_rect_gb, 0, 1)
            l_rect.addWidget(QLabel("Petite Base:"), 1, 0)
            self.trap_rect_pb = QDoubleSpinBox(minimum=1, maximum=10000, value=450)
            l_rect.addWidget(self.trap_rect_pb, 1, 1)
            l_rect.addWidget(QLabel("Hauteur:"), 2, 0)
            self.trap_rect_h = QDoubleSpinBox(minimum=1, maximum=10000, value=350)
            l_rect.addWidget(self.trap_rect_h, 2, 1)
            stacked.addWidget(sub_rect)
            layout.addWidget(stacked)
            combo.currentIndexChanged.connect(stacked.setCurrentIndex)
            page.setProperty("combo", combo)
            return page

        def _create_triangle_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(0, 10, 0, 0)
            self.combo_tri_type = QComboBox()
            self.combo_tri_type.addItems(["Équilatéral", "Isocèle", "Rectangle", "Quelconque"])
            layout.addWidget(QLabel("Type de Triangle :"))
            layout.addWidget(self.combo_tri_type)
            self.stacked_tri = QStackedWidget()
            sub_equi = QWidget()
            l_equi = QGridLayout(sub_equi)
            l_equi.addWidget(QLabel("Côté (mm):"), 0, 0)
            self.tri_equi_cote = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
            l_equi.addWidget(self.tri_equi_cote, 0, 1)
            self.stacked_tri.addWidget(sub_equi)
            sub_iso = QWidget()
            l_iso = QVBoxLayout(sub_iso)
            self.combo_tri_iso_methode = QComboBox()
            self.combo_tri_iso_methode.addItems(["Par base et hauteur", "Par 3 côtés"])
            l_iso.addWidget(QLabel("Méthode :"))
            l_iso.addWidget(self.combo_tri_iso_methode)
            self.stacked_tri_iso = QStackedWidget()
            page_iso_bh = QWidget()
            l_iso_bh = QGridLayout(page_iso_bh)
            l_iso_bh.addWidget(QLabel("Base:"), 0, 0)
            self.tri_iso_base = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
            l_iso_bh.addWidget(self.tri_iso_base, 0, 1)
            l_iso_bh.addWidget(QLabel("Hauteur:"), 1, 0)
            self.tri_iso_hauteur = QDoubleSpinBox(minimum=1, maximum=10000, value=400)
            l_iso_bh.addWidget(self.tri_iso_hauteur, 1, 1)
            self.stacked_tri_iso.addWidget(page_iso_bh)
            page_iso_sss = QWidget()
            l_iso_sss = QGridLayout(page_iso_sss)
            l_iso_sss.addWidget(QLabel("Côté égal 1:"), 0, 0)
            self.tri_iso_s1 = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
            l_iso_sss.addWidget(self.tri_iso_s1, 0, 1)
            l_iso_sss.addWidget(QLabel("Côté égal 2:"), 1, 0)
            self.tri_iso_s2 = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
            l_iso_sss.addWidget(self.tri_iso_s2, 1, 1)
            l_iso_sss.addWidget(QLabel("Base:"), 2, 0)
            self.tri_iso_s3 = QDoubleSpinBox(minimum=1, maximum=10000, value=300)
            l_iso_sss.addWidget(self.tri_iso_s3, 2, 1)
            self.stacked_tri_iso.addWidget(page_iso_sss)
            l_iso.addWidget(self.stacked_tri_iso)
            self.combo_tri_iso_methode.currentIndexChanged.connect(self.stacked_tri_iso.setCurrentIndex)
            self.stacked_tri.addWidget(sub_iso)
            sub_rect = QWidget()
            l_rect = QVBoxLayout(sub_rect)
            self.combo_tri_rect_methode = QComboBox()
            self.combo_tri_rect_methode.addItems(["Par 2 côtés", "Par 1 côté et 1 angle"])
            l_rect.addWidget(QLabel("Méthode :"))
            l_rect.addWidget(self.combo_tri_rect_methode)
            self.stacked_tri_rect = QStackedWidget()
            page_rect_2c = QWidget()
            l_rect_2c = QGridLayout(page_rect_2c)
            l_rect_2c.addWidget(QLabel("Remplissez 2 des 3 champs :"), 0, 0, 1, 2)
            l_rect_2c.addWidget(QLabel("Adjacent:"), 1, 0)
            self.tri_rect_2c_adj = QDoubleSpinBox(minimum=0, maximum=10000, value=300)
            self.tri_rect_2c_adj.setSpecialValueText(" ")
            l_rect_2c.addWidget(self.tri_rect_2c_adj, 1, 1)
            l_rect_2c.addWidget(QLabel("Opposé:"), 2, 0)
            self.tri_rect_2c_opp = QDoubleSpinBox(minimum=0, maximum=10000, value=400)
            self.tri_rect_2c_opp.setSpecialValueText(" ")
            l_rect_2c.addWidget(self.tri_rect_2c_opp, 2, 1)
            l_rect_2c.addWidget(QLabel("Hypoténuse:"), 3, 0)
            self.tri_rect_2c_hyp = QDoubleSpinBox(minimum=0, maximum=10000, value=0)
            self.tri_rect_2c_hyp.setSpecialValueText(" ")
            l_rect_2c.addWidget(self.tri_rect_2c_hyp, 3, 1)
            self.stacked_tri_rect.addWidget(page_rect_2c)
            page_rect_1a = QWidget()
            l_rect_1a = QGridLayout(page_rect_1a)
            l_rect_1a.addWidget(QLabel("Côté connu:"), 0, 0)
            self.tri_rect_1a_cote = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
            l_rect_1a.addWidget(self.tri_rect_1a_cote, 0, 1)
            l_rect_1a.addWidget(QLabel("Angle (degrés):"), 1, 0)
            self.tri_rect_1a_angle = QDoubleSpinBox(minimum=1, maximum=89, value=30)
            l_rect_1a.addWidget(self.tri_rect_1a_angle, 1, 1)
            self.combo_rect_1a_type = QComboBox()
            self.combo_rect_1a_type.addItems(["Adjacent", "Opposé", "Hypoténuse"])
            l_rect_1a.addWidget(self.combo_rect_1a_type, 2, 0, 1, 2)
            self.stacked_tri_rect.addWidget(page_rect_1a)
            l_rect.addWidget(self.stacked_tri_rect)
            self.combo_tri_rect_methode.currentIndexChanged.connect(self.stacked_tri_rect.setCurrentIndex)
            self.stacked_tri.addWidget(sub_rect)
            sub_quel = QWidget()
            l_quel = QVBoxLayout(sub_quel)
            self.combo_tri_quel_methode = QComboBox()
            self.combo_tri_quel_methode.addItems(
                ["Par 3 côtés (SSS)", "Par 2 côtés et 1 angle (SAS)", "Par 1 côté et 2 angles (ASA)"])
            l_quel.addWidget(QLabel("Méthode :"))
            l_quel.addWidget(self.combo_tri_quel_methode)
            self.stacked_tri_quel = QStackedWidget()
            page_quel_sss = QWidget()
            l_quel_sss = QGridLayout(page_quel_sss)
            l_quel_sss.addWidget(QLabel("Côté A:"), 0, 0)
            self.tri_quel_sss_a = QDoubleSpinBox(minimum=1, maximum=10000, value=500)
            l_quel_sss.addWidget(self.tri_quel_sss_a, 0, 1)
            l_quel_sss.addWidget(QLabel("Côté B:"), 1, 0)
            self.tri_quel_sss_b = QDoubleSpinBox(minimum=1, maximum=10000, value=600)
            l_quel_sss.addWidget(self.tri_quel_sss_b, 1, 1)
            l_quel_sss.addWidget(QLabel("Côté C:"), 2, 0)
            self.tri_quel_sss_c = QDoubleSpinBox(minimum=1, maximum=10000, value=700)
            l_quel_sss.addWidget(self.tri_quel_sss_c, 2, 1)
            self.stacked_tri_quel.addWidget(page_quel_sss)
            page_quel_sas = QWidget()
            l_quel_sas = QGridLayout(page_quel_sas)
            l_quel_sas.addWidget(QLabel("Côté B:"), 0, 0)
            self.tri_quel_sas_b = QDoubleSpinBox(minimum=1, maximum=10000, value=600)
            l_quel_sas.addWidget(self.tri_quel_sas_b, 0, 1)
            l_quel_sas.addWidget(QLabel("Côté C:"), 1, 0)
            self.tri_quel_sas_c = QDoubleSpinBox(minimum=1, maximum=10000, value=700)
            l_quel_sas.addWidget(self.tri_quel_sas_c, 1, 1)
            l_quel_sas.addWidget(QLabel("Angle A inclus (°):"), 2, 0)
            self.tri_quel_sas_angle = QDoubleSpinBox(minimum=1, maximum=179, value=45)
            l_quel_sas.addWidget(self.tri_quel_sas_angle, 2, 1)
            self.stacked_tri_quel.addWidget(page_quel_sas)
            page_quel_asa = QWidget()
            l_quel_asa = QGridLayout(page_quel_asa)
            l_quel_asa.addWidget(QLabel("Côté C:"), 0, 0)
            self.tri_quel_asa_c = QDoubleSpinBox(minimum=1, maximum=10000, value=700)
            l_quel_asa.addWidget(self.tri_quel_asa_c, 0, 1)
            l_quel_asa.addWidget(QLabel("Angle A adj. (°):"), 1, 0)
            self.tri_quel_asa_angle_a = QDoubleSpinBox(minimum=1, maximum=178, value=45)
            l_quel_asa.addWidget(self.tri_quel_asa_angle_a, 1, 1)
            l_quel_asa.addWidget(QLabel("Angle B adj. (°):"), 2, 0)
            self.tri_quel_asa_angle_b = QDoubleSpinBox(minimum=1, maximum=178, value=65)
            l_quel_asa.addWidget(self.tri_quel_asa_angle_b, 2, 1)
            self.stacked_tri_quel.addWidget(page_quel_asa)
            l_quel.addWidget(self.stacked_tri_quel)
            self.combo_tri_quel_methode.currentIndexChanged.connect(self.stacked_tri_quel.setCurrentIndex)
            self.stacked_tri.addWidget(sub_quel)
            layout.addWidget(self.stacked_tri)
            self.combo_tri_type.currentIndexChanged.connect(self.stacked_tri.setCurrentIndex)
            return page

        def _create_circulaire_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(0, 10, 0, 0)
            combo = QComboBox()
            combo.addItems(["Cercle", "Ellipse"])
            layout.addWidget(QLabel("Type de Forme :"))
            layout.addWidget(combo)
            stacked = QStackedWidget()
            sub_cercle = QWidget()
            l_cercle = QGridLayout(sub_cercle)
            l_cercle.addWidget(QLabel("Rayon (mm):"), 0, 0)
            self.cercle_rayon = QDoubleSpinBox(minimum=1, maximum=5000, value=250)
            l_cercle.addWidget(self.cercle_rayon, 0, 1)
            stacked.addWidget(sub_cercle)
            sub_ellipse = QWidget()
            l_ellipse = QGridLayout(sub_ellipse)
            l_ellipse.addWidget(QLabel("Rayon X (mm):"), 0, 0)
            self.ellipse_rx = QDoubleSpinBox(minimum=1, maximum=5000, value=300)
            l_ellipse.addWidget(self.ellipse_rx, 0, 1)
            l_ellipse.addWidget(QLabel("Rayon Y (mm):"), 1, 0)
            self.ellipse_ry = QDoubleSpinBox(minimum=1, maximum=5000, value=200)
            l_ellipse.addWidget(self.ellipse_ry, 1, 1)
            stacked.addWidget(sub_ellipse)
            layout.addWidget(stacked)
            combo.currentIndexChanged.connect(stacked.setCurrentIndex)
            page.setProperty("combo", combo)
            return page

        def creer_panneau_liste(self, parent_layout):
            liste_widget = QWidget()
            liste_layout = QVBoxLayout(liste_widget)
            liste_layout.addWidget(QLabel("<b>Liste des Pièces à Découper :</b>"))
            self.table_pieces = QTableWidget()
            self.table_pieces.setColumnCount(3)
            self.table_pieces.setHorizontalHeaderLabels(["Quantité", "Type", "Description"])
            self.table_pieces.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.table_pieces.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.table_pieces.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            liste_layout.addWidget(self.table_pieces)
            btn_layout = QHBoxLayout()
            self.btn_supprimer = QPushButton("Supprimer la sélection")
            self.btn_supprimer.setEnabled(False)
            btn_layout.addWidget(self.btn_supprimer)
            liste_layout.addLayout(btn_layout)
            parent_layout.addWidget(liste_widget, 3)

        def creer_panneau_actions(self):
            actions_widget = QFrame()
            actions_widget.setFrameShape(QFrame.Shape.StyledPanel)
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.btn_charger = QPushButton("Charger...")
            self.btn_sauvegarder = QPushButton("Sauvegarder...")
            self.btn_calculer = QPushButton("LANCER LE CALCUL")
            self.btn_calculer.setStyleSheet(
                "background-color: #008CBA; color: white; font-weight: bold; padding: 15px;")
            actions_layout.addWidget(self.btn_charger)
            actions_layout.addWidget(self.btn_sauvegarder)
            actions_layout.addStretch()
            actions_layout.addWidget(self.btn_calculer)
            self.main_layout.addWidget(actions_widget)

        def connect_signals(self):
            self.combo_forme_principale.currentIndexChanged.connect(self.stacked_widget_main.setCurrentIndex)
            self.btn_ajouter.clicked.connect(self.ajouter_piece)
            self.btn_supprimer.clicked.connect(self.supprimer_piece)
            self.table_pieces.itemSelectionChanged.connect(self.maj_boutons_liste)
            self.btn_calculer.clicked.connect(self.lancer_calcul)
            self.btn_charger.clicked.connect(self.charger_liste_2d)
            self.btn_sauvegarder.clicked.connect(self.sauvegarder_liste_2d)
            self.btn_retour.clicked.connect(self.retour)

        def ajouter_piece(self):
            forme_principale = self.combo_forme_principale.currentText()
            quantite = self.spin_quantite.value()
            description = "Erreur de saisie"
            piece_data = {}
            valide = True
            if forme_principale == "Rectangle":
                largeur = self.rect_largeur.value()
                hauteur = self.rect_hauteur.value()
                description = f"Rectangle - L: {largeur}, H: {hauteur}"
                piece_data = {'forme': 'rectangle', 'largeur': largeur, 'hauteur': hauteur}
            elif forme_principale == "Trapèze":
                page = self.stacked_widget_main.currentWidget()
                combo = page.property("combo")
                type_forme = combo.currentText()
                if type_forme == "Isocèle":
                    gb = self.trap_iso_gb.value()
                    pb = self.trap_iso_pb.value()
                    h = self.trap_iso_h.value()
                    description = f"Trapèze Isocèle - GB: {gb}, PB: {pb}, H: {h}"
                    piece_data = {'forme': 'trapeze_isocele', 'grande_base': gb, 'petite_base': pb, 'hauteur': h}
                elif type_forme == "Rectangle":
                    gb = self.trap_rect_gb.value()
                    pb = self.trap_rect_pb.value()
                    h = self.trap_rect_h.value()
                    description = f"Trapèze Rectangle - GB: {gb}, PB: {pb}, H: {h}"
                    piece_data = {'forme': 'trapeze_rectangle', 'grande_base': gb, 'petite_base': pb, 'hauteur': h}
            elif forme_principale == "Triangle":
                type_tri = self.combo_tri_type.currentText()
                if type_tri == "Équilatéral":
                    cote = self.tri_equi_cote.value()
                    description = f"T. Équilatéral - Côté: {cote}"
                    piece_data = {'forme': 'triangle_equilateral', 'cote': cote}
                elif type_tri == "Isocèle":
                    methode = self.combo_tri_iso_methode.currentText()
                    if "base et hauteur" in methode:
                        base = self.tri_iso_base.value()
                        h = self.tri_iso_hauteur.value()
                        description = f"T. Isocèle (B/H) - B: {base}, H: {h}"
                        piece_data = {'forme': 'triangle_isocele_bh', 'base': base, 'hauteur': h}
                    else:
                        s1 = self.tri_iso_s1.value()
                        s2 = self.tri_iso_s2.value()
                        s3 = self.tri_iso_s3.value()
                        if s1 != s2:
                            QMessageBox.warning(self, "Erreur",
                                                "Les deux côtés égaux doivent avoir la même longueur.")
                            valide = False
                        description = f"T. Isocèle (SSS) - Côtés: {s1}, {s1}, {s3}"
                        piece_data = {'forme': 'triangle_isocele_sss', 'cote_egal': s1, 'base': s3}
                elif type_tri == "Rectangle":
                    methode = self.combo_tri_rect_methode.currentText()
                    if "2 côtés" in methode:
                        adj = self.tri_rect_2c_adj.value()
                        opp = self.tri_rect_2c_opp.value()
                        hyp = self.tri_rect_2c_hyp.value()
                        sides = {'adj': adj, 'opp': opp, 'hyp': hyp}
                        known_sides = {k: v for k, v in sides.items() if v > 0}
                        if len(known_sides) != 2:
                            QMessageBox.warning(self, "Erreur",
                                                "Veuillez remplir exactement 2 des 3 champs.")
                            valide = False
                        description = f"T. Rectangle (2C) - {', '.join([f'{k.capitalize()}:{v}' for k, v in known_sides.items()])}"
                        piece_data = {'forme': 'triangle_rectangle_2c', **known_sides}
                    else:
                        cote = self.tri_rect_1a_cote.value()
                        angle = self.tri_rect_1a_angle.value()
                        type_cote = self.combo_rect_1a_type.currentText()
                        description = f"T. Rectangle (1A1C) - Côté({type_cote}): {cote}, Angle: {angle}°"
                        piece_data = {'forme': 'triangle_rectangle_1a1c', 'cote': cote, 'angle': angle,
                                      'type_cote': type_cote}
                elif type_tri == "Quelconque":
                    methode = self.combo_tri_quel_methode.currentText()
                    if "SSS" in methode:
                        a = self.tri_quel_sss_a.value()
                        b = self.tri_quel_sss_b.value()
                        c = self.tri_quel_sss_c.value()
                        description = f"T. Quelconque (SSS) - Côtés: {a}, {b}, {c}"
                        piece_data = {'forme': 'triangle_quelconque_sss', 'a': a, 'b': b, 'c': c}
                    elif "SAS" in methode:
                        b = self.tri_quel_sas_b.value()
                        c = self.tri_quel_sas_c.value()
                        angle = self.tri_quel_sas_angle.value()
                        description = f"T. Quelconque (SAS) - B: {b}, C: {c}, Angle A: {angle}°"
                        piece_data = {'forme': 'triangle_quelconque_sas', 'b': b, 'c': c, 'angle_a': angle}
                    elif "ASA" in methode:
                        c = self.tri_quel_asa_c.value()
                        angle_a = self.tri_quel_asa_angle_a.value()
                        angle_b = self.tri_quel_asa_angle_b.value()
                        description = f"T. Quelconque (ASA) - Côté C: {c}, Angle A: {angle_a}°, Angle B: {angle_b}°"
                        piece_data = {'forme': 'triangle_quelconque_asa', 'c': c, 'angle_a': angle_a,
                                      'angle_b': angle_b}
            elif forme_principale == "Forme Circulaire":
                page = self.stacked_widget_main.currentWidget()
                combo_circ = page.property("combo")
                type_circ = combo_circ.currentText()
                if type_circ == "Cercle":
                    rayon = self.cercle_rayon.value()
                    description = f"Cercle - Rayon: {rayon}"
                    piece_data = {'forme': 'cercle', 'rayon': rayon}
                elif type_circ == "Ellipse":
                    rx = self.ellipse_rx.value()
                    ry = self.ellipse_ry.value()
                    description = f"Ellipse - Rayons: {rx}x{ry}"
                    piece_data = {'forme': 'ellipse', 'rayon_x': rx, 'rayon_y': ry}

            if valide:
                row = self.table_pieces.rowCount()
                self.table_pieces.insertRow(row)
                q_item = QTableWidgetItem(str(quantite))
                d_item = QTableWidgetItem(description)
                type_item_text = description.split(' - ')[0] if ' - ' in description else forme_principale
                f_item = QTableWidgetItem(type_item_text)
                d_item.setData(Qt.ItemDataRole.UserRole, piece_data)
                self.table_pieces.setItem(row, 0, q_item)
                self.table_pieces.setItem(row, 1, f_item)
                self.table_pieces.setItem(row, 2, d_item)

        def supprimer_piece(self):
            selected_row = self.table_pieces.currentRow()
            if selected_row >= 0:
                self.table_pieces.removeRow(selected_row)

        def maj_boutons_liste(self):
            self.btn_supprimer.setEnabled(bool(self.table_pieces.selectedItems()))

        def sauvegarder_liste_2d(self):
            if self.table_pieces.rowCount() == 0:
                QMessageBox.warning(self, "Liste Vide", "Il n'y a aucune pièce à sauvegarder.")
                return
            chemin_fichier, _ = QFileDialog.getSaveFileName(self, "Sauvegarder la liste 2D", "",
                                                            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
            if not chemin_fichier:
                return
            try:
                with open(chemin_fichier, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in range(self.table_pieces.rowCount()):
                        quantite = self.table_pieces.item(row, 0).text()
                        description = self.table_pieces.item(row, 2).text()
                        data = self.table_pieces.item(row, 2).data(Qt.ItemDataRole.UserRole)
                        writer.writerow([quantite, description, repr(data)])
                QMessageBox.information(self, "Succès", f"Liste sauvegardée dans\n{chemin_fichier}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur de Sauvegarde", f"Impossible de sauvegarder le fichier :\n{e}")

        def charger_liste_2d(self):
            chemin_fichier, _ = QFileDialog.getOpenFileName(self, "Charger une liste 2D", "",
                                                            "Fichiers CSV (*.csv);;Tous les fichiers (*.*)")
            if not chemin_fichier:
                return
            try:
                with open(chemin_fichier, mode='r', newline='', encoding='utf-8') as f:
                    lecteur_csv = csv.reader(f)
                    self.table_pieces.setRowCount(0)
                    for i, ligne in enumerate(lecteur_csv):
                        if len(ligne) < 3:
                            continue
                        quantite = int(ligne[0])
                        description = ligne[1]
                        piece_data = eval(ligne[2])
                        type_forme = description.split(' - ')[0] if ' - ' in description else "Inconnu"
                        row = self.table_pieces.rowCount()
                        self.table_pieces.insertRow(row)
                        q_item = QTableWidgetItem(str(quantite))
                        f_item = QTableWidgetItem(type_forme)
                        d_item = QTableWidgetItem(description)
                        d_item.setData(Qt.ItemDataRole.UserRole, piece_data)
                        self.table_pieces.setItem(row, 0, q_item)
                        self.table_pieces.setItem(row, 1, f_item)
                        self.table_pieces.setItem(row, 2, d_item)
                QMessageBox.information(self, "Succès", "La liste de pièces a été chargée.")
            except Exception as e:
                QMessageBox.critical(self, "Erreur de Chargement", f"Impossible de lire le fichier :\n{e}")

        def lancer_calcul(self):
            if self.table_pieces.rowCount() == 0:
                QMessageBox.warning(self, "Aucune pièce",
                                    "Veuillez ajouter au moins une pièce à la liste.")
                return
            panneau_dims = (self.panel_w.value(), self.panel_h.value())
            largeur_coupe = self.kerf.value()
            pieces_a_creer = []
            for row in range(self.table_pieces.rowCount()):
                quantite = int(self.table_pieces.item(row, 0).text())
                data = self.table_pieces.item(row, 2).data(Qt.ItemDataRole.UserRole)
                if not data:
                    continue
                poly = None
                vertices = None
                forme = data.get('forme')
                try:
                    if forme == 'rectangle':
                        vertices = creer_trapeze_isocele(data['largeur'], data['largeur'], data['hauteur'])
                    elif forme == 'trapeze_isocele':
                        vertices = creer_trapeze_isocele(data['grande_base'], data['petite_base'], data['hauteur'])
                    elif forme == 'trapeze_rectangle':
                        vertices = creer_trapeze_rectangle(data['grande_base'], data['petite_base'], data['hauteur'])
                    elif forme == 'triangle_equilateral':
                        cote = data['cote']
                        hauteur = (math.sqrt(3) / 2) * cote
                        vertices = [(0, 0), (cote, 0), (cote / 2, hauteur)]
                    elif forme == 'triangle_isocele_bh':
                        base = data['base']
                        h = data['hauteur']
                        vertices = [(0, 0), (base, 0), (base / 2, h)]
                    elif forme == 'triangle_isocele_sss':
                        s1 = data['cote_egal']
                        base = data['base']
                        if not (2 * s1 > base):
                            raise ValueError("Inégalité triangulaire non respectée")
                            h = math.sqrt(s1 ** 2 - (base / 2) ** 2)
                            vertices = [(0, 0), (base, 0), (base / 2, h)]
                    elif forme == 'triangle_rectangle_2c':
                        adj = data.get('adj')
                        opp = data.get('opp')
                        hyp = data.get('hyp')
                        if adj and opp:
                            pass
                        elif adj and hyp:
                            opp = math.sqrt(hyp ** 2 - adj ** 2)
                        elif opp and hyp:
                            adj = math.sqrt(hyp ** 2 - opp ** 2)
                        vertices = [(0, 0), (adj, 0), (0, opp)]
                    elif forme == 'triangle_rectangle_1a1c':
                        cote = data['cote']
                        angle_rad = math.radians(data['angle'])
                        type_cote = data['type_cote']
                        if type_cote == 'Adjacent':
                            adj = cote
                            opp = adj * math.tan(angle_rad)
                        elif type_cote == 'Opposé':
                            opp = cote
                            adj = opp / math.tan(angle_rad)
                        elif type_cote == 'Hypoténuse':
                            opp = cote * math.sin(angle_rad)
                            adj = cote * math.cos(angle_rad)
                        vertices = [(0, 0), (adj, 0), (0, opp)]
                    elif forme == 'triangle_quelconque_sss':
                        a, b, c = data['a'], data['b'], data['c']
                        if not (a + b > c and a + c > b and b + c > a):
                            raise ValueError("Inégalité triangulaire non respectée")
                        angle_b_rad = math.acos((a ** 2 + c ** 2 - b ** 2) / (2 * a * c))
                        vertices = [(0, 0), (c, 0), (a * math.cos(angle_b_rad), a * math.sin(angle_b_rad))]
                    elif forme == 'triangle_quelconque_sas':
                        b, c, angle_a_deg = data['b'], data['c'], data['angle_a']
                        angle_a_rad = math.radians(angle_a_deg)
                        vertices = [(0, 0), (c, 0), (b * math.cos(angle_a_rad), b * math.sin(angle_a_rad))]
                    elif forme == 'triangle_quelconque_asa':
                        c, angle_a_deg, angle_b_deg = data['c'], data['angle_a'], data['angle_b']
                        if angle_a_deg + angle_b_deg >= 180:
                            raise ValueError("La somme des angles doit être < 180°")
                        angle_a_rad = math.radians(angle_a_deg)
                        angle_b_rad = math.radians(angle_b_deg)
                        angle_c_rad = math.pi - angle_a_rad - angle_b_rad
                        b = c * math.sin(angle_b_rad) / math.sin(angle_c_rad)
                        vertices = [(0, 0), (c, 0), (b * math.cos(angle_a_rad), b * math.sin(angle_a_rad))]
                    elif forme == 'cercle':
                        r = data['rayon']
                        poly = Point(r, r).buffer(r, quad_segs=16)
                    elif forme == 'ellipse':
                        rx = data['rayon_x']
                        ry = data['rayon_y']
                        cercle_unitaire = Point(rx, ry).buffer(1, quad_segs=16)
                        poly = scale(
                            cercle_unitaire, xfact=rx, yfact=ry)
                    if vertices:
                        poly = Polygon(vertices)
                    if poly:
                        pieces_a_creer.extend([poly] * quantite)
                except (ValueError, KeyError, ZeroDivisionError) as e:
                    QMessageBox.critical(self, "Erreur de Données", f"Erreur de création à la ligne {row + 1}: {e}")
                    return
            if not pieces_a_creer:
                QMessageBox.critical(self, "Erreur", "Aucune pièce valide n'a pu être créée.")
                return
            QMessageBox.information(self, "Calcul en cours...", "Le calcul est lancé. L'interface peut se figer.")
            QApplication.processEvents()
            panneaux_finaux = placer_pieces(panneau_dims, pieces_a_creer, largeur_coupe)
            if panneaux_finaux:
                QMessageBox.information(self, "Calcul Terminé",
                                        f"""{len(panneaux_finaux)} panneau(x) nécessaire(s).
    Les fichiers de sortie vont être générés.""")
                dessiner_plan_png(panneaux_finaux, panneau_dims[0], panneau_dims[1])
            else:
                QMessageBox.warning(self, "Calcul Terminé", "Aucune solution trouvée.")

        def retour(self):
            self.hide()
            self.retour_au_choix.emit()


    class ModeSelectionDialog(QDialog):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Choisir le type d'optimisation")
            self.selected_mode = None
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Quel type de calepinage souhaitez-vous effectuer ?"))
            self.btn_1d = QPushButton("Optimisation de Barres (1D)")
            self.btn_2d = QPushButton("Optimisation de Panneaux (2D)")
            layout.addWidget(self.btn_1d)
            layout.addWidget(self.btn_2d)

    manager = ApplicationManager()
    manager.run()
