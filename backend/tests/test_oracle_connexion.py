#!/usr/bin/env python
"""
DEBUG ORACLE – Test de connexion direct
"""
import sys

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    ORACLE CONNECTION DEBUG                                 ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

# Step 1 : Check drivers
print("\n1️⃣  VÉRIFICATION DES DRIVERS ORACLE")
print("=" * 70)

try:
    import oracledb
    print("✓ oracledb installé")
    print(f"  Version: {oracledb.__version__}")
except ImportError:
    print("❌ oracledb NOT installed")
    print("   Installe : pip install oracledb")
    sys.exit(1)

# Step 2 : Load .env
print("\n2️⃣  CHARGEMENT .env")
print("=" * 70)

from dotenv import load_dotenv
import os

load_dotenv()

ORACLE_DSN = os.getenv("ORACLE_DSN", "").strip()
ORACLE_USER = os.getenv("ORACLE_USER", "").strip()
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD", "").strip()

print(f"ORACLE_DSN: {ORACLE_DSN}")
print(f"ORACLE_USER: {ORACLE_USER}")
print(f"ORACLE_PASSWORD: {'*' * len(ORACLE_PASSWORD) if ORACLE_PASSWORD else '❌ VIDE'}")

if not ORACLE_DSN or not ORACLE_USER:
    print("\n❌ Erreur : ORACLE_DSN ou ORACLE_USER manquant dans .env")
    sys.exit(1)

# Step 3 : Parse DSN
print("\n3️⃣  PARSING DSN")
print("=" * 70)

if ":" in ORACLE_DSN and "/" in ORACLE_DSN:
    parts = ORACLE_DSN.split(":")
    host = parts[0]
    port_sid = parts[1].split("/")
    port = port_sid[0]
    sid = port_sid[1] if len(port_sid) > 1 else ""
    
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"SID/Service: {sid}")
else:
    print(f"⚠️  DSN format non standard : {ORACLE_DSN}")

# Step 4 : Try connection
print("\n4️⃣  TEST DE CONNEXION")
print("=" * 70)

try:
    print(f"Connexion à {ORACLE_USER}@{ORACLE_DSN}...")
    
    # Essaye avec oracledb
    conn = oracledb.connect(
        user=ORACLE_USER,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )
    
    print("✓ CONNEXION RÉUSSIE !")
    
    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM DUAL")
    result = cursor.fetchone()
    print(f"✓ Query test OK: {result}")
    
    # List tables
    print("\n5️⃣  TABLES DISPONIBLES")
    print("=" * 70)
    
    cursor.execute("""
        SELECT table_name 
        FROM user_tables 
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    if tables:
        print(f"✓ {len(tables)} tables trouvées :")
        for table in tables[:10]:  # Show first 10
            print(f"   - {table[0]}")
        if len(tables) > 10:
            print(f"   ... et {len(tables) - 10} autres")
    else:
        print("⚠️  Aucune table trouvée")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ CONNEXION ÉCHOUÉE")
    print(f"\nErreur: {type(e).__name__}")
    print(f"Message: {str(e)}")
    
    print(f"\n🔍 DIAGNOSTIC :")
    print(f"  1. Vérifie que Oracle tourne sur {host}:{port}")
    print(f"  2. Vérifie username/password (pll5175a)")
    print(f"  3. Vérifie le SID/Service Name ({sid})")
    print(f"  4. Vérifie le firewall/réseau (telline.univ-tlse3.fr)")
    print(f"  5. Essaye de te connecter manuellement avec SQL Developer")
    
    sys.exit(1)

print("\n" + "=" * 70)
print("✅ ORACLE CONFIGURATION OK")
print("=" * 70)
print("\nTu peux maintenant utiliser : python test_oracle.py")