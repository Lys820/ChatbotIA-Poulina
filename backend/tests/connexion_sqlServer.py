#!/usr/bin/env python
"""
TEST CONNEXION SQL SERVER - Diagnostic complet
Verifie la connexion a SQL Server et charge les donnees
"""
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

print("""
================================================================================
                    TEST CONNEXION SQL SERVER POULINA
================================================================================
""")

# Etape 1: Verifier drivers
print("\n1. VERIFICATION DES DRIVERS ODBC")
print("-" * 80)

try:
    import pyodbc
    print("Drivers ODBC disponibles:")
    for driver in pyodbc.drivers():
        if 'SQL Server' in driver:
            print(f"  - {driver}")
except ImportError:
    print("ERROR: pyodbc non installe")
    print("Installation: pip install pyodbc")
    sys.exit(1)

# Etape 2: Charger .env
print("\n2. CHARGEMENT .env")
print("-" * 80)

from dotenv import load_dotenv
import os

load_dotenv()

SQLSERVER_SERVER = os.getenv("SQLSERVER_SERVER", "").strip()
SQLSERVER_DATABASE = os.getenv("SQLSERVER_DATABASE", "").strip()
SQLSERVER_USER = os.getenv("SQLSERVER_USER", "").strip()
SQLSERVER_PASSWORD = os.getenv("SQLSERVER_PASSWORD", "").strip()

print(f"SQLSERVER_SERVER: {SQLSERVER_SERVER}")
print(f"SQLSERVER_DATABASE: {SQLSERVER_DATABASE}")
print(f"SQLSERVER_USER: {SQLSERVER_USER}")
print(f"SQLSERVER_PASSWORD: {'*' * len(SQLSERVER_PASSWORD) if SQLSERVER_PASSWORD else 'VIDE'}")

if not SQLSERVER_SERVER or not SQLSERVER_DATABASE or not SQLSERVER_USER:
    print("\nERROR: Donnees SQL Server manquantes dans .env")
    sys.exit(1)

# Etape 3: Test connexion
print("\n3. TEST DE CONNEXION")
print("-" * 80)

try:
    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={SQLSERVER_SERVER};'
        f'DATABASE={SQLSERVER_DATABASE};'
        f'UID={SQLSERVER_USER};'
        f'PWD={SQLSERVER_PASSWORD}'
    )
    print(f"Connection string: {connection_string[:80]}...")
    
    conn = pyodbc.connect(connection_string)
    print("Connexion reussie!")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM dbo.centre_elevage")
    result = cursor.fetchone()
    print(f"Centres trouves: {result[0]}")
    
    cursor.close()
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    print("\nDiagnostic:")
    print("  1. Verifier que SQL Server tourne")
    print("  2. Verifier le nom du serveur (localhost, SQLSERVER-PC, etc.)")
    print("  3. Verifier les credentials (utilisateur/mot de passe)")
    print("  4. Verifier le firewall")
    print("  5. Verifier que la base POULINA existe")
    sys.exit(1)

# Etape 4: Charger donnees
print("\n4. CHARGEMENT DES DONNEES")
print("-" * 80)

try:
    import pandas as pd
    
    # Analyses
    query_a = """
    SELECT TOP 5 
        id_demande, num_analyse, id_centre, meilleure_souche, conforme, statut
    FROM dbo.demande_analyse
    ORDER BY id_demande DESC
    """
    df_a = pd.read_sql(query_a, conn)
    print(f"Analyses: {len(df_a)} lignes")
    if len(df_a) > 0:
        print(f"  Colonnes: {list(df_a.columns)[:4]}")
    
    # Labos
    query_l = """
    SELECT TOP 5
        id_labo, nom_labo, gouvernorat, score_global
    FROM dbo.laboratoire
    WHERE actif = 1
    """
    df_l = pd.read_sql(query_l, conn)
    print(f"Labos: {len(df_l)} lignes")
    if len(df_l) > 0:
        print(f"  Colonnes: {list(df_l.columns)}")
    
    # Souches
    query_s = "SELECT COUNT(*) as count FROM dbo.souche"
    df_s = pd.read_sql(query_s, conn)
    print(f"Souches: {df_s.iloc[0]['count']} au total")
    
    conn.close()
    
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print("\n" + "=" * 80)
print("SUCCESS: SQL Server OK et donnees accessibles")
print("=" * 80)
print("\nProchaines etapes:")
print("  1. Copier database_sqlserver.py dans app/data/")
print("  2. Copier config_sqlserver.py dans app/core/")
print("  3. Mettre a jour main.py avec le nouvel endpoint /train-from-sqlserver")
print("  4. Lancer: python main.py")
print("  5. Tester: POST http://localhost:8000/api/v1/analyses/train-from-sqlserver")