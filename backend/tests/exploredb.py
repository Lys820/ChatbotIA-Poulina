#!/usr/bin/env python
"""
EXPLORE ORACLE DB – Découvre les colonnes réelles
"""
import oracledb
from dotenv import load_dotenv
import os

load_dotenv()

ORACLE_DSN = os.getenv("ORACLE_DSN")
ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")

print("\n" + "=" * 70)
print("EXPLORATION ORACLE DB")
print("=" * 70)

try:
    conn = oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )
    cursor = conn.cursor()
    
    # List all tables
    print("\n1️⃣  TABLES DISPONIBLES")
    print("-" * 70)
    
    cursor.execute("""
        SELECT table_name 
        FROM user_tables 
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    table_names = [t[0] for t in tables]
    
    for table in table_names:
        print(f"  - {table}")
    
    # For each table, show columns
    print("\n2️⃣  DÉTAILS DES TABLES (colonnes)")
    print("-" * 70)
    
    for table in table_names:
        cursor.execute(f"""
            SELECT column_name, data_type
            FROM user_tab_columns
            WHERE table_name = '{table}'
            ORDER BY column_id
        """)
        
        cols = cursor.fetchall()
        print(f"\n{table}:")
        for col_name, col_type in cols:
            print(f"    - {col_name} ({col_type})")
        
        # Show sample data
        print(f"    Exemples :")
        try:
            cursor.execute(f"SELECT * FROM {table} WHERE ROWNUM <= 3")
            rows = cursor.fetchall()
            for row in rows:
                print(f"      {row}")
        except:
            print(f"      (impossible de lire)")
    
    # Check specific tables we need
    print("\n3️⃣  TABLES REQUISES POUR POULINA")
    print("-" * 70)
    
    required_tables = [
        "demande_analyse",
        "centre_elevage", 
        "batiment",
        "souche",
        "laboratoire",
        "laborantin",
        "maladie",
        "historique_maladie"
    ]
    
    for req_table in required_tables:
        if req_table.upper() in [t.upper() for t in table_names]:
            print(f"  ✓ {req_table}")
        else:
            print(f"  ❌ {req_table} MANQUANTE")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ Exploration terminée")
    print("=" * 70)
    print("\nCopie-colle la structure au dessus et dis-moi")
    print("si les noms de colonnes sont différents de ceux attendus.")

except Exception as e:
    print(f"❌ Erreur : {e}")
    import traceback
    traceback.print_exc()