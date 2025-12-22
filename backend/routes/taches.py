"""
Blueprint pour les routes de gestion des tâches
Gère le CRUD des tâches, les sous-tâches et l'assignation des membres
"""
from flask import Blueprint, jsonify, request
import os
import sys
# Ajout du répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection

# Création du Blueprint pour les tâches
taches_bp = Blueprint('taches', __name__, url_prefix='/api')


def get_toutes_sous_taches_recursive(conn, idTacheParent):
    """
    Récupère TOUTES les sous-tâches d'une tâche (récursif : inclut sous-sous-tâches, etc.)
    
    Args:
        conn: Connexion à la base de données
        idTacheParent: ID de la tâche parente
        
    Returns:
        Liste de toutes les sous-tâches à tous les niveaux
    """
    cursor = conn.cursor(dictionary=True)
    
    # Récupérer les sous-tâches directes
    cursor.execute("""
        SELECT idTache, statutTache, dateFinTache 
        FROM tache 
        WHERE idTacheParent = %s
    """, (idTacheParent,))
    sous_taches_directes = cursor.fetchall()
    cursor.close()
    
    toutes_sous_taches = list(sous_taches_directes)
    
    # Pour chaque sous-tâche directe, récupérer ses propres sous-tâches (récursion)
    for st in sous_taches_directes:
        sous_sous_taches = get_toutes_sous_taches_recursive(conn, st['idTache'])
        toutes_sous_taches.extend(sous_sous_taches)
    
    return toutes_sous_taches


def mettre_a_jour_statut_tache_parente(conn, idTacheParent):
    """
    Met à jour automatiquement le statut d'une tâche parente en fonction de TOUTES ses sous-tâches (récursif)
    
    Logique:
    - Si toutes les sous-tâches (tous niveaux) sont terminées → Tâche parente "Terminée"
    - Si au moins une sous-tâche est en cours/en révision → Tâche parente "En cours"
    - Si au moins une sous-tâche est en retard → Tâche parente "En retard"
    - Sinon → Tâche parente "À faire"
    """
    try:
        # Récupérer TOUTES les sous-tâches (tous niveaux)
        toutes_sous_taches = get_toutes_sous_taches_recursive(conn, idTacheParent)
        
        print(f"[DEBUG] Tâche parente {idTacheParent}: {len(toutes_sous_taches)} sous-tâches trouvées (tous niveaux)")
        
        if not toutes_sous_taches:
            print(f"[DEBUG] Aucune sous-tâche trouvée pour la tâche parente {idTacheParent}, pas de mise à jour")
            return  # Pas de sous-tâches, ne rien changer
        
        total_sous_taches = len(toutes_sous_taches)
        sous_taches_terminees = sum(1 for st in toutes_sous_taches if st['statutTache'] == 'Terminée')
        sous_taches_en_cours = sum(1 for st in toutes_sous_taches if st['statutTache'] in ['En cours', 'En révision'])
        
        print(f"[DEBUG] Sous-tâches (TOUS NIVEAUX): Total={total_sous_taches}, Terminées={sous_taches_terminees}, En cours={sous_taches_en_cours}")
        
        # Vérifier si des sous-tâches sont en retard
        from datetime import datetime
        today = datetime.now().date()
        sous_taches_en_retard = sum(1 for st in toutes_sous_taches 
                                    if st['dateFinTache'] and st['dateFinTache'] < today 
                                    and st['statutTache'] != 'Terminée')
        
        # Déterminer le nouveau statut de la tâche parente
        if sous_taches_terminees == total_sous_taches:
            nouveau_statut = 'Terminée'
        elif sous_taches_en_retard > 0:
            nouveau_statut = 'En retard'
        elif sous_taches_en_cours > 0:
            nouveau_statut = 'En cours'
        else:
            nouveau_statut = 'À faire'
        
        print(f"[DEBUG] Nouveau statut calculé pour tâche parente {idTacheParent}: {nouveau_statut}")
        
        # Mettre à jour le statut de la tâche parente
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tache 
            SET statutTache = %s 
            WHERE idTache = %s
        """, (nouveau_statut, idTacheParent))
        cursor.close()
        
        print(f"[INFO] ✅ Statut de la tâche parente {idTacheParent} mis à jour : {nouveau_statut}")
        
    except Exception as e:
        print(f"[ERREUR] Échec de la mise à jour du statut de la tâche parente {idTacheParent}: {e}")


def mettre_a_jour_statut_projet(conn, idProjet):
    """
    Met à jour automatiquement le statut d'un projet en fonction de TOUTES ses tâches
    
    Logique (examine TOUTES les tâches, tous niveaux confondus):
    - Si toutes les tâches sont terminées → Projet "Terminé"
    - Si au moins une tâche est en cours/en révision → Projet "En cours"
    - Si au moins une tâche est en retard → Projet "En retard"
    - Sinon → Projet "À faire"
    """
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer TOUTES les tâches du projet (tous niveaux confondus)
        cursor.execute("""
            SELECT statutTache, dateFinTache 
            FROM tache 
            WHERE idProjet = %s
        """, (idProjet,))
        taches = cursor.fetchall()
        
        if not taches:
            # Pas de tâches = projet "À faire"
            nouveau_statut = 'À faire'
        else:
            total_taches = len(taches)
            taches_terminees = sum(1 for t in taches if t['statutTache'] == 'Terminée')
            taches_en_cours = sum(1 for t in taches if t['statutTache'] in ['En cours', 'En révision'])
            
            # Vérifier si des tâches sont en retard
            from datetime import datetime
            today = datetime.now().date()
            taches_en_retard = sum(1 for t in taches 
                                  if t['dateFinTache'] and t['dateFinTache'] < today 
                                  and t['statutTache'] != 'Terminée')
            
            # Déterminer le nouveau statut
            if taches_terminees == total_taches:
                nouveau_statut = 'Terminé'
            elif taches_en_retard > 0:
                nouveau_statut = 'En retard'
            elif taches_en_cours > 0:
                nouveau_statut = 'En cours'
            else:
                nouveau_statut = 'À faire'
        
        # Mettre à jour le statut du projet
        cursor.execute("""
            UPDATE projet 
            SET statutProjet = %s 
            WHERE idProjet = %s
        """, (nouveau_statut, idProjet))
        
        cursor.close()
        print(f"[INFO] Statut du projet {idProjet} mis à jour : {nouveau_statut}")
        print(f"[DEBUG] Tâches: Total={total_taches}, Terminées={taches_terminees}, En cours={taches_en_cours}, En retard={taches_en_retard if 'taches_en_retard' in locals() else 0}")
        
    except Exception as e:
        print(f"[ERREUR] Échec de la mise à jour du statut du projet {idProjet}: {e}")


def calculer_progression_tache(conn, idTache):
    """
    Calcule la progression d'une tâche à partir de TOUTES ses heures et sous-tâches (récursif)
    
    Logique:
    1. Récupérer TOUTES les tâches descendantes (sous-tâches, sous-sous-tâches, etc.)
    2. Calculer: total heures travaillées / total heures estimées (tous niveaux confondus)
    3. Si pas d'heures estimées: compter les tâches terminées / total tâches
    4. Si la tâche est terminée: toujours 100%
    
    Returns:
        float: Pourcentage de progression (0-100)
    """
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les infos de la tâche principale
        cursor.execute("""
            SELECT statutTache, heuresEstimees,
                   COALESCE((SELECT SUM(heures) FROM saisie_temps WHERE idTache = %s), 0) as heuresTravaillees
            FROM tache 
            WHERE idTache = %s
        """, (idTache, idTache))
        tache_principale = cursor.fetchone()
        
        if not tache_principale:
            cursor.close()
            return 0
        
        # Si terminée, retourner 100%
        if tache_principale['statutTache'] == 'Terminée':
            cursor.close()
            return 100
        
        # Fonction récursive pour récupérer TOUTES les sous-tâches
        def get_all_subtasks(parent_id):
            cursor.execute("""
                SELECT idTache, statutTache, heuresEstimees,
                       COALESCE((SELECT SUM(heures) FROM saisie_temps WHERE idTache = t.idTache), 0) as heuresTravaillees,
                       (SELECT COUNT(*) FROM tache WHERE idTacheParent = t.idTache) as nb_sous_taches
                FROM tache t
                WHERE idTacheParent = %s
            """, (parent_id,))
            subtasks = cursor.fetchall()
            
            all_tasks = []
            for subtask in subtasks:
                all_tasks.append(subtask)
                # Récursion : ajouter les sous-sous-tâches
                all_tasks.extend(get_all_subtasks(subtask['idTache']))
            
            return all_tasks
        
        # Récupérer toutes les sous-tâches (tous niveaux)
        toutes_sous_taches = get_all_subtasks(idTache)
        
        # Vérifier si la tâche principale a des sous-tâches
        cursor.execute("SELECT COUNT(*) as nb FROM tache WHERE idTacheParent = %s", (idTache,))
        a_des_sous_taches = cursor.fetchone()['nb'] > 0
        
        # NOUVELLE LOGIQUE : Compter toutes les tâches qui ont des heures estimées OU qui sont des feuilles
        # Une tâche parente peut avoir ses propres heures (travail à faire après les sous-tâches)
        taches_a_compter = []
        
        if a_des_sous_taches and toutes_sous_taches:
            # La tâche a des sous-tâches
            # Inclure la tâche principale si elle a des heures estimées
            heures_principale = float(tache_principale['heuresEstimees'] or 0)
            if heures_principale > 0:
                taches_a_compter.append(tache_principale)
            
            # Ajouter toutes les sous-tâches qui sont des feuilles OU qui ont des heures
            for t in toutes_sous_taches:
                heures_est = float(t['heuresEstimees'] or 0)
                est_feuille = t['nb_sous_taches'] == 0
                if est_feuille or heures_est > 0:
                    taches_a_compter.append(t)
        else:
            # Pas de sous-tâches, calculer sur la tâche elle-même
            taches_a_compter = [tache_principale]
        
        if not taches_a_compter:
            cursor.close()
            return 0
        
        # LOGIQUE HYBRIDE : Heures + Statuts combinés (pondérée par les heures)
        # Pour chaque tâche, prendre le maximum entre:
        # - Progression par heures (si heures estimées > 0)
        # - Progression par statut (100% si terminée, 0% sinon)
        
        progressions_ponderees = []
        poids_total = 0
        
        for t in taches_a_compter:
            heures_est = float(t['heuresEstimees'] or 0)
            heures_trav = float(t['heuresTravaillees'] or 0)
            statut = t['statutTache']
            
            # Le poids est basé sur les heures estimées (si > 0), sinon poids de 1
            poids = heures_est if heures_est > 0 else 1
            
            # Progression par statut
            prog_statut = 100 if statut in ['Terminée', 'Terminé'] else 0
            
            # Progression par heures
            if heures_est > 0:
                prog_heures = min((heures_trav / heures_est) * 100, 100)
            else:
                prog_heures = 0
            
            # Prendre le maximum des deux
            prog_tache = max(prog_statut, prog_heures)
            
            # Pondérer par les heures
            progressions_ponderees.append(prog_tache * poids)
            poids_total += poids
        
        # Moyenne pondérée des progressions
        progression = sum(progressions_ponderees) / poids_total if poids_total > 0 else 0
        cursor.close()
        return round(progression, 2)
        
    except Exception as e:
        print(f"[ERREUR] Échec du calcul de progression de la tâche {idTache}: {e}")
        return 0


def calculer_progression_projet(conn, idProjet):
    """
    Calcule la progression globale d'un projet à partir de TOUTES les tâches (tous niveaux)
    
    La progression est calculée en tenant compte de:
    1. TOUTES les heures estimées vs travaillées (tâches + sous-tâches + sous-sous-tâches, etc.)
    2. TOUTES les tâches terminées vs total des tâches (tous niveaux confondus)
    
    Priorité : Heures travaillées / Heures estimées (si heures estimées > 0)
    Sinon : Nombre de tâches terminées / Total des tâches
    
    Returns:
        float: Pourcentage de progression (0-100)
    """
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer TOUTES les tâches du projet
        cursor.execute("""
            SELECT 
                idTache, 
                statutTache, 
                heuresEstimees,
                COALESCE((SELECT SUM(heures) FROM saisie_temps WHERE idTache = t.idTache), 0) as heuresTravaillees,
                (SELECT COUNT(*) FROM tache WHERE idTacheParent = t.idTache) as nb_sous_taches
            FROM tache t
            WHERE idProjet = %s
        """, (idProjet,))
        toutes_les_taches = cursor.fetchall()
        
        if not toutes_les_taches:
            cursor.close()
            return 0
        
        # NOUVELLE LOGIQUE : Compter toutes les tâches qui ont des heures estimées OU qui sont des feuilles
        # Une tâche parente peut avoir ses propres heures (travail à faire après les sous-tâches)
        taches_a_compter = []
        for t in toutes_les_taches:
            heures_est = float(t['heuresEstimees'] or 0)
            est_feuille = t['nb_sous_taches'] == 0
            
            # Compter la tâche si :
            # - C'est une feuille (pas de sous-tâches)
            # - OU elle a des heures estimées > 0 (même si c'est un parent)
            if est_feuille or heures_est > 0:
                taches_a_compter.append(t)
        
        if not taches_a_compter:
            cursor.close()
            return 0
        
        # LOGIQUE HYBRIDE : Heures + Statuts combinés
        # Pour chaque tâche à compter, prendre le maximum entre:
        # - Progression par heures (si heures estimées > 0)
        # - Progression par statut (100% si terminée, 0% sinon)
        
        progressions_ponderees = []
        poids_total = 0
        
        for t in taches_a_compter:
            heures_est = float(t['heuresEstimees'] or 0)
            heures_trav = float(t['heuresTravaillees'] or 0)
            statut = t['statutTache']
            
            # Le poids est basé sur les heures estimées (si > 0), sinon poids de 1
            poids = heures_est if heures_est > 0 else 1
            
            # Progression par statut
            prog_statut = 100 if statut in ['Terminée', 'Terminé'] else 0
            
            # Progression par heures
            if heures_est > 0:
                prog_heures = min((heures_trav / heures_est) * 100, 100)
            else:
                prog_heures = 0
            
            # Prendre le maximum des deux
            prog_tache = max(prog_statut, prog_heures)
            
            # Pondérer par les heures
            progressions_ponderees.append(prog_tache * poids)
            poids_total += poids
        
        # Moyenne pondérée des progressions
        progression = sum(progressions_ponderees) / poids_total if poids_total > 0 else 0
        cursor.close()
        
        return round(progression, 2)
        
    except Exception as e:
        print(f"[ERREUR] Échec du calcul de progression du projet {idProjet}: {e}")
        return 0


def mettre_a_jour_hierarchie_complete(conn, idTache):
    """
    Met à jour toute la hiérarchie: tâche parente (si existe) puis projet
    
    Cette fonction assure la cohérence des statuts sur toute la chaîne:
    Sous-tâche → Tâche parente → Projet
    
    Args:
        conn: Connexion à la base de données
        idTache: Identifiant de la tâche modifiée/ajoutée/supprimée
    """
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les informations de la tâche
        cursor.execute("""
            SELECT idTacheParent, idProjet 
            FROM tache 
            WHERE idTache = %s
        """, (idTache,))
        tache_info = cursor.fetchone()
        
        if tache_info:
            id_tache_parent = tache_info['idTacheParent']
            id_projet = tache_info['idProjet']
            cursor.close()
            
            print(f"[DEBUG] Tâche {idTache}: idTacheParent={id_tache_parent}, idProjet={id_projet}")
            
            # Si c'est une sous-tâche, mettre à jour la tâche parente d'abord
            if id_tache_parent is not None and id_tache_parent != 0:
                print(f"[DEBUG] C'est une sous-tâche, mise à jour de la tâche parente {id_tache_parent}")
                mettre_a_jour_statut_tache_parente(conn, id_tache_parent)
                print(f"[INFO] Hiérarchie: Sous-tâche {idTache} → Tâche parente {id_tache_parent} mise à jour")
            else:
                print(f"[DEBUG] C'est une tâche principale (pas de parent)")
            
            # Toujours mettre à jour le projet en dernier
            mettre_a_jour_statut_projet(conn, id_projet)
            print(f"[INFO] Hiérarchie: Projet {id_projet} mis à jour")
        else:
            cursor.close()
            print(f"[ATTENTION] Tâche {idTache} introuvable pour mise à jour hiérarchie")
            
    except Exception as e:
        print(f"[ERREUR] Échec de la mise à jour de la hiérarchie complète: {e}")
        import traceback
        traceback.print_exc()


def verifier_taches_en_retard(conn, idProjet=None):
    """
    Vérifie et met à jour les tâches en retard (date limite dépassée et non terminées)
    
    Args:
        conn: Connexion à la base de données
        idProjet: Si spécifié, vérifier uniquement les tâches de ce projet
    """
    from datetime import date
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Requête pour trouver les tâches en retard
        query = """
            SELECT idTache, titreTache, dateFinTache, statutTache
            FROM tache
            WHERE dateFinTache < %s
            AND statutTache NOT IN ('Terminée', 'En retard')
        """
        params = [date.today()]
        
        if idProjet:
            query += " AND idProjet = %s"
            params.append(idProjet)
        
        cursor.execute(query, params)
        taches_en_retard = cursor.fetchall()
        
        # Mettre à jour le statut des tâches en retard
        for tache in taches_en_retard:
            cursor.execute("""
                UPDATE tache 
                SET statutTache = 'En retard'
                WHERE idTache = %s
            """, (tache['idTache'],))
            print(f"[AUTO] Tâche {tache['idTache']} '{tache['titreTache']}' passée en retard (échéance: {tache['dateFinTache']})")
        
        if taches_en_retard:
            conn.commit()
            print(f"[AUTO] {len(taches_en_retard)} tâche(s) mise(s) à jour en statut 'En retard'")
        
        cursor.close()
        
    except Exception as e:
        print(f"[ERREUR] Échec de la vérification des tâches en retard: {e}")


def valider_dates_tache(conn, idProjet, idTacheParent, dateDebutTache, dateFinTache):
    """
    Valide que les dates d'une tâche respectent les contraintes hiérarchiques
    
    Règles:
    - Si tâche parente : les dates doivent être dans la plage de la tâche parente
    - Si tâche principale : les dates doivent être dans la plage du projet
    - dateDebut doit être <= dateFin
    
    Returns:
        (bool, str): (est_valide, message_erreur)
    """
    from datetime import datetime
    
    if not dateDebutTache or not dateFinTache:
        return True, ""  # Pas de dates = pas de validation
    
    # Convertir les dates en objets datetime si ce sont des strings
    if isinstance(dateDebutTache, str):
        dateDebutTache = datetime.strptime(dateDebutTache, '%Y-%m-%d').date()
    if isinstance(dateFinTache, str):
        dateFinTache = datetime.strptime(dateFinTache, '%Y-%m-%d').date()
    
    # Vérifier que dateDebut <= dateFin
    if dateDebutTache > dateFinTache:
        return False, "La date de début doit être antérieure ou égale à la date de fin"
    
    cursor = conn.cursor(dictionary=True)
    
    # Si c'est une sous-tâche, vérifier les dates de la tâche parente
    if idTacheParent:
        cursor.execute("""
            SELECT dateDebutTache, dateFinTache, titreTache
            FROM tache 
            WHERE idTache = %s
        """, (idTacheParent,))
        tache_parente = cursor.fetchone()
        
        if tache_parente:
            debut_parent = tache_parente['dateDebutTache']
            fin_parent = tache_parente['dateFinTache']
            
            if debut_parent and fin_parent:
                if dateDebutTache < debut_parent:
                    cursor.close()
                    return False, f"La date de début ({dateDebutTache}) doit être après celle de la tâche parente ({debut_parent})"
                if dateFinTache > fin_parent:
                    cursor.close()
                    return False, f"La date de fin ({dateFinTache}) doit être avant celle de la tâche parente ({fin_parent})"
    
    # Si c'est une tâche principale (pas de parent), vérifier les dates du projet
    else:
        cursor.execute("""
            SELECT dateDebut, dateFin, nomProjet
            FROM projet 
            WHERE idProjet = %s
        """, (idProjet,))
        projet = cursor.fetchone()
        
        if projet:
            debut_projet = projet['dateDebut']
            fin_projet = projet['dateFin']
            
            if debut_projet and fin_projet:
                if dateDebutTache < debut_projet:
                    cursor.close()
                    return False, f"La date de début ({dateDebutTache}) doit être après celle du projet ({debut_projet})"
                if dateFinTache > fin_projet:
                    cursor.close()
                    return False, f"La date de fin ({dateFinTache}) doit être avant celle du projet ({fin_projet})"
    
    cursor.close()
    return True, ""


@taches_bp.route('/taches', methods=['POST'])
def ajouter_tache():
    """
    Ajoute une nouvelle tâche dans la base de données
    
    Body attendu (JSON):
    {
        "idProjet": 1,
        "idTacheParent": null,  // null si tâche principale, sinon ID de la tâche parente
        "titreTache": "Titre de la tâche",
        "descriptionTache": "Description",
        "statutTache": "À faire",
        "prioriteTache": "Moyenne",
        "dateDebutTache": "2024-01-01",
        "dateFinTache": "2024-01-31",
        "heuresEstimees": 10
    }
    """
    data = request.get_json(silent=True) or {}
    try:
        conn = get_db_connection()
        
        # VALIDATION DES DATES
        est_valide, message_erreur = valider_dates_tache(
            conn,
            data.get('idProjet'),
            data.get('idTacheParent'),
            data.get('dateDebutTache'),
            data.get('dateFinTache')
        )
        
        if not est_valide:
            conn.close()
            return jsonify({'message': message_erreur}), 400
        
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tache
            (idProjet, idTacheParent, titreTache, nomTache, descriptionTache, statutTache,
             prioriteTache, dateDebutTache, dateFinTache, heuresEstimees, idEtat)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                data.get('idProjet'),
                data.get('idTacheParent'),
                data.get('titreTache'),
                data.get('titreTache'),  # nomTache = titreTache
                data.get('descriptionTache'),
                data.get('statutTache'),
                data.get('prioriteTache'),
                data.get('dateDebutTache'),
                data.get('dateFinTache'),
                data.get('heuresEstimees', 0),
                1  # idEtat par défaut
            )
        )
        idTache = cursor.lastrowid  # Récupérer l'ID de la tâche créée
        
        # Mettre à jour toute la hiérarchie (tâche parente + projet)
        mettre_a_jour_hierarchie_complete(conn, idTache)
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tâche ajoutée avec succès', 'idTache': idTache}), 201
    except Exception as e:
        import traceback
        print("[API] Erreur ajout tâche:", e)
        traceback.print_exc()
        return jsonify({'message': 'Erreur ajout tâche', 'error': str(e)}), 500


@taches_bp.route('/taches/<int:idProjet>', methods=['GET'])
def get_taches_by_projet(idProjet):
    """
    Retourne la liste des tâches d'un projet donné avec les heures travaillées et la progression
    
    Args:
        idProjet: Identifiant du projet
        
    Retourne:
        Liste des tâches avec leurs informations + heures travaillées + progression calculée récursivement
    """
    conn = get_db_connection()
    
    # Vérifier et mettre à jour les tâches en retard AVANT de les retourner
    verifier_taches_en_retard(conn, idProjet)
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, 
               COALESCE(SUM(st.heures), 0) as heuresTravaillees
        FROM tache t
        LEFT JOIN saisie_temps st ON t.idTache = st.idTache
        WHERE t.idProjet = %s
        GROUP BY t.idTache
    """, (idProjet,))
    data = cursor.fetchall()
    
    # Calculer la progression pour chaque tâche (récursivement)
    for tache in data:
        tache['progressionTache'] = calculer_progression_tache(conn, tache['idTache'])
    
    cursor.close()
    conn.close()
    return jsonify(data)


@taches_bp.route('/taches/<int:idTache>', methods=['PUT'])
def update_tache(idTache):
    """
    Modifie une tâche dans la base de données
    
    Args:
        idTache: Identifiant de la tâche à modifier
        
    Body attendu (JSON):
    {
        "titreTache": "Nouveau titre",
        "descriptionTache": "Nouvelle description",
        "statutTache": "En cours",
        "prioriteTache": "Haute",
        "dateDebutTache": "2024-01-01",
        "dateFinTache": "2024-01-31",
        "heuresEstimees": 15
    }
    
    Note: Met à jour automatiquement le statut des sous-tâches et de la tâche parente
    """
    data = request.get_json(silent=True) or {}
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les infos de la tâche pour validation
        cursor.execute("SELECT idProjet, idTacheParent FROM tache WHERE idTache = %s", (idTache,))
        tache_info = cursor.fetchone()
        
        if not tache_info:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Tâche introuvable'}), 404
        
        # Gérer les valeurs None pour les champs optionnels
        titre = data.get('titreTache')
        description = data.get('descriptionTache')
        statut = data.get('statutTache')
        priorite = data.get('prioriteTache')
        date_debut = data.get('dateDebutTache') if data.get('dateDebutTache') else None
        date_fin = data.get('dateFinTache') if data.get('dateFinTache') else None
        heures = data.get('heuresEstimees') if data.get('heuresEstimees') else 0
        
        # VALIDATION DES DATES
        est_valide, message_erreur = valider_dates_tache(
            conn,
            tache_info['idProjet'],
            tache_info['idTacheParent'],
            date_debut,
            date_fin
        )
        
        if not est_valide:
            cursor.close()
            conn.close()
            return jsonify({'message': message_erreur}), 400
        
        print(f"Mise à jour tâche {idTache}: {data}")
        
        cursor = conn.cursor()  # Recréer le cursor sans dictionary pour l'update
        
        cursor.execute(
            """
            UPDATE tache 
            SET titreTache = %s, nomTache = %s, descriptionTache = %s, 
                statutTache = %s, prioriteTache = %s, 
                dateDebutTache = %s, dateFinTache = %s, heuresEstimees = %s
            WHERE idTache = %s
            """,
            (
                titre,
                titre,  # nomTache = titreTache
                description,
                statut,
                priorite,
                date_debut,
                date_fin,
                heures,
                idTache
            )
        )
        
        # Si la tâche est marquée comme terminée, marquer toutes ses sous-tâches comme terminées
        if statut == 'Terminée':
            cursor.execute("UPDATE tache SET statutTache = 'Terminée' WHERE idTacheParent = %s", (idTache,))
            conn.commit()
            print(f"[INFO] Toutes les sous-tâches de la tâche {idTache} ont été marquées comme terminées")
        
        # Mettre à jour toute la hiérarchie (tâche parente + projet)
        mettre_a_jour_hierarchie_complete(conn, idTache)
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tâche modifiée avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de la modification de la tâche: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Erreur lors de la modification de la tâche: {str(e)}'}), 500


def supprimer_tache_recursive(conn, cursor, idTache):
    """
    Supprime récursivement une tâche et toutes ses sous-tâches (tous niveaux)
    Supprime aussi toutes les données associées (affectations, heures, dépendances)
    
    Args:
        conn: Connexion à la base de données
        cursor: Curseur de la base de données
        idTache: ID de la tâche à supprimer
    """
    # 1. Trouver toutes les sous-tâches directes
    cursor.execute("SELECT idTache FROM tache WHERE idTacheParent = %s", (idTache,))
    sous_taches = cursor.fetchall()
    
    # 2. Supprimer récursivement chaque sous-tâche
    for sous_tache in sous_taches:
        supprimer_tache_recursive(conn, cursor, sous_tache['idTache'])
    
    # 3. Supprimer les données associées à cette tâche
    # Supprimer les saisies de temps (avant la tâche car ON DELETE RESTRICT)
    cursor.execute("DELETE FROM saisie_temps WHERE idTache = %s", (idTache,))
    
    # Supprimer les dépendances (CASCADE déjà géré par FK)
    cursor.execute("DELETE FROM dependance_tache WHERE idPredecesseur = %s OR idSuccesseur = %s", (idTache, idTache))
    
    # Supprimer les affectations (CASCADE déjà géré par FK)
    cursor.execute("DELETE FROM affectation_tache WHERE idTache = %s", (idTache,))
    
    # 4. Supprimer la tâche elle-même
    cursor.execute("DELETE FROM tache WHERE idTache = %s", (idTache,))
    
    print(f"[INFO] Tâche {idTache} et toutes ses sous-tâches supprimées")


@taches_bp.route('/taches/<int:idTache>', methods=['DELETE'])
def delete_tache(idTache):
    """
    Supprime une tâche et toutes ses sous-tâches (récursif tous niveaux)
    Supprime également toutes les données associées (heures, affectations, dépendances)
    
    Args:
        idTache: Identifiant de la tâche à supprimer
        
    Note: Suppression récursive complète de toute la hiérarchie
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer les informations de la tâche avant de la supprimer
        cursor.execute("SELECT idProjet, idTacheParent FROM tache WHERE idTache = %s", (idTache,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return jsonify({'message': 'Tâche introuvable'}), 404
        
        id_projet = result['idProjet']
        id_tache_parent = result['idTacheParent']
        
        # Supprimer récursivement la tâche et toutes ses sous-tâches (tous niveaux)
        supprimer_tache_recursive(conn, cursor, idTache)
        
        # Mettre à jour la hiérarchie après suppression
        if id_projet:
            # Si c'était une sous-tâche, mettre à jour la tâche parente
            if id_tache_parent:
                mettre_a_jour_statut_tache_parente(conn, id_tache_parent)
                print(f"[INFO] Suppression: Tâche parente {id_tache_parent} mise à jour")
            
            # Toujours mettre à jour le projet
            mettre_a_jour_statut_projet(conn, id_projet)
            print(f"[INFO] Suppression: Projet {id_projet} mis à jour")
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Tâche supprimée avec succès'}), 200
    except Exception as e:
        print(f"[ERREUR] Suppression de la tâche {idTache}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': f'Erreur lors de la suppression de la tâche: {str(e)}'}), 500


# ==================== GESTION DES MEMBRES DE LA TÂCHE ====================

@taches_bp.route('/taches/<int:idTache>/membres', methods=['GET'])
def get_tache_membres(idTache):
    """
    Retourne les membres assignés à une tâche
    
    Args:
        idTache: Identifiant de la tâche
        
    Retourne:
        Liste des employés assignés à la tâche avec leurs informations
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT e.idEmploye, e.nomEmploye, e.prenomEmploye, e.courrielEmploye
            FROM employe e
            INNER JOIN affectation_tache at ON e.idEmploye = at.idEmploye
            WHERE at.idTache = %s
            """,
            (idTache,)
        )
        membres = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(membres), 200
    except Exception as e:
        print(f"Erreur lors de la récupération des membres de la tâche: {e}")
        return jsonify([]), 200


@taches_bp.route('/taches/<int:idTache>/membres', methods=['POST'])
def assign_tache_membres(idTache):
    """
    Assigne des membres à une tâche
    
    Args:
        idTache: Identifiant de la tâche
        
    Body attendu (JSON):
    {
        "membres": [1, 2, 3]  // Liste des idEmploye
    }
    
    Note: Remplace les affectations existantes
    """
    data = request.get_json(silent=True) or {}
    membres = data.get('membres', [])  # Liste des idEmploye
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Supprimer les anciennes affectations
        cursor.execute("DELETE FROM affectation_tache WHERE idTache = %s", (idTache,))
        
        # Ajouter les nouvelles affectations
        for idEmploye in membres:
            cursor.execute(
                "INSERT INTO affectation_tache (idEmploye, idTache, roleSurLaTache) VALUES (%s, %s, %s)",
                (idEmploye, idTache, 'Collaborateur')
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Membres assignés à la tâche avec succès'}), 200
    except Exception as e:
        print(f"Erreur lors de l'assignation des membres à la tâche: {e}")
        return jsonify({'message': 'Erreur lors de l\'assignation des membres'}), 500


# ==================== CALCUL DE PROGRESSION ====================

@taches_bp.route('/taches/<int:idTache>/progression', methods=['GET'])
def get_progression_tache(idTache):
    """
    Retourne la progression calculée d'une tâche
    
    Args:
        idTache: Identifiant de la tâche
        
    Returns:
        JSON avec le pourcentage de progression
    """
    try:
        conn = get_db_connection()
        progression = calculer_progression_tache(conn, idTache)
        conn.close()
        return jsonify({'idTache': idTache, 'progression': progression}), 200
    except Exception as e:
        print(f"Erreur lors du calcul de progression de la tâche {idTache}: {e}")
        return jsonify({'message': 'Erreur lors du calcul de progression'}), 500


@taches_bp.route('/projets/<int:idProjet>/progression', methods=['GET'])
def get_progression_projet(idProjet):
    """
    Retourne la progression calculée d'un projet
    
    Args:
        idProjet: Identifiant du projet
        
    Returns:
        JSON avec le pourcentage de progression
    """
    try:
        conn = get_db_connection()
        progression = calculer_progression_projet(conn, idProjet)
        conn.close()
        return jsonify({'idProjet': idProjet, 'progression': progression}), 200
    except Exception as e:
        print(f"Erreur lors du calcul de progression du projet {idProjet}: {e}")
        return jsonify({'message': 'Erreur lors du calcul de progression'}), 500


@taches_bp.route('/projets/<int:idProjet>/recalculer', methods=['POST'])
def recalculer_projet(idProjet):
    """
    Force le recalcul du statut et de la progression d'un projet
    
    Args:
        idProjet: Identifiant du projet
        
    Returns:
        JSON avec le nouveau statut et la progression
    """
    try:
        conn = get_db_connection()
        
        # Recalculer le statut du projet
        mettre_a_jour_statut_projet(conn, idProjet)
        
        # Recalculer la progression
        progression = calculer_progression_projet(conn, idProjet)
        
        # Récupérer le projet mis à jour
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT statutProjet FROM projet WHERE idProjet = %s", (idProjet,))
        projet = cursor.fetchone()
        cursor.close()
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'idProjet': idProjet, 
            'statutProjet': projet['statutProjet'] if projet else None,
            'progression': progression
        }), 200
    except Exception as e:
        print(f"Erreur lors du recalcul du projet {idProjet}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'message': 'Erreur lors du recalcul du projet'}), 500
