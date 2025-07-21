import PyInstaller.__main__
import os

# Nom du script principal et nom de l'exécutable souhaité
nom_script = 'gui2.py'
nom_executable = 'OptimisationDecoupeGui'

# Vérifie que le script principal existe
if not os.path.exists(nom_script):
    print(f"❌ Erreur : Le script '{nom_script}' est introuvable.")
else:
    print(f"🚀 Lancement de la création de l'exécutable pour '{nom_script}'...")

    # Exécute PyInstaller avec les options souhaitées
    PyInstaller.__main__.run([
        nom_script,
        '--onefile',
        '--clean',  # Nettoie les anciens fichiers de build
        f'--name={nom_executable}'
    ])

    print("\n✅ Processus terminé. L'exécutable se trouve dans le dossier 'dist'.")