# Ce fichier fait partie de Mon ECF.
# Ce projet est sous licence GPL3 (https://www.gnu.org/licenses/gpl-3.0.txt)

import tkinter as tk
from tkinter import messagebox
import random
import sqlite3
import json
import os
import xml.etree.ElementTree as ET

# Supprimer la base de données existante s'il y en a une
if os.path.exists("pendu.db"):
    os.remove("pendu.db")

# Charger la configuration à partir du fichier JSON
with open("conf.json", "r") as config_file:
    config = json.load(config_file)

# Initialisation de la base de données SQLite
conn = sqlite3.connect('pendu.db')
cursor = conn.cursor()

# Création des tables
cursor.execute('''CREATE TABLE IF NOT EXISTS themes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY,
                    word TEXT NOT NULL UNIQUE)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS theme_words (
                    theme_id INTEGER,
                    word_id INTEGER,
                    word TEXT NOT NULL,
                    PRIMARY KEY (theme_id, word_id),
                    FOREIGN KEY (theme_id) REFERENCES themes(id),
                    FOREIGN KEY (word_id) REFERENCES words(id))''')

# Insérer les données de thèmes et mots de l'exemple
themes_data = ["Developpeur", "Designer"]
words_data = ["PYTHON", "HTML", "CSS", "JAVASCRIPT", "DATABASE", "INTERFACE", "MOBILE", "NETWORK", "CODE"]
designer_words = ["SKETCH", "FIGMA", "ADOBE", "PROTOTYPE", "UX", "UI", "VECTOR", "MOCKUP", "WIREFRAME"]

# Insérer les thèmes
for theme in themes_data:
    cursor.execute("INSERT OR IGNORE INTO themes (name) VALUES (?)", (theme,))

# Insérer les mots communs à tous les thèmes
for word in words_data:
    cursor.execute("INSERT OR IGNORE INTO words (word) VALUES (?)", (word,))

# Insérer les mots pour le thème "Developpeur"
cursor.execute("SELECT id FROM themes WHERE name='Developpeur'")
theme_row = cursor.fetchone()

if theme_row is not None:
    theme_id = theme_row[0]
    for word_id, word in enumerate(words_data, 1):
        cursor.execute("INSERT OR IGNORE INTO theme_words (theme_id, word_id, word) VALUES (?, ?, ?)", (theme_id, word_id, word))

# Insérer les mots pour le thème "Designer"
cursor.execute("SELECT id FROM themes WHERE name='Designer'")
theme_row = cursor.fetchone()

if theme_row is not None:
    theme_id = theme_row[0]
    for word_id, word in enumerate(designer_words, 1):  # Commencer les word_id à partir de 1
        cursor.execute("INSERT INTO theme_words (theme_id, word_id, word) VALUES (?, ?, ?)", (theme_id, word_id, word))

conn.commit()

# Pouces
THUMBS_UP = "\U0001F44D"  # Pouce levé
THUMBS_DOWN = "\U0001F44E"  # Pouce baissé

# Classe principale de l'application
class PenduApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Jeu du Pendu")
        self.geometry("800x400")  

        # Créer un tk.StringVar pour stocker le thème sélectionné
        self.selected_theme = tk.StringVar(value="Developpeur")

        self.pendu_frame = tk.Frame(self)
        self.pendu_frame.pack(side=tk.LEFT, padx=20)

        self.canvas = tk.Canvas(self.pendu_frame, bg=config["canevas"], width=400, height=250)
        self.canvas.pack()

        self.word_label = tk.Label(self, text="", font=("Helvetica", 20))
        self.word_label.pack(side=tk.BOTTOM, pady=50)

        self.alphabet_frame = tk.Frame(self)
        self.alphabet_frame.pack(side=tk.BOTTOM)

        self.new_game_button = tk.Button(self, text="Nouvelle partie", command=self.new_game)
        self.new_game_button.pack(side=tk.TOP)

        # Initialiser used_letters comme attribut de la classe
        self.used_letters = set()

        # Initialiser game_ended comme attribut de la classe
        self.game_ended = True

        # Charger les mots à partir de la base de données
        self.load_themes()

        self.current_theme_id = config["theme"]

        self.load_words()

        # Choisissez un mot aléatoire parmi les mots chargés
        self.choose_new_word()

        # Initialiser le nombre de tentatives à 0
        self.attempts = 0
        self.max_attempts = 10
        self.current_word = ['_'] * len(self.selected_word)
        self.used_letters = set()

        # Créer les boutons de l'alphabet
        self.create_alphabet_buttons()

        self.new_game()

        # Créer la barre de menu
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # Charger le fichier XML du menu
        self.load_menu_xml("menus.xml")

    def load_themes(self):
        cursor.execute("SELECT * FROM themes")
        self.themes = {theme_id: theme_name for (theme_id, theme_name) in cursor.fetchall()}
        self.themes[3] = "Designer"  

    def load_designer_words(self):
        cursor.execute("SELECT word FROM theme_words WHERE theme_id=?", (3,))
        self.designer_words = [word[0] for word in cursor.fetchall()]

    def load_words(self):
        if self.current_theme_id == 3:  # Vérifier si le thème sélectionné est "Designer UI"
            cursor.execute("SELECT word FROM theme_words WHERE theme_id=?", (self.current_theme_id,))
            self.words = [word[0] for word in cursor.fetchall()]
        else:
            cursor.execute("SELECT word FROM words")
            self.words = [word[0] for word in cursor.fetchall()]
            

    def choose_new_word(self):
        # Vérifier que self.words contient les mots du thème sélectionné
        cursor.execute("SELECT word FROM theme_words WHERE theme_id=?", (self.current_theme_id,))
        self.words = [word[0] for word in cursor.fetchall()]

        if len(self.words) > 0:
            self.selected_word = random.choice(self.words).upper()
        else:
            print("Aucun mot trouvé pour le thème sélectionné.")

    def new_game(self):
        # Enregistrer à nouveau le frame des boutons de l'alphabet
        self.alphabet_frame.pack(pady=10)

        self.word_label.config(text="")
        self.canvas.delete("all")

        print("Thème sélectionné :", self.selected_theme.get())
        # Charger les mots à partir de la base de données pour le thème actuel
        self.load_words()

        # Choisissez un mot aléatoire parmi les mots chargés
        self.choose_new_word()


        self.attempts = 0
        self.max_attempts = 10
        self.current_word = ['_'] * len(self.selected_word)
        self.used_letters.clear()  # Réinitialiser les lettres utilisées pour la nouvelle partie

        self.draw_hangman()

        # Marquer le début de la nouvelle partie
        self.game_ended = False

        # Mettre à jour le mot actuel dans le label
        self.word_label.config(text=" ".join(self.current_word))

        # Réinitialiser les boutons de l'alphabet après que self.selected_word soit défini
        self.update_alphabet_buttons()

    def draw_hangman(self):
        # Nettoyer le canevas avant de redessiner
        self.canvas.delete("all")

        # Dessiner le pendu en fonction des tentatives restantes
        if self.attempts >= 1:
            self.canvas.create_line(50, 190, 150, 190, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 2:
            self.canvas.create_line(100, 190, 100, 40, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 3:
            self.canvas.create_line(100, 40, 175, 40, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 4:
            self.canvas.create_line(175, 40, 175, 70, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 5:
            self.canvas.create_oval(160, 70, 190, 100, width=config["line"]["width"], outline=config["line"]["color"])
        if self.attempts >= 6:
            self.canvas.create_line(175, 100, 175, 130, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 7:
            self.canvas.create_line(175, 100, 195, 120, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 8:
            self.canvas.create_line(175, 100, 155, 120, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 9:
            self.canvas.create_line(175, 130, 195, 160, width=config["line"]["width"], fill=config["line"]["color"])
        if self.attempts >= 10:
            self.canvas.create_line(175, 130, 155, 160, width=config["line"]["width"], fill=config["line"]["color"])

        # Mettre à jour l'interface après le dessin
        self.update()

    def create_alphabet_buttons(self):
        # Créer les boutons de l'alphabet en trois colonnes
        column_count = 0
        row_count = 0
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            if letter in self.used_letters:
                state = tk.DISABLED
                bg = config["letters"]["used"]
            else:
                state = tk.NORMAL
                bg = config["letters"]["active"]

            button = tk.Button(self.alphabet_frame, text=letter, font=("Helvetica", 12), state=state, command=lambda l=letter: self.check_letter(l), bg=bg, relief=tk.RAISED, bd=2)
            button.grid(row=row_count, column=column_count, padx=5, pady=5)

            column_count += 1
            if letter in "GNU":
                column_count = 0
                row_count += 1

    def check_letter(self, letter):
        if letter in self.used_letters:
            return

        self.used_letters.add(letter)

        if letter in self.selected_word:
            for idx, char in enumerate(self.selected_word):
                if char == letter:
                    self.current_word[idx] = letter

            self.word_label.config(text=" ".join(self.current_word))

            if "_" not in self.current_word:
                self.game_over(True)
        else:
            self.attempts += 1
            self.draw_hangman()

            if self.attempts == self.max_attempts:
                self.game_over(False)

        # Mettre à jour les boutons de l'alphabet
        self.update_alphabet_buttons()

    def update_alphabet_buttons(self):
        # Mettre à jour les boutons de l'alphabet en fonction des lettres utilisées
        for button in self.alphabet_frame.winfo_children():
            letter = button["text"]
            if letter in self.used_letters:
                button.config(state=tk.DISABLED)
            else:
                button.config(state=tk.NORMAL)

    def game_over(self, won):
        self.alphabet_frame.pack_forget()

        if won:
            messagebox.showinfo("Partie terminée", "Bravo ! Vous avez gagné.")
            icon = THUMBS_UP  # Afficher un pouce levé si gagné
        else:
            messagebox.showinfo("Partie terminée", f"Dommage ! Le mot était '{self.selected_word}'.")
            icon = THUMBS_DOWN  # Afficher un pouce baissé si perdu

        # Dessiner l'icône (pouce levé ou baissé) en bas à droite du widget de canevas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        icon_size = 50  # Taille de l'icône
        x_pos = canvas_width - icon_size - 10  # Position en x (10 pixels du bord droit)
        y_pos = canvas_height - icon_size - 10  # Position en y (10 pixels du bord bas)
        self.canvas.create_text(x_pos, y_pos, text=icon, font=("Helvetica", 50), fill=config["line"]["color"])

        self.game_ended = True
        self.new_game_button.config(command=self.new_game)

    def load_menu_xml(self, xml_file):
        print("Chargement du fichier XML :", xml_file)

        if not os.path.exists(xml_file):
            messagebox.showerror("Fichier introuvable", f"Le fichier '{xml_file}' est introuvable.")
            return

        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            for menu_element in root:
                menu_label_element = menu_element.attrib.get("categorie")
                if menu_label_element is not None:
                    menu_label = menu_label_element.strip()
                    menu = tk.Menu(self.menu_bar, tearoff=0)

                    for lien_element in menu_element.findall("lien"):
                        lien_label = lien_element.find("label").text
                        lien_command = lien_element.find("command").text

                        print("Chargement du lien :", lien_label)

                        if lien_label == "Nouvelle partie":
                            menu.add_command(label=lien_label, command=self.new_game)
                        elif lien_label == "Niveaux / thèmes":
                            menu.add_command(label=lien_label, command=self.edit_themes)
                        elif lien_label == "Apparence":
                            menu.add_command(label=lien_label, command=self.change_appearance)
                        elif lien_label == "Quitter":
                            menu.add_command(label=lien_label, command=self.quit)
                        elif lien_label == "Editer les mots":
                            menu.add_command(label=lien_label, command=self.edit_words)
                        elif lien_label == "Editer les niveaux":
                            menu.add_command(label=lien_label, command=self.edit_levels)
                        elif lien_label == "A propos":
                            menu.add_command(label=lien_label, command=self.show_about)

                    self.menu_bar.add_cascade(label=menu_label, menu=menu)

        except ET.ParseError:
            messagebox.showerror("Erreur", "Le fichier XML est mal formaté.")
            return

    def edit_themes(self):
        def on_theme_selected():
            selected_theme = theme_var.get()
            self.selected_theme.set(selected_theme)
            if selected_theme == "Developpeur":
                self.current_theme_id = 1
            elif selected_theme == "Designer":
                self.current_theme_id = 3
            self.load_words()
            self.choose_new_word()
            theme_selection_window.destroy()

        print("Thème sélectionné :", self.current_theme_id)

        theme_selection_window = tk.Toplevel(self)
        theme_selection_window.title("Sélectionner le thème")
        theme_selection_window.geometry("300x150")

        theme_var = tk.StringVar(value=self.selected_theme.get())

        for theme in ["Developpeur", "Designer"]:
            theme_radio = tk.Radiobutton(theme_selection_window, text=theme, variable=theme_var, value=theme)
            theme_radio.pack(anchor=tk.W)

        confirm_button = tk.Button(theme_selection_window, text="Confirmer", command=on_theme_selected)
        confirm_button.pack(pady=10)

    def change_appearance(self):
        # Charger les options d'apparence à partir du fichier JSON
        with open("conf.json", "r") as config_file:
            appearance_options = json.load(config_file)

        # Fonction pour appliquer les nouvelles couleurs
        
        def apply_appearance():
        # Afficher le contenu du dictionnaire appearance_options
            print(appearance_options)
            # Obtenir l'apparence sélectionnée
            selected_appearance = appearance_var.get()
            # Mettre à jour les couleurs actuelles avec l'apparence sélectionnée
            self.canvas.config(bg=appearance_options[selected_appearance]["canevas"])
            self.new_game_button.config(bg=appearance_options[selected_appearance]["letters"]["used"])
            # ... (mettez à jour d'autres éléments d'apparence selon vos besoins)

        # Créer une fenêtre pour le menu de sélection des couleurs
        appearance_window = tk.Toplevel(self)
        appearance_window.title("Changer l'apparence")

        # Créer un tk.StringVar pour stocker l'apparence sélectionnée
        appearance_var = tk.StringVar(value="canevas")

        # Créer les boutons radio pour sélectionner l'apparence
        for appearance_key, appearance_name in appearance_options["themes"].items():
            appearance_radio = tk.Radiobutton(appearance_window, text=appearance_name, variable=appearance_var, value=appearance_key)
            appearance_radio.pack(anchor=tk.W)

        # Créer un bouton pour appliquer l'apparence sélectionnée
        apply_button = tk.Button(appearance_window, text="Appliquer", command=apply_appearance)
        apply_button.pack(pady=10)

    def edit_words(self):
        def add_word():
            new_word = new_word_entry.get().strip().upper()
            if new_word:
                cursor.execute("INSERT OR IGNORE INTO words (word) VALUES (?)", (new_word,))
            conn.commit()
            self.load_words() 
            new_word_entry.delete(0, tk.END)
            self.choose_new_word()
            update_word_list()

        def edit_word():
            if selected_word:
                new_word = new_word_entry.get().strip().upper()
            if new_word:
                cursor.execute("UPDATE words SET word=? WHERE word=?", (new_word, selected_word))
                conn.commit()
                self.load_words()
                new_word_entry.delete(0, tk.END)
                self.choose_new_word()
                update_word_list()

        def delete_word():
            if selected_word:
                cursor.execute("DELETE FROM words WHERE word=?", (selected_word,))
            conn.commit()
            self.load_words() 
            new_word_entry.delete(0, tk.END)
            self.choose_new_word()
            update_word_list()

        def on_word_selected(event):
            nonlocal selected_word
            selected_word = word_listbox.get(word_listbox.curselection())
            new_word_entry.delete(0, tk.END)
            new_word_entry.insert(tk.END, selected_word)

        def update_word_list():
            cursor.execute("SELECT word FROM words")
            words = [word[0] for word in cursor.fetchall()]
            word_listbox.delete(0, tk.END)
            for word in words:
                word_listbox.insert(tk.END, word)

        def validate_word(action):
            if action == "add":
                add_word()
            elif action == "edit":
                edit_word()
            self.load_words()
            word_edit_window.destroy()
            

        word_edit_window = tk.Toplevel(self)
        word_edit_window.title("Éditer les mots")
        word_edit_window.geometry("400x300")

        selected_word = None

        word_listbox = tk.Listbox(word_edit_window)
        word_listbox.pack(padx=10, pady=10)
        word_listbox.bind("<<ListboxSelect>>", on_word_selected)
        update_word_list()

        new_word_entry = tk.Entry(word_edit_window)
        new_word_entry.pack(pady=5)

        button_frame = tk.Frame(word_edit_window)
        button_frame.pack(pady=5)

        add_button = tk.Button(button_frame, text="Ajouter", command=lambda: validate_word("add"))
        add_button.pack(side=tk.LEFT, padx=5)

        edit_button = tk.Button(button_frame, text="Modifier", command=lambda: validate_word("edit"))
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="Supprimer", command=delete_word)
        delete_button.pack(side=tk.LEFT, padx=5)

        validate_button = tk.Button(word_edit_window, text="Valider", command=lambda: validate_word("add"))
        validate_button.pack(side=tk.BOTTOM, pady=5)


    def edit_levels(self):
        messagebox.showinfo("Edition des niveaux", "Prochainement \nPrévus pour la mise à jour 2.0.1.")

    def show_about(self):
        messagebox.showinfo("A propos", "Mon projet pendu \nProjet pour l'ECF \nCe programme est sous licence GPL3\nJulien\nVersion Beta 1.0.1")


if __name__ == "__main__":
    app = PenduApp()
    app.mainloop()