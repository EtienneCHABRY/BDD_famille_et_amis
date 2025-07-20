from datetime import datetime
import pandas as pd

def FormatDateComplet(datexx):
    """
    Prend en entrée une date (au format chaîne, datetime ou Timestamp)
    et la retourne au format : jour (sans le zéro) mois (en toutes lettres, en français) année sur 4 chiffres.
    Exemple : 1 janvier 2025, 19 juillet 2025
    """
    # Gestion si l'entrée est déjà de type datetime, sinon on tente de parser
    if not isinstance(datexx, datetime):
        try:
            datexx = datetime.strptime(str(datexx), "%Y-%m-%d")
        except ValueError:
            try:
                datexx = datetime.strptime(str(datexx), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return str(datexx)  # Retour brut si non reconnu

    # Liste des mois en français
    mois_fr = ["janvier", "février", "mars", "avril", "mai", "juin",
               "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    jour = int(datexx.day)
    mois = mois_fr[datexx.month - 1]
    annee = datexx.year
    return f"{jour} {mois} {annee}"

def format_dates_dataframe(df):
    """
    Convertit les colonnes dont le nom commence par 'date' au format jj/mm/aaaa.
    """
    if not isinstance(df, pd.DataFrame):
        return df

    for col in df.columns:
        if col.lower().startswith('date'):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True).dt.strftime('%d/%m/%Y')
            except Exception:
                pass
    return df
