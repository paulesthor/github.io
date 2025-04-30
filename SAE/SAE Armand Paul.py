# -*- coding: utf-8 -*-

# Importation des bibliothèques nécessaires
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import csv
from datetime import datetime
from mysql.connector import IntegrityError
from mysql.connector import Error
import mysql.connector

class DBManagerPro:
    def __init__(self, root):
        # Initialisation de la classe principale
        self.root = root
        self.db_connection = None  # Variable pour stocker la connexion à la base de données
        self.current_role = None  # Variable pour stocker le rôle de l'utilisateur (Employé/Admin)
        self.setup_ui()  # Appel de la méthode pour créer l'interface
        
    def setup_ui(self):
        # Configuration de base de la fenêtre principale
        self.root.title("DB Manager Pro")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)
        self.root.configure(bg="#0d1b2a")  # Couleur de fond
        self.setup_styles()  # Configuration des styles
        self.create_login_ui()  # Création de l'interface de login

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        colors = {
            "bg": "#0d1b2a",
            "card": "#1b263b",
            "text": "#e0e1dd",
            "accent": "#5e60ce",
            "highlight": "#7b7fda",
            "entry": "#2a3c5a",
            "header": "#1a2a3a",
            "error": "#ff6b6b",
            "warning": "#ff6b6b"
        }
        
        self.style.configure(".", background=colors["bg"], foreground=colors["text"], 
                           font=("Segoe UI", 11), borderwidth=0)
        self.style.configure("Card.TFrame", background=colors["card"], padding=12)
        self.style.configure("Accent.TButton", background=colors["accent"], 
                           foreground="white", font=("Segoe UI", 12, "bold"), padding=12)
        self.style.configure("Warning.TButton", background=colors["warning"],
                           foreground="white", font=("Segoe UI", 12, "bold"), padding=12)
        self.style.map("Accent.TButton", background=[("active", colors["highlight"]), 
                      ("pressed", "#4a4dcc")])
        self.style.map("Warning.TButton", background=[("active", "#ff8c8c"),
                      ("pressed", "#cc4a4a")])
        self.style.configure("TButton", background="#3a4a6a", 
                           font=("Segoe UI", 10, "bold"), padding=8)
        self.style.map("TButton", background=[("active", "#4a5a7a"), ("pressed", "#2a3a5a")])
        self.style.configure("Treeview", background=colors["card"], rowheight=30, 
                           fieldbackground=colors["card"])
        self.style.configure("Treeview.Heading", background=colors["header"], padding=10)
        self.style.map("Treeview", background=[("selected", colors["accent"])],
                     foreground=[("selected", "white")])
        self.style.configure("TEntry", fieldbackground=colors["entry"])
        self.style.configure("TCombobox", fieldbackground=colors["entry"], 
                           background=colors["card"])
    def create_login_ui(self):
        # Création de l'interface de connexion
        self.login_frame = ttk.Frame(self.root, style="Card.TFrame", padding=30)
        self.login_frame.pack(expand=True, fill=tk.BOTH, padx=15, pady=15)
        
        # Titre de l'application
        ttk.Label(self.login_frame, 
                 text="🗃️ DB Manager Pro", 
                 font=("Segoe UI", 24, "bold")).pack(pady=(0, 5))
        
        # Sous-titre
        ttk.Label(self.login_frame, 
                 text="Gestion de bases MySQL",
                 font=("Segoe UI", 10)).pack(pady=(0, 20))
        
        # Frame pour le formulaire de connexion
        form_frame = ttk.Frame(self.login_frame, style="Card.TFrame", padding=20)
        form_frame.pack(fill=tk.X)

        # Champ pour sélectionner le rôle
        ttk.Label(form_frame, text="Rôle :").pack(anchor="w")
        self.role_var = tk.StringVar(value="Employé")
        ttk.Combobox(form_frame, textvariable=self.role_var, 
                    values=["Employé", "Administrateur"], 
                    state="readonly").pack(fill=tk.X, pady=3, ipady=4)
        
        # Champ pour le mot de passe
        ttk.Label(form_frame, text="Mot de passe :").pack(anchor="w", pady=(10, 0))
        self.pass_entry = ttk.Entry(form_frame, show="•")
        self.pass_entry.pack(fill=tk.X, pady=3, ipady=6)
        
        # Bouton de connexion
        self.connect_button = ttk.Button(
            form_frame,
            text="CONNEXION",
            style="Accent.TButton",
            command=self.handle_login
        )
        self.connect_button.pack(pady=15, fill=tk.X, ipady=8)
        
        # Liaison de la touche Entrée au champ de mot de passe
        self.pass_entry.bind("<Return>", lambda e: self.handle_login())

    def handle_login(self, event=None):
        # Gestion de la tentative de connexion
        if self.pass_entry.get() == "1234":  # Mot de passe simple pour le prototype
            self.current_role = self.role_var.get()  # Stockage du rôle
            self.create_main_ui()  # Création de l'interface principale
        else:
            # Message d'erreur si le mot de passe est incorrect
            messagebox.showerror("Erreur d'authentification", "Le mot de passe est incorrect.")
            self.pass_entry.delete(0, tk.END)  # Effacement du champ mot de passe

    def create_main_ui(self):
        # Création de l'interface principale après connexion
        self.login_frame.destroy()  # Suppression de l'écran de login
        
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Création de la sidebar
        sidebar = ttk.Frame(self.main_frame, width=200, style="Card.TFrame")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Boutons de navigation dans la sidebar
        for text, cmd in [("🗃️ Gestion Base", self.show_db_manager),
                         ("📝 Console SQL", self.show_sql_console),
                         ("📤 Importer CSV", self.show_import_csv),
                         ("ℹ️ Aide", self.show_help)]:
            btn = ttk.Button(sidebar, text=text, command=cmd)
            btn.pack(fill=tk.X, pady=5, padx=5)
        
        # Zone de contenu principal
        self.content = ttk.Frame(self.main_frame, padding=15)
        self.content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # En-tête avec titre et bouton de déconnexion
        header = ttk.Frame(self.content)
        header.pack(fill=tk.X, pady=(0, 15))
        self.title_label = ttk.Label(header, text="Gestion Base de Données", 
                                   font=("Segoe UI", 16, "bold"))
        self.title_label.pack(side=tk.LEFT)
        ttk.Button(header, text="Déconnexion", command=self.handle_logout).pack(side=tk.RIGHT)
        
        # Conteneur pour les cartes de contenu
        self.card_container = ttk.Frame(self.content)
        self.card_container.pack(fill=tk.BOTH, expand=True)
        
        # Affichage par défaut de la gestion de base de données
        self.show_db_manager()

    def show_import_csv(self):
        # Affichage de l'interface d'importation CSV
        self.clear_content()
        self.title_label.config(text="Importer des données depuis CSV")
        
        import_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=20)
        import_frame.pack(fill=tk.BOTH, expand=True)
        
        # Texte explicatif
        ttk.Label(import_frame, 
                 text="Importer des données depuis des fichiers CSV vers la base MySQL",
                 font=("Segoe UI", 12)).pack(pady=(0, 20))
        
        # Instructions pour l'utilisateur
        instructions = """
        Instructions :
        1. Assurez-vous d'avoir les fichiers CSV dans le même dossier que l'application
        2. Les fichiers doivent s'appeler : saunier.csv, client.csv, entree.csv, sortie.csv
        3. Cliquez sur le bouton "Importer les données" pour lancer le processus
        """
        ttk.Label(import_frame, text=instructions, justify=tk.LEFT).pack(pady=(0, 20))
        
        # Bouton pour lancer l'importation
        ttk.Button(import_frame, 
                  text="Importer les données", 
                  style="Accent.TButton",
                  command=self.import_csv_data).pack(pady=10)
        
        # Bouton de suppression réservé à l'admin
        if self.current_role == "Administrateur":
            ttk.Button(import_frame,
                      text="⚠️ Supprimer TOUTES les données",
                      style="Warning.TButton",
                      command=self.confirm_delete_all_data).pack(pady=10)
        
        # Zone de texte pour afficher le statut de l'importation
        self.import_status = scrolledtext.ScrolledText(
            import_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 9),
            state=tk.DISABLED
        )
        self.import_status.pack(fill=tk.BOTH, expand=True)

    def confirm_delete_all_data(self):
        """Affiche une boîte de dialogue de confirmation avant la suppression"""
        if messagebox.askyesno(
            "Confirmation", 
            "⚠️ ATTENTION! Cela va supprimer TOUTES les données des tables.\n\n"
            "Cette action est irréversible. Continuer?",
            icon='warning'
        ):
            self.delete_all_data()

    def delete_all_data(self):
        """Supprime toutes les données des tables principales"""
        if self.current_role != "Administrateur":
            messagebox.showwarning("Accès refusé", "Réservé aux administrateurs")
            return
        
        try:
            db = self.connect_to_db()
            if not db:
                return
            
            c = db.cursor()
            
            # Liste des tables à vider (dans l'ordre pour respecter les contraintes de clé étrangère)
            tables = ["concerner", "sortie", "entree", "client", "saunier"]
            
            self.update_import_status("\nDébut de la suppression des données...")
            
            for table in tables:
                try:
                    c.execute(f"DELETE FROM {table}")
                    db.commit()
                    self.update_import_status(f"Table {table} vidée avec succès")
                except Error as e:
                    db.rollback()
                    self.update_import_status(f"ERREUR lors de la vidange de {table}: {str(e)}")
            
            self.update_import_status("\nToutes les données ont été supprimées!")
            messagebox.showinfo("Succès", "Toutes les données ont été supprimées")
            
        except Error as e:
            self.update_import_status(f"ERREUR inattendue: {str(e)}")
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{str(e)}")

    def import_csv_data(self):
                           # Liste des tables à remplir (chaque table correspond à un fichier csv du même nom)
            listeTables = ["saunier", "client", "entree", "sortie"]
            
            # Liste pour stocker les identifiants pour voir s'ils sont déjà insérés dans la table "sortie"
            listeIdSor = []
            
            # On teste l'ajout des données des fichiers csv dans la base de données (donc si elles sont déjà présentes ou non)
            try :    
                # On parcourt chaque table
                for table in listeTables :
                    # On ouvre le fichier CSV correspondant à la table
                    fichier = open(table + ".csv")
                    
                    # On crée un lecteur CSV du fichier, et on précise que le séparateur est le ";", car c'est un fichier csv2
                    lecteurCSV = csv.DictReader(fichier, delimiter=";")
                    
                    # On teste la connexion à la base de données MySQL
                    try :
                        # Connexion à la base de données MySQL, nommée "base_de_donnees_saunier"
                        db = mysql.connector.connect(host="localhost", user="root", password="", database="base_de_donnees_saunier")
                        c = db.cursor()
                    # S'il y a une erreur :
                    except mysql.connector.Error :
                        # On affiche l'erreur à l'utilisateur
                        print("La connexion à la base de données a échoué, vérifiez bien que le nom de votre base soit : 'base_de_donnees_saunier' ")
                        # On arrête le programme
                        break
                    # Liste pour stocker chaque ligne du lecteur CSV, chaque ligne étant sous la forme de dictionnaire
                    listeDicos = []
                    
                    # On parcourt chaque ligne du fichier CSV pour les ajouter dans "listeDicos"
                    for ligne in lecteurCSV:
                        listeDicos.append(ligne)
                
                    # On parcourt ensuite chaque dictionnaire de la liste des dictionnaires
                    for dictionnaire in listeDicos :
                        # On crée une liste qui contiendra les valeurs à insérer dans la table
                        liste = []
                
                        # On parcourt chaque valeur du dictionnaire (donc on parcourt chaque champ)
                        for valeur in dictionnaire.values() :
                            # Si la valeur contient deux "/" (donc si la valeur est une date au format "JJ/MM/AAAA") :
                            if valeur.count("/") == 2 : 
                                # On convertit la chaîne de caractères en objet date
                                date_csv = datetime.strptime(valeur, "%d/%m/%Y")
                
                                # On transforme la date au format "AAAA/MM/JJ"
                                date_inversee = date_csv.strftime("%Y/%m/%d")
                                # On ajoute la date
                                liste.append(date_inversee)
                                
                            else :
                                # Sinon, on ajoute simplement la valeur à la liste
                                liste.append(valeur)
                
                        # Si la table traitée est "sortie" :
                        if table == "sortie" :
                            listeSor = []   # Liste qui va contenir les valeurs pour la table "sortie"
                            listeConc = []  # Liste qui va contenir les valeurs pour la table "concerner"
                
                            # On sépare les 5 champs du fichier "sortie" selon leur destination (table "sortie" ou bien table "concerner")
                            for i in range(5) :
                                if i == 0:
                                    # Le premier champ est commun aux deux tables, donc on l'ajoute dans les listes de "sortie" et "concerner"
                                    listeSor.append(liste[i])
                                    listeConc.append(liste[i])
                                elif i < 3 :
                                    # On ajoute les champs 2 et 3 dans la liste pour "sortie"
                                    listeSor.append(liste[i])
                                else :
                                    # On ajoute les champs 4 et 5 dans la liste pour "concerner"
                                    listeConc.append(liste[i])
                
                            # Si la valeur du champ 1 (donc le numéro de sortie) n'est pas déjà présent dans la liste des numéros de sortie (appelés ici "Identifiants de sortie")
                            if listeSor[0] not in listeIdSor :
                                # On va ajouter ce numéro / identifiant de sortie dans la liste des Id de sortie 
                                listeIdSor.append(listeSor[0])
                                # On transtype la liste qui contient les valeurs pour la table "sortie" en un tuple
                                TupleSor = tuple(listeSor)
                                # On insère ce tuple dans la table "sortie"
                                c.execute("insert into " + table + " values" + str(TupleSor))
                                # On "force" l'insertion
                                db.commit()
                
                            # On transtype la liste qui contient les valeurs pour la table "concerner" en un tuple
                            TupleConc = tuple(listeConc)
                            # On insère ce tuple dans la table "concerner"
                            c.execute("insert into concerner values" + str(TupleConc))
                            # On "force" l'insertion
                            db.commit()
                
                        else :
                            # Sinon, si c'est une autre table que "sortie" qui est traitée ("saunier", "client", "entree") :
                            monTuple = tuple(liste) # On transtype la liste qui contient les valeurs pour la table à remplir en un tuple
                            c.execute("insert into " + table + " values" + str(monTuple)) # On insère ce tuple dans la table traitée
                            db.commit() # On "force" l'insertion
                
                # On affiche à l'utilisateur un message de confirmation d'ajout des données
                    print("L'ensemble des données du fichier " + table +" csv ont bien été ajoutées à la base de données !")
            
            # Si la base de données est déjà remplie :
            except IntegrityError :
                # On en informe l'utilisateur
                print("Les données des fichiers sont déjà présentes dans la base de données !")
                
                self.update_import_status(f"Table {table} importée avec succès")
                fichier.close()
                
            except FileNotFoundError:
                self.update_import_status(f"ERREUR: Fichier {table}.csv introuvable")
            except Error as e:
                self.update_import_status(f"ERREUR MySQL ({table}): {str(e)}")
            except Exception as e:
                self.update_import_status(f"ERREUR inattendue ({table}): {str(e)}")
        
                self.update_import_status("\nImportation terminée!")

    def update_import_status(self, message):
        # Mise à jour de la zone de statut d'importation
        self.import_status.config(state=tk.NORMAL)
        self.import_status.insert(tk.END, message + "\n")
        self.import_status.see(tk.END)
        self.import_status.config(state=tk.DISABLED)
        self.root.update()  # Pour mettre à jour l'interface pendant l'importation

    def show_help(self):
        # Affichage de la page d'aide
        self.clear_content()
        self.title_label.config(text="Aide Utilisateur")
        
        help_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=15)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text = """
        GUIDE COMPLET D'UTILISATION

        1. GESTION DE BASE DE DONNÉES
        • Sélection : Choisissez une table dans le menu déroulant
        • Recherche : Utilisez le champ de recherche pour filtrer
        • Actualisation : Cliquez sur [🔄 Actualiser] puis [Charger]
        • Ajout : [+ Ajouter] ouvre un formulaire de création
        • Modification : Sélectionnez une ligne puis [Modifier] (Admin)
        • Suppression : Sélectionnez une ligne puis [Supprimer] (Admin)

        2. CONSOLE SQL
        • Saisie : Écrivez votre requête dans la zone prévue
        • Exemples : Utilisez les boutons prédéfinis
        • Exécution : Cliquez sur [Exécuter] ou [Ctrl+Entrée]

        3. IMPORTATION CSV
        • Préparation : Placez les fichiers CSV dans le même dossier
        • Format : Les fichiers doivent être nommés correctement
        • Lancement : Cliquez sur [Importer les données]
        • Suppression : Le bouton [Supprimer TOUTES les données] (Admin seulement)
          permet de vider complètement les tables
        """
        
        help_text = "\n".join(line.strip() for line in help_text.split("\n"))
        
        help_area = scrolledtext.ScrolledText(
            help_frame, 
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            height=20,
            padx=10,
            pady=10,
            background="#1b263b",
            foreground="#e0e1dd",
            insertbackground="#e0e1dd"
        )
        help_area.insert(tk.END, help_text)
        help_area.config(state=tk.DISABLED)
        help_area.pack(fill=tk.BOTH, expand=True)

    def show_db_manager(self):
        # Affichage de l'interface de gestion de base de données
        self.clear_content()
        self.title_label.config(text="Gestion Base de Données")
        
        # Frame supérieure (stats + recherche)
        top_frame = ttk.Frame(self.card_container)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Statistiques
        stats_frame = ttk.Frame(top_frame)
        stats_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        for text, value in [("Tables disponibles", "8"), ("Statut", "Connecté")]:
            card = ttk.Frame(stats_frame, style="Card.TFrame", padding=10)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
            ttk.Label(card, text=text).pack(anchor="w")
            ttk.Label(card, text=value, font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(2, 0))
        
        # Recherche
        search_frame = ttk.Frame(top_frame, style="Card.TFrame", padding=5)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, padx=5)
        
        ttk.Label(search_frame, text="Rechercher :").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        search_entry.bind("<KeyRelease>", self.search_data)
        
        # Barre d'outils principale
        toolbar = ttk.Frame(self.card_container)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        self.table_var = tk.StringVar()
        try:
            cursor = self.connect_to_db().cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            if not tables:
                messagebox.showinfo("Information", "Aucune table trouvée")
                return
                
            table_combo = ttk.Combobox(toolbar, textvariable=self.table_var, 
                                     values=tables, state="readonly")
            table_combo.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
            table_combo.current(0)
            
            ttk.Button(toolbar, text="🔄 Actualiser", command=self.refresh_tables).pack(side=tk.LEFT, padx=(0, 10))
            ttk.Button(toolbar, text="Charger", style="Accent.TButton",
                      command=lambda: self.load_table_data(self.table_var.get())).pack(side=tk.LEFT)
            
            ttk.Button(toolbar, text="+ Ajouter", 
                      command=self.add_db_row).pack(side=tk.RIGHT, padx=(10, 0))
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")
            return
        
        # Tableau de données
        table_frame = ttk.Frame(self.card_container, style="Card.TFrame", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        self.db_tree = ttk.Treeview(table_frame, show="headings")
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.db_tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.db_tree.xview)
        self.db_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        
        self.db_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Boutons d'action
        self.btn_frame = ttk.Frame(self.card_container)
        if self.current_role == "Administrateur":
            self.btn_frame.pack(fill=tk.X, pady=(5, 0))
            ttk.Button(self.btn_frame, text="Modifier", command=self.modify_db_row).pack(side=tk.LEFT, padx=5)
            ttk.Button(self.btn_frame, text="Supprimer", command=self.delete_db_row).pack(side=tk.LEFT, padx=5)
        
        self.load_table_data(tables[0] if tables else "")

    def search_data(self, event=None):
        # Méthode pour rechercher dans les données
        search_term = self.search_var.get().lower()
        
        if not hasattr(self, 'db_tree') or not self.db_tree.get_children():
            return
            
        for item in self.db_tree.get_children():
            values = [str(v).lower() for v in self.db_tree.item(item)['values']]
            if any(search_term in val for val in values):
                self.db_tree.selection_set(item)
                self.db_tree.focus(item)
                self.db_tree.see(item)
            else:
                self.db_tree.selection_remove(item)

    def show_sql_console(self):
       """Affiche la console SQL avec les requêtes prédéfinies"""
       self.clear_content()
       self.title_label.config(text="Console SQL")
       
       main_frame = ttk.Frame(self.card_container)
       main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
       
       # Frame pour l'éditeur SQL
       sql_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
       sql_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
       
       ttk.Label(sql_frame, text="Commande SQL :").pack(anchor="w")
       
       self.sql_input = scrolledtext.ScrolledText(
           sql_frame, 
           height=6,
           wrap=tk.WORD,
           font=("Consolas", 10)
       )
       self.sql_input.pack(fill=tk.BOTH, expand=False)
       
       # Bouton d'exécution
       btn_frame = ttk.Frame(sql_frame)
       btn_frame.pack(fill=tk.X, pady=(8, 0))
       
       ttk.Button(
           btn_frame, 
           text="Exécuter (Ctrl+Entrée)", 
           style="Accent.TButton",
           command=self.execute_sql
       ).pack(side=tk.LEFT)
       
       # Frame pour les requêtes prédéfinies
       queries_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=8)
       queries_frame.pack(fill=tk.X, pady=(0, 10))
       
       ttk.Label(queries_frame, text="Requêtes Prédéfinies :").pack(anchor="w")
       
       # Définition des requêtes spécifiques
       queries = [
           ("1. Ventes par mois", """
               CREATE OR REPLACE VIEW VentesParMois AS
               SELECT 
                   MONTH(dateSort) AS Mois,
                   SUM(qteSort) AS QuantiteTotale
               FROM Sortie S
               JOIN Concerner C ON S.numSort = C.numSort
               GROUP BY Mois
               ORDER BY QuantiteTotale DESC;
           """),
           
           ("2. Top clients", """
               SELECT 
                   C.numCli, 
                   C.nomCli, 
                   SUM(Co.qteSort) AS TotalCommande
               FROM Client C
               JOIN Sortie S ON C.numCli = S.numCli
               JOIN Concerner Co ON S.numSort = Co.numSort
               GROUP BY C.numCli, C.nomCli
               ORDER BY TotalCommande DESC;
           """),
           
           ("3. Gains 2024", """
               SELECT 
                   SUM(Co.qteSort * P.Prix_Vente) AS TotalGain
               FROM Sortie S
               JOIN Concerner Co ON S.numSort = Co.numSort
               JOIN Prix P ON Co.numPdt = P.numPdt
               WHERE YEAR(S.dateSort) = P.Annee
                 AND P.Annee = 2024;
           """),
           
           ("4. Top sauniers", """
               SELECT 
                   S.nomSau, 
                   SUM(E.qteEnt) AS TotalProduction
               FROM Saunier S
               JOIN Entree E ON S.numSau = E.numSau
               GROUP BY S.nomSau
               ORDER BY TotalProduction DESC;
           """),
           
           ("5. Sauniers 2024", """
               SELECT 
                   S.nomSau, 
                   SUM(E.qteEnt) AS TotalProduction
               FROM Saunier S
               JOIN Entree E ON S.numSau = E.numSau
               WHERE YEAR(E.dateEnt) = 2024
               GROUP BY S.nomSau
               HAVING TotalProduction > 0
               ORDER BY TotalProduction DESC;
           """),
           
           ("6. Nouveau client", """
               INSERT INTO Client (numCli, nomCli, prenomCli, villeCli)
               VALUES (999, 'DUPONT', 'Jean', 'Paris');
           """),
           
           ("7. Update produit", """
               UPDATE PRODUIT
               SET 
                   libPdt = 'Nouveau nom produit',
                   stockPdt = 150
               WHERE numPro = 1;
           """),
           
           ("8. Clients inactifs", """
               SELECT numCli, nomCli
               FROM Client
               WHERE numCli NOT IN (
                   SELECT DISTINCT numCli 
                   FROM Sortie 
                   WHERE YEAR(dateSort) = 2024
               );
           """),
           
           ("9. Top produits 2024", """
               CREATE OR REPLACE VIEW ProduitsPlusVendus_2024 AS
               SELECT 
                   P.numPdt,
                   P.libPdt,
                   SUM(C.qteSort) AS QuantiteVendue
               FROM Produit P
               JOIN Concerner C ON P.numPdt = C.numPdt
               JOIN Sortie S ON C.numSort = S.numSort
               WHERE YEAR(S.dateSort) = 2024
               GROUP BY P.numPdt, P.libPdt
               ORDER BY QuantiteVendue DESC;
           """),
           
           ("10. Nb clients", """
               SELECT COUNT(DISTINCT numCli) AS NombreClients
               FROM Client;
           """)
       ]
       
       # Création des boutons de requêtes
       buttons_frame = ttk.Frame(queries_frame)
       buttons_frame.pack(fill=tk.X)
       
       # Organisation en 3 colonnes
       for i, (text, query) in enumerate(queries):
           btn = ttk.Button(
               buttons_frame,
               text=text,
               command=lambda q=query: self.insert_sql_command(q),
               width=20
           )
           btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")
       
       # Zone de résultats
       results_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=10)
       results_frame.pack(fill=tk.BOTH, expand=True)
       
       ttk.Label(results_frame, text="Résultats :").pack(anchor="w")
       
       self.sql_results = scrolledtext.ScrolledText(
           results_frame, 
           height=10, 
           wrap=tk.WORD,
           font=("Consolas", 9)
       )
       self.sql_results.pack(fill=tk.BOTH, expand=True)
       self.sql_results.config(state=tk.DISABLED)
       
       # Raccourci clavier
       self.sql_input.bind("<Control-Return>", lambda e: self.execute_sql())

    def insert_sql_command(self, command):
       """Insère la requête dans l'éditeur SQL"""
       self.sql_input.delete(1.0, tk.END)
       self.sql_input.insert(tk.END, command.strip())
       self.sql_input.focus()

    def execute_sql(self):
       """Exécute la requête SQL et affiche les résultats"""
       sql = self.sql_input.get(1.0, tk.END).strip()
       if not sql:
           messagebox.showwarning("Attention", "Veuillez entrer une commande SQL")
           return
           
       try:
           connection = self.connect_to_db()
           if not connection:
               return
               
           cursor = connection.cursor()
           cursor.execute(sql)
           
           self.sql_results.config(state=tk.NORMAL)
           self.sql_results.delete(1.0, tk.END)
           
           if cursor.description:  # Si la requête retourne des résultats
               columns = [desc[0] for desc in cursor.description]
               self.sql_results.insert(tk.END, " | ".join(columns) + "\n")
               self.sql_results.insert(tk.END, "-"*50 + "\n")
               
               for row in cursor.fetchall():
                   self.sql_results.insert(tk.END, " | ".join(str(value) for value in row) + "\n")
           else:  # Requête de modification
               connection.commit()
               self.sql_results.insert(tk.END, f"Succès. Lignes affectées : {cursor.rowcount}")
               
           self.sql_results.config(state=tk.DISABLED)
           
       except Error as e:
           messagebox.showerror("Erreur SQL", f"Erreur :\n{str(e)}")
           self.sql_results.config(state=tk.NORMAL)
           self.sql_results.delete(1.0, tk.END)
           self.sql_results.insert(tk.END, f"ERREUR: {str(e)}")
           self.sql_results.config(state=tk.DISABLED)

    def load_table_data(self, table_name):
        # Chargement des données d'une table dans le Treeview
        if not table_name:
            return
            
        connection = self.connect_to_db()
        if not connection:
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                messagebox.showinfo("Information", f"Table {table_name} vide")
                return
                
            columns = list(rows[0].keys())
            
            self.db_tree.delete(*self.db_tree.get_children())
            self.db_tree["columns"] = columns
            
            for col in columns:
                self.db_tree.heading(col, text=col, anchor="w")
                col_width = min(300, max(100, len(col) * 8 + 20))
                self.db_tree.column(col, width=col_width, anchor="w", stretch=True)
            
            for row in rows:
                self.db_tree.insert("", "end", values=list(row.values()))
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")

    def add_db_row(self):
        # Ajout d'une nouvelle ligne dans la table
        table_name = self.table_var.get()
        if not table_name:
            return
            
        connection = self.connect_to_db()
        if not connection:
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"DESCRIBE {table_name}")
            columns_info = cursor.fetchall()
            
            add_win = tk.Toplevel(self.root)
            add_win.title(f"Ajouter - {table_name}")
            add_win.configure(bg=self.style.lookup(".", "background"))
            
            entries = []
            required_cols = []
            
            for col_info in columns_info:
                if "auto_increment" in col_info["Extra"].lower():
                    continue
                    
                frame = ttk.Frame(add_win, padding=5)
                frame.pack(fill=tk.X)
                
                col_name = col_info["Field"]
                col_type = col_info["Type"]
                is_nullable = col_info["Null"] == "YES"
                default_value = col_info["Default"]
                
                label_text = f"{col_name} ({col_type})"
                if not is_nullable and default_value is None:
                    label_text += " *"
                    required_cols.append(col_name)
                
                ttk.Label(frame, text=label_text, width=30).pack(side=tk.LEFT)
                
                entry = ttk.Entry(frame)
                entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
                
                if default_value is not None:
                    entry.insert(0, str(default_value))
                
                entries.append((col_name, entry, is_nullable))
            
            def save_new_row():
                try:
                    cursor = connection.cursor()
                    
                    columns = []
                    values = []
                    placeholders = []
                    
                    for col_name, entry, is_nullable in entries:
                        value = entry.get()
                        
                        if not value and col_name in required_cols:
                            messagebox.showerror("Erreur", f"{col_name} est obligatoire")
                            return
                        
                        columns.append(col_name)
                        values.append(value if value else None)
                        placeholders.append("%s")
                    
                    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                    
                    cursor.execute(query, values)
                    connection.commit()
                    
                    messagebox.showinfo("Succès", "Donnée ajoutée")
                    add_win.destroy()
                    self.load_table_data(table_name)
                    
                except Error as e:
                    messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")
                    connection.rollback()
            
            btn_frame = ttk.Frame(add_win, padding=10)
            btn_frame.pack(fill=tk.X)
            
            ttk.Button(btn_frame, text="Ajouter", style="Accent.TButton",
                     command=save_new_row).pack(side=tk.RIGHT)
            ttk.Button(btn_frame, text="Annuler", 
                     command=add_win.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")

    def modify_db_row(self):
        # Modification d'une ligne existante
        if self.current_role != "Administrateur":
            messagebox.showwarning("Accès refusé", "Réservé aux administrateurs")
            return
            
        selected = self.db_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Sélectionnez une ligne")
            return
        
        table_name = self.table_var.get()
        if not table_name:
            return
            
        connection = self.connect_to_db()
        if not connection:
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"DESCRIBE {table_name}")
            columns_info = cursor.fetchall()
            
            item = self.db_tree.item(selected[0])
            values = item["values"]
            columns = self.db_tree["columns"]
            
            edit_win = tk.Toplevel(self.root)
            edit_win.title(f"Modifier - {table_name}")
            edit_win.configure(bg=self.style.lookup(".", "background"))
            
            entries = []
            primary_keys = []
            
            for i, (col_info, col_name, val) in enumerate(zip(columns_info, columns, values)):
                frame = ttk.Frame(edit_win, padding=5)
                frame.pack(fill=tk.X)
                
                is_primary = col_info["Key"] == "PRI"
                if is_primary:
                    primary_keys.append((col_name, val))
                
                ttk.Label(frame, text=f"{col_name} ({col_info['Type']})", width=30).pack(side=tk.LEFT)
                
                if is_primary:
                    ttk.Label(frame, text=str(val)).pack(side=tk.LEFT, expand=True, fill=tk.X)
                    entries.append(None)
                else:
                    entry = ttk.Entry(frame)
                    entry.insert(0, str(val))
                    entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
                    entries.append(entry)
            
            def save_changes():
                try:
                    cursor = connection.cursor()
                    
                    set_parts = []
                    new_values = []
                    for col_info, col_name, entry in zip(columns_info, columns, entries):
                        if entry is not None:
                            set_parts.append(f"{col_name} = %s")
                            new_values.append(entry.get())
                    
                    where_parts = []
                    for pk_col, pk_val in primary_keys:
                        where_parts.append(f"{pk_col} = %s")
                        new_values.append(pk_val)
                    
                    query = f"UPDATE {table_name} SET {', '.join(set_parts)} WHERE {' AND '.join(where_parts)}"
                    
                    cursor.execute(query, new_values)
                    connection.commit()
                    
                    messagebox.showinfo("Succès", "Modification réussie")
                    edit_win.destroy()
                    self.load_table_data(table_name)
                    
                except Error as e:
                    messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")
                    connection.rollback()
            
            btn_frame = ttk.Frame(edit_win, padding=10)
            btn_frame.pack(fill=tk.X)
            
            ttk.Button(btn_frame, text="Enregistrer", style="Accent.TButton",
                     command=save_changes).pack(side=tk.RIGHT)
            ttk.Button(btn_frame, text="Annuler", 
                     command=edit_win.destroy).pack(side=tk.RIGHT, padx=5)
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")

    def delete_db_row(self):
        # Suppression d'une ligne
        if self.current_role != "Administrateur":
            messagebox.showwarning("Accès refusé", "Réservé aux administrateurs")
            return
            
        selected = self.db_tree.selection()
        if not selected:
            messagebox.showwarning("Avertissement", "Sélectionnez une ligne")
            return
        
        table_name = self.table_var.get()
        if not table_name:
            return
            
        if not messagebox.askyesno("Confirmation", "Supprimer cette ligne ?"):
            return
            
        connection = self.connect_to_db()
        if not connection:
            return
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(f"DESCRIBE {table_name}")
            columns_info = cursor.fetchall()
            
            item = self.db_tree.item(selected[0])
            values = item["values"]
            columns = self.db_tree["columns"]
            
            primary_keys = []
            for col_info, col_name, val in zip(columns_info, columns, values):
                if col_info["Key"] == "PRI":
                    primary_keys.append((col_name, val))
            
            if not primary_keys:
                messagebox.showerror("Erreur", "Clé primaire introuvable")
                return
            
            where_parts = []
            params = []
            for pk_col, pk_val in primary_keys:
                where_parts.append(f"{pk_col} = %s")
                params.append(pk_val)
            
            query = f"DELETE FROM {table_name} WHERE {' AND '.join(where_parts)}"
            
            cursor.execute(query, params)
            connection.commit()
            
            messagebox.showinfo("Succès", "Suppression réussie")
            self.load_table_data(table_name)
            
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")
            connection.rollback()

    def refresh_tables(self):
        # Actualisation de la liste des tables
        connection = self.connect_to_db()
        if not connection:
            return
        
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
            if tables:
                self.table_var.set(tables[0])
                self.load_table_data(tables[0])
            else:
                messagebox.showinfo("Information", "Aucune table trouvée")
                
        except Error as e:
            messagebox.showerror("Erreur", f"Erreur :\n{str(e)}")

    def connect_to_db(self):
        # Connexion à la base de données MySQL
        try:
            if self.db_connection and self.db_connection.is_connected():
                return self.db_connection
            
            self.db_connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="base_de_donnees_saunier"
            )
            return self.db_connection
        except Error as e:
            messagebox.showerror("Erreur", f"Connexion impossible :\n{str(e)}")
            return None

    def clear_content(self):
        # Nettoyage de la zone de contenu principale
        for widget in self.card_container.winfo_children():
            widget.destroy()

    def handle_logout(self):
        # Gestion de la déconnexion
        if self.db_connection and self.db_connection.is_connected():
            self.db_connection.close()
        self.main_frame.destroy()
        self.create_login_ui()

if __name__ == "__main__":
    # Point d'entrée de l'application
    root = tk.Tk()
    app = DBManagerPro(root)
    root.mainloop()