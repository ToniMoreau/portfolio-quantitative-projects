import sqlite3
import numpy as np
#--MEMO RAPIDE--#
#[0] : id_ia
#[1] : génération
#[2] : profondeur
#[3] : beam_N #cut actions
#[4] : temps_moyen_tour
#[5] : nb_victoire
#[6] : nb_match
#[7] : ratio_elagage
#[8] : elo
#[9] : score
#[10] : active

#---INIT BASE---#
def initialise_database():
    connection = sqlite3.connect("ia_performances.db")
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("CREATE TABLE IF NOT EXISTS IA ( " \
    "id_ia INTEGER PRIMARY KEY, " \
    "génération INT, " \
    "profondeur INT, " \
    "beam_N INT, " \
    "temps_moyen_tour REAL, " \
    "nb_victoire INT, " \
    "nb_match INT, " \
    "ratio_elagage REAL, " \
    "elo REAL, "\
    "score REAL, " \
    "active INT DEFAULT 1)" )
    cursor.execute("CREATE TABLE IF NOT EXISTS Session (" \
    "id_session INTEGER PRIMARY KEY, " \
    "id_ia1 INT REFERENCES IA(id_ia),  " \
    "id_ia2 INT REFERENCES IA(id_ia), " \
    "nb_fils_ia1 INT, " \
    "nb_fils_ia2 INT, " \
    "gagnant INT)" )
    
    cursor.execute("CREATE TABLE IF NOT EXISTS Coefs_Tri (" \
        "id_ia INTEGER PRIMARY KEY REFERENCES IA(id_ia), " \
        "Difference_Hauteur REAL, " \
        "Distance_Centre REAL, " \
        "Mobilite_Verticale_Montee REAL, " \
        "Mobilite_Verticale_Descente REAL, " \
        "Controle_Hauteur_3 REAL)"
    )
    cursor.execute("CREATE TABLE IF NOT EXISTS Coefs_Eval (" \
        "id_ia INTEGER PRIMARY KEY REFERENCES IA(id_ia), " \
        "Difference_Hauteur REAL, " \
        "Distance_Centre REAL, " \
        "Mobilite_Verticale_Montee REAL, " \
        "Mobilite_Verticale_Descente REAL, " \
        "Controle_Hauteur_3 REAL)"
    )

    connection.commit()

    return connection

#---CREER LIGNE---#
def inserer_ia(connection : sqlite3.Connection, génération : int,  profondeur : int, beam_N : int, elo : float = 1000.):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO IA (génération,profondeur, beam_N, temps_moyen_tour,nb_victoire,nb_match,ratio_elagage, elo, score) VALUES(?,?,?,?,?,?,?,?,?)",(génération,profondeur, beam_N, 0,0,0,0, elo,0))
    id_ia = cursor.lastrowid
    connection.commit()
    return  get_ia_from_id(connection,id_ia)
    
def inserer_session(connection : sqlite3.Connection, id_ia1 : int, id_ia2 : int, nb_fils_ia1 : int,nb_fils_ia2: int, gagnant : int):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Session (id_ia1, id_ia2, nb_fils_ia1, nb_fils_ia2, gagnant) VALUES(?,?,?,?,?)",(id_ia1, id_ia2, nb_fils_ia1, nb_fils_ia2, gagnant))
    connection.commit()

def inserer_coefs_tri(connection : sqlite3.Connection, id_ia : int, dict_coefs_tri : dict[str, float]):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Coefs_Tri (id_ia, Difference_Hauteur, Distance_Centre, Mobilite_Verticale_Montee, Mobilite_Verticale_Descente, Controle_Hauteur_3) VALUES(?,?,?,?,?,?)",(id_ia,dict_coefs_tri["Difference_Hauteur"], dict_coefs_tri["Distance_Centre"], dict_coefs_tri["Mobilite_Verticale_Montee"], dict_coefs_tri["Mobilite_Verticale_Descente"] ,dict_coefs_tri["Controle_Hauteur_3"]))
    connection.commit()
    return get_coefs_tri_from_id(connection, id_ia)
def inserer_coefs_eval(connection : sqlite3.Connection, id_ia : int, dict_coefs_eval : dict[str, float]):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Coefs_Eval (id_ia, Difference_Hauteur, Distance_Centre, Mobilite_Verticale_Montee, Mobilite_Verticale_Descente, Controle_Hauteur_3) VALUES(?,?,?,?,?,?)",(id_ia,dict_coefs_eval["Difference_Hauteur"], dict_coefs_eval["Distance_Centre"], dict_coefs_eval["Mobilite_Verticale_Montee"], dict_coefs_eval["Mobilite_Verticale_Descente"] ,dict_coefs_eval["Controle_Hauteur_3"]))
    connection.commit()
    return get_coefs_eval_from_id(connection, id_ia)

#---UPDATE LIGNE---#
def mettre_a_jour_active(connection:sqlite3.Connection, id_ia, active):
    cursor = connection.cursor()
    cursor.execute("UPDATE IA SET active = ? WHERE id_ia = ?", (active, id_ia))
    connection.commit()
    
def mettre_a_jour_ia(connection : sqlite3.Connection,id_ia : int, temps_moyen_tour : float, nb_victoire : int, nb_match:int,ratio_elagage : float, elo : float, score : float):
    cursor = connection.cursor()
    cursor.execute("UPDATE IA SET ratio_elagage = ?, score = ?, elo = ?, nb_match= ?, nb_victoire = ?, temps_moyen_tour = ? WHERE id_ia = ? ", (ratio_elagage,score,elo,nb_match, nb_victoire,temps_moyen_tour, id_ia))
    connection.commit()
    return get_ia_from_id(connection,id_ia)

def mettre_a_jour_elo(connection : sqlite3.Connection, id_ia: int, elo : float):
    cursor = connection.cursor()
    cursor.execute("UPDATE IA SET elo = ? WHERE id_ia = ?", (elo, id_ia))
    connection.commit()
    return get_ia_from_id(connection,id_ia)

def mettre_a_jour_coefs_tri(connection : sqlite3.Connection, id_ia: int, dict_coefs_tri : dict[str, float]):
    cursor = connection.cursor()
    cursor.execute("UPDATE Coefs_Tri SET Difference_Hauteur=?, Distance_Centre=?, Mobilite_Verticale_Montee=?, Mobilite_Verticale_Descente=?, Controle_Hauteur_3=? WHERE id_ia = ?", 
        (dict_coefs_tri["Difference_Hauteur"], dict_coefs_tri["Distance_Centre"], dict_coefs_tri["Mobilite_Verticale_Montee"], dict_coefs_tri["Mobilite_Verticale_Descente"], dict_coefs_tri["Controle_Hauteur_3"], id_ia))
    connection.commit()
    return get_coefs_tri_from_id(connection, id_ia)

def mettre_a_jour_coefs_eval(connection : sqlite3.Connection, id_ia: int, dict_coefs_eval : dict[str, float]):
    cursor = connection.cursor()
    cursor.execute("UPDATE Coefs_Eval SET Difference_Hauteur=?, Distance_Centre=?, Mobilite_Verticale_Montee=?, Mobilite_Verticale_Descente=?, Controle_Hauteur_3=? WHERE id_ia = ?", 
    (dict_coefs_eval["Difference_Hauteur"], dict_coefs_eval["Distance_Centre"], dict_coefs_eval["Mobilite_Verticale_Montee"], dict_coefs_eval["Mobilite_Verticale_Descente"], dict_coefs_eval["Controle_Hauteur_3"], id_ia))
    connection.commit()
    return get_coefs_eval_from_id(connection, id_ia)
#---GETTERS---#
def get_coefs_tri_from_id(connection : sqlite3.Connection, id_ia : int):
    cursor = connection.cursor()
    coefs_tri = cursor.execute("SELECT * FROM Coefs_Tri WHERE id_ia = ?", (id_ia,)).fetchone()
    colonnes = [desc[0] for desc in cursor.description]
    dict_coefs_tri = dict(zip(colonnes[1:], coefs_tri[1:]))  # on saute id_ia
    return dict_coefs_tri

def get_coefs_eval_from_id(connection : sqlite3.Connection, id_ia : int):
    cursor = connection.cursor()
    coefs_eval = cursor.execute("SELECT * FROM Coefs_Eval WHERE id_ia = ?", (id_ia,)).fetchone()
    colonnes = [desc[0] for desc in cursor.description]
    dict_coefs_eval = dict(zip(colonnes[1:], coefs_eval[1:]))  # on saute id_ia
    return dict_coefs_eval

def get_ias_by_position(connection : sqlite3.Connection,liste_ordre : list[int]):
    cursor = connection.cursor()
    ias = []
    for i in liste_ordre:
        ia = cursor.execute("SELECT * FROM IA ORDER BY elo DESC LIMIT 1 OFFSET ?", (i-1,)).fetchone()
        ias.append(ia)        
    return ias

def get_ia_from_id(connection : sqlite3.Connection,id_ia : int):
    cursor = connection.cursor()
    ia = cursor.execute("SELECT * FROM IA WHERE id_ia = ?", (id_ia,)).fetchone()
    return ia

def get_all_ias(connection : sqlite3.Connection):
    cursor = connection.cursor()
    ias = cursor.execute("SELECT * FROM IA WHERE active = 1").fetchall()
    return ias

def get_tournoi_cpt(connection : sqlite3.Connection, modulo : int):
    cursor = connection.cursor()
    count = cursor.execute("SELECT COUNT(*) FROM Session").fetchone()[0] % modulo
    return count

def get_generation_actuelle(connection :sqlite3.Connection):
    cursor = connection.cursor()
    generation = cursor.execute("SELECT MAX(génération) FROM IA").fetchone()
    
    return generation[0]

def recalculer_scores(connection : sqlite3.Connection, calculer_score_fn):
    cursor = connection.cursor()
    ias = cursor.execute("SELECT id_ia, elo, temps_moyen_tour FROM IA").fetchall()
    for ia in ias:
        id_ia, elo, temps = ia
        nouveau_score = calculer_score_fn(elo, temps)
        cursor.execute("UPDATE IA SET score = ? WHERE id_ia = ?", (nouveau_score, id_ia))
    connection.commit()