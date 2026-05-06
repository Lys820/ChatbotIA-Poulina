#!/usr/bin/env python
"""
TEST ORACLE TRAINING – Windows compatible
Pas besoin de curl, juste Python
"""
import asyncio
import httpx
import json


async def test_oracle_training():
    """Teste /train-from-oracle endpoint."""
    BASE = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient(timeout=60) as client:
        print("\n" + "=" * 70)
        print("ENTRAÎNEMENT DEPUIS ORACLE")
        print("=" * 70)
        
        try:
            print("\nConnexion Oracle et récupération des données...")
            print("(Cela peut prendre quelques secondes)\n")
            
            r = await client.post(f"{BASE}/analyses/train-from-oracle")
            
            print(f"Status: {r.status_code}\n")
            
            # Handle both dict and tuple responses
            if isinstance(r.content, bytes):
                try:
                    data = r.json()
                except:
                    data = {"error": "Could not parse response"}
            else:
                data = r.content
            
            print(f"Raw response type: {type(data)}\n")
            
            if r.status_code == 200:
                # If it's a tuple (data, status_code), extract the data
                if isinstance(data, tuple):
                    data = data[0]
                
                print("✓ SUCCÈS")
                
                # Safely get values
                if isinstance(data, dict):
                    print(f"  Message: {data.get('message', 'OK')}")
                    print(f"\n  Analyses : {data.get('analyses', {}).get('docs', 'N/A')} docs")
                    print(f"  Labos    : {data.get('labos', {}).get('docs', 'N/A')} docs")
                    
                    if 'model_status' in data:
                        print(f"\n  Souche model : {data['model_status'].get('souche', {}).get('model', 'N/A')}")
                        print(f"  Souche accuracy : {data['model_status'].get('souche', {}).get('accuracy', 0):.3f}")
                        print(f"  Labo model : {data['model_status'].get('labo', {}).get('model', 'N/A')}")
                        print(f"  Labo accuracy : {data['model_status'].get('labo', {}).get('accuracy', 0):.3f}")
                    
                    print(f"\n  Entraîné à : {data.get('trained_at', 'N/A')}")
                else:
                    print(f"  Réponse: {str(data)[:200]}")
            else:
                print("❌ ERREUR")
                if isinstance(data, dict):
                    print(f"  {data.get('message', str(data))}")
                else:
                    print(f"  {str(data)[:200]}")
        
        except Exception as e:
            print(f"❌ Erreur : {e}")
            import traceback
            traceback.print_exc()
            print(f"\nVérifies :")
            print(f"  1. Le serveur tourne ? (python main.py)")
            print(f"  2. Oracle configuré dans .env ? (ORACLE_DSN, ORACLE_USER, ORACLE_PASSWORD)")
            print(f"  3. Oracle est accessible ?")


async def test_csv_upload():
    """Teste le fallback CSV upload."""
    BASE = "http://localhost:8000/api/v1"

    async with httpx.AsyncClient(timeout=30) as client:
        print("\n" + "=" * 70)
        print("FALLBACK : CSV UPLOAD")
        print("=" * 70)
        print("\nSi Oracle ne marche pas, tu peux uploader un CSV :\n")
        
        try:
            with open("test_analyses.csv", "rb") as f1, open("test_labos.csv", "rb") as f2:
                files = {
                    "file_analyses": ("test_analyses.csv", f1),
                    "file_labos": ("test_labos.csv", f2),
                }
                r = await client.post(f"{BASE}/analyses/upload", files=files)
            
            print(f"Status: {r.status_code}")
            data = r.json()
            
            if r.status_code == 200:
                print("✓ CSV upload réussi")
                print(f"  Analyses : {data['analyses'].get('docs', 0)} docs")
                print(f"  Labos    : {data['labos'].get('docs', 0)} docs")
            else:
                print(f"❌ Erreur : {data.get('message', str(data))}")
        
        except FileNotFoundError:
            print("❌ Fichiers CSV non trouvés")
            print("   Tape d'abord : python test_quick.py")
        except Exception as e:
            print(f"❌ Erreur : {e}")


async def main():
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║         POULINA – TEST ORACLE TRAINING (Windows compatible)                ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    # Try Oracle first
    await test_oracle_training()
    
    # Show CSV fallback
    print("\n")
    await test_csv_upload()
    
    print("\n" + "=" * 70)
    print("Test terminé")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())