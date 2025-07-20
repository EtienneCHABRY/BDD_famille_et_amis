import streamlit as st
import mysql.connector
import pandas as pd
import bcrypt
from datetime import datetime
import utilitaires1
import json


# Configuration de la page
st.set_page_config(
    page_title="Gestionnaire de Base de Données",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuration de la base de données (à adapter selon votre configuration)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Adelaide17110!',
    'database': 'mywhoswho',
    'port': 3306
}

# Base de données des utilisateurs (en production, utilisez une vraie base de données)
USERS_DB = {
    'admin': {
        'password': bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'role': 'administrateur',
        'permissions': ['lecture', 'ecriture', 'suppression', 'administration']
    },
    'utilisateur': {
        'password': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'role': 'utilisateur',
        'permissions': ['lecture']
    },
    'editeur': {
        'password': bcrypt.hashpw('edit123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'role': 'éditeur',
        'permissions': ['lecture', 'ecriture']
    }
}

# Fonction de connexion à la base de données
# @st.cache_resource ne pas utiliser le cache, qui est source de difficultés
def init_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        st.error(f"Erreur de connexion à la base de données : {err}")
        return None

# Fonction d'authentification
def authentifier_utilisateur(nom_utilisateur, mot_de_passe):
    if nom_utilisateur in USERS_DB:
        stored_password = USERS_DB[nom_utilisateur]['password'].encode('utf-8')
        if bcrypt.checkpw(mot_de_passe.encode('utf-8'), stored_password):
            return USERS_DB[nom_utilisateur]
    return None

# Fonction pour exécuter une requête SQL

def executer_requete(requete_sql):
    """
    Exécute une requête SQL sur la base connectée et retourne le résultat en DataFrame formaté.

    - Les colonnes dont le nom commence par « date » sont automatiquement formatées en jj/mm/aaaa.
    """
    conn = init_connection()
    if conn is None:
        return "Erreur : connexion à la base impossible."

    cursor = conn.cursor()
    try:
        cursor.execute(requete_sql)
        lignes = cursor.fetchall()

        if not lignes:
            return pd.DataFrame()  # Aucune donnée

        # Récupère les noms de colonnes
        colonnes = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(lignes, columns=colonnes)

        # 🔁 Formater les colonnes date au format français
        df = utilitaires1.format_dates_dataframe(df)

        return df

    except Exception as e:
        return f"Erreur SQL : {e}"

    finally:
        cursor.close()
        conn.close()

# Interface d'accueil
def page_accueil():
    st.title("🗄️ Qui est qui, est né quand, où ?")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Bienvenue dans votre base de connaissances 
        
        Cette application vous permet d'accéder à l'aide-mémoire géré par Etienne: n'hésitez pas à lui demander des améliorations ou des corrections par mail sur sa boite perso.
        
        ### Fonctionnalités disponibles :
        - 🔐 **Authentification sécurisée** avec gestion des droits
        - 📊 **Consultation des données** avec interface intuitive
        - 🔍 **Requêtes personnalisées** selon vos permissions
        - 📈 **Visualisation des résultats** sous forme de tableaux
        - 🔄 **Requêtes interactives** basées sur les résultats précédents
        
        ### Pour commencer :
        1. Connectez-vous avec vos identifiants dans la barre latérale
        2. Sélectionnez le module souhaité
        3. Explorez les données !
        """)
    
    with col2:
        st.info("""
        **Comptes de démonstration :**
        
        **Administrateur :**
        - Utilisateur : admin
        - Mot de passe : admin123
        
        **Éditeur :**
        - Utilisateur : editeur
        - Mot de passe : edit123
        
        **Utilisateur :**
        - Utilisateur : utilisateur
        - Mot de passe : user123
        """)

# Interface de connexion
def interface_connexion():
    st.sidebar.markdown("## 🔐 Connexion")
    
    nom_utilisateur = st.sidebar.text_input("Nom d'utilisateur")
    mot_de_passe = st.sidebar.text_input("Mot de passe", type="password")
    
    if st.sidebar.button("Se connecter"):
        utilisateur = authentifier_utilisateur(nom_utilisateur, mot_de_passe)
        if utilisateur:
            st.session_state.utilisateur = nom_utilisateur
            st.session_state.role = utilisateur['role']
            st.session_state.permissions = utilisateur['permissions']
            st.sidebar.success(f"Connecté en tant que {utilisateur['role']}")
            st.rerun()
        else:
            st.sidebar.error("Identifiants incorrects")

# Interface principale après connexion
def interface_principale():
    st.sidebar.markdown(f"## 👤 {st.session_state.utilisateur}")
    st.sidebar.markdown(f"**Rôle :** {st.session_state.role}")
    
    # Menu de navigation
    menu = st.sidebar.selectbox(
    "Sélectionnez un module :",
    ["Accueil", "Consultation des données", "Requêtes personnalisées", "Requêtes niveau 2", "Historique"]
)

    
    if st.sidebar.button("Se déconnecter"):
        for key in ['utilisateur', 'role', 'permissions']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
    
    # Affichage du module sélectionné
    if menu == "Accueil":
        page_accueil()
    elif menu == "Consultation des données":
        module_consultation()
    elif menu == "Requêtes personnalisées":
        module_requetes()
    elif menu == "Historique":
        module_historique()
    elif menu == "Requêtes niveau 2":
        module_requetes_niveau2()

# Module de consultation des données
def module_consultation():
    st.title("📊 Consultation des Données")
    st.markdown("---")
    
    # Simuler des tables disponibles (à adapter selon votre base)
    tables_disponibles = ["personnes", "typesunions", "unionsorig", "maisons"]
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Sélection de table")
        table_selectionnee = st.selectbox("Choisissez une table :", tables_disponibles)
        if table_selectionnee == "personnes":
            Champs_selectionnes_pardefaut = "nom, prénom, DATE_FORMAT(datenaissance, '%d/%m/%Y') AS 'Né(e) le'"
        else:
            Champs_selectionnes_pardefaut = "*"
        
        
        # Options de filtrage
        st.subheader("Options de filtrage")
        limite = st.number_input("Nombre de lignes à afficher", min_value=1, max_value=1000, value=100,step=12)
        
        if st.button("Consulter la table"):
            requete = f"SELECT {Champs_selectionnes_pardefaut} FROM {table_selectionnee} order by datenaissance LIMIT {limite}"
            
            print (requete)
            resultats = executer_requete(requete)
            
            if isinstance(resultats, pd.DataFrame):
                st.session_state.derniers_resultats = resultats
                st.session_state.derniere_table = table_selectionnee
            else:
                st.error(f"Erreur lors de la consultation : {resultats}")
    
    with col2:
        st.subheader("Résultats")
        if 'derniers_resultats' in st.session_state:
            st.dataframe(st.session_state.derniers_resultats, use_container_width=True)
            
            # Statistiques rapides
            st.subheader("Statistiques")
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Nombre de lignes", len(st.session_state.derniers_resultats))
            with col_stat2:
                st.metric("Nombre de colonnes", len(st.session_state.derniers_resultats.columns))
            with col_stat3:
                st.metric("Table", st.session_state.get('derniere_table', 'N/A'))
        else:
            st.info("Sélectionnez une table pour voir les résultats")

# Module de requêtes personnalisées
def module_requetes():
    st.title("🔍 Requêtes Personnalisées")
    st.markdown("---")
    
    # Vérifier les permissions
    if 'lecture' not in st.session_state.permissions:
        st.error("Vous n'avez pas les permissions nécessaires pour ce module.")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Éditeur de requêtes")
        
        # Requêtes prédéfinies
        requetes_predefinies = {
            "Sélectionner tout": "SELECT * FROM nom_table LIMIT 10",
            "Compter les lignes": "SELECT COUNT(*) as total FROM personnes",
            "Recherche par critère": "SELECT * FROM nom_table WHERE colonne = 'valeur'",
            "Grouper par": "SELECT colonne, COUNT(*) FROM nom_table GROUP BY colonne"
        }
        
        requete_choisie = st.selectbox("Requêtes prédéfinies :", list(requetes_predefinies.keys()))
        
        # Zone de texte pour la requête
        requete_sql = st.text_area(
            "Requête SQL :",
            value=requetes_predefinies[requete_choisie],
            height=150
        )
        
        # Boutons d'action
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            executer = st.button("Exécuter la requête", type="primary")
        with col_btn2:
            if 'ecriture' in st.session_state.permissions:
                st.button("Sauvegarder la requête")
    
    with col2:
        st.subheader("Aide et syntaxe")
        st.markdown("""
        **Exemples de requêtes :**
        
        ```sql
        -- Sélection simple
        SELECT * FROM clients;
        
        -- Avec condition
        SELECT nom, email FROM clients 
        WHERE ville = 'Paris';
        
        -- Avec jointure
        SELECT c.nom, o.date_commande 
        FROM clients c 
        JOIN commandes o ON c.id = o.client_id;
        ```
        
        **Conseils :**
        - Utilisez LIMIT pour limiter les résultats
        - Testez d'abord avec SELECT avant UPDATE/DELETE
        - Les requêtes de modification nécessitent des permissions spéciales
        """)
    
    # Exécution de la requête
    if executer:
        if requete_sql.strip():
            # Vérifier les permissions pour les requêtes de modification
            if any(keyword in requete_sql.upper() for keyword in ['UPDATE', 'DELETE', 'INSERT']):
                if 'ecriture' not in st.session_state.permissions:
                    st.error("Vous n'avez pas les permissions pour modifier les données.")
                    return
            
            resultats = executer_requete(requete_sql)
            
            if isinstance(resultats, pd.DataFrame):
                st.subheader("Résultats de la requête")
                st.dataframe(resultats, use_container_width=True)
                
                # Sauvegarder dans l'historique
                if 'historique' not in st.session_state:
                    st.session_state.historique = []
                
                st.session_state.historique.append({
                    'timestamp': datetime.now(),
                    'utilisateur': st.session_state.utilisateur,
                    'requete': requete_sql,
                    'resultats': len(resultats)
                })
                
                # Possibilité de créer une nouvelle requête basée sur les résultats
                if not resultats.empty:
                    st.subheader("Requête de suivi")
                    if st.button("Créer une requête basée sur ces résultats"):
                        # Exemple : créer une requête pour approfondir
                        st.info("Fonctionnalité de requête de suivi à développer selon vos besoins spécifiques")
            
            else:
                st.success(resultats)
        else:
            st.warning("Veuillez saisir une requête SQL.")

# Module d'historique
def module_historique():
    st.title("📈 Historique des Requêtes")
    st.markdown("---")
    
    if 'historique' not in st.session_state or not st.session_state.historique:
        st.info("Aucune requête dans l'historique.")
        return
    
    # Afficher l'historique
    historique_df = pd.DataFrame(st.session_state.historique)
    
    st.subheader("Requêtes récentes")
    for i, entry in enumerate(reversed(st.session_state.historique[-10:])):  # 10 dernières requêtes
        with st.expander(f"Requête du {entry['timestamp'].strftime('%d/%m/%Y %H:%M:%S')} - {entry['utilisateur']}"):
            st.code(entry['requete'], language='sql')
            st.text(f"Résultats : {entry['resultats']} ligne(s)")
            
            if st.button(f"Réexécuter", key=f"reexec_{i}"):
                resultats = executer_requete(entry['requete'])
                if isinstance(resultats, pd.DataFrame):
                    st.dataframe(resultats)
                else:
                    st.success(resultats)
#module ajouté de claude
def module_requetes_niveau2():
    st.title("🔎 Requêtes niveau 2")
    st.markdown("---")
    if 'lecture' not in st.session_state.permissions:
        st.error("Vous n'avez pas les permissions nécessaires pour ce module.")
        return

    conn = init_connection()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        col_g, col_d = st.columns([2, 1])
        with col_d:
            cursor.execute("SHOW TABLES")
            tables = [r[0] for r in cursor.fetchall()]
            table = st.selectbox("Table :", tables, key="niv2_table")

            champs, champs_types = [], {}
            if table:
                cursor.execute(f"DESCRIBE `{table}`")
                desc = cursor.fetchall()
                champs = [row[0] for row in desc]
                champs_types = {row[0]: row[1].lower() for row in desc}
            champs_sel = st.multiselect("Champs à afficher :", champs, default=champs[:2] if champs else [], key="niv2_fields")

            st.markdown('**Critères de sélection**')
            crits = []
            for field in champs_sel:
                champ_type = champs_types.get(field, '')
                if field.lower().startswith('date'):
                    # Champ date : saisie jj/mm/aaaa
                    date_str = st.text_input(f"{field} (jj/mm/aaaa) :", key=f"n2date_{field}")
                    if date_str:
                        # Validation simple du format
                        try:
                            # Convertir en format SQL (aaaa-mm-jj)
                            dt = datetime.strptime(date_str, "%d/%m/%Y")
                            sql_date = dt.strftime("%Y-%m-%d")
                            crits.append(f"`{field}` = '{sql_date}'")
                        except ValueError:
                            st.warning(f"Format invalide pour {field}, attendu jj/mm/aaaa")
                elif any(x in champ_type for x in ['char', 'text', 'varchar']):
                    valeur = st.text_input(f"{field} contient :", key=f"n2crit_{field}")
                    if valeur:
                        crits.append(f"`{field}` LIKE '%{valeur}%'")
                else:
                    valeur = st.text_input(f"{field} =", key=f"n2crit_{field}")
                    if valeur:
                        crits.append(f"`{field}` = '{valeur}'")

        if table and champs_sel:
            req_auto = f"SELECT {', '.join([f'`{c}`' for c in champs_sel])} FROM `{table}`"
            if crits:
                req_auto += " WHERE " + " AND ".join(crits)
            req_auto += " LIMIT 100"
        else:
            req_auto = ""

        with col_g:
            st.subheader("Éditeur de la requête SQL")
            requete_saisie = st.text_area(
                "Saisissez ou éditez votre requête SQL :",
                value=req_auto if req_auto else "",
                height=150, key="niv2_sql")
            if st.button("Lancer la requête", key="niv2_run"):
                if requete_saisie.strip():
                    resultats = executer_requete(requete_saisie.strip())
                    st.session_state['niv2req_lancee'] = requete_saisie
                    st.session_state['niv2req_resultats'] = resultats
                else:
                    st.warning("Veuillez saisir une requête SQL.")

            st.markdown("**Requête exécutée :**")
            st.code(st.session_state.get('niv2req_lancee', ""), language='sql')
            if 'niv2req_resultats' in st.session_state:
                if isinstance(st.session_state['niv2req_resultats'], pd.DataFrame):
                    st.dataframe(st.session_state['niv2req_resultats'], use_container_width=True)
                else:
                    st.info(st.session_state['niv2req_resultats'])

        with col_d:
            st.markdown("**Aperçu de la requête générée :**")
            st.code(req_auto, language='sql')
    finally:
        cursor.close()
        conn.close()
                    
                    
# Application principale
def main():
    # Initialisation de la session
    if 'utilisateur' not in st.session_state:
        page_accueil()
        interface_connexion()
    else:
        interface_principale()

if __name__ == "__main__":
    main()