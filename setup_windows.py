"""
setup_windows.py

Setup complet du projet Windows.
"""

import os
import sys
import subprocess
from pathlib import Path

print("="*80)
print("🚀 DEEPFAKE DETECTOR - WINDOWS SETUP")
print("="*80)

# ========================================
# 1️⃣ CRÉER LES RÉPERTOIRES
# ========================================

print("\n📂 Step 1: Creating directories...")

dirs = {
    'data': Path("C:\\data\\datasets"),
    'filtered': Path("C:\\data\\filtered_dataset"),
    'checkpoints': Path("C:\\checkpoints_filtered"),
    'logs': Path("./logs"),
    'media': Path("./media"),
}

for name, path in dirs.items():
    path.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {path}")

# ========================================
# 2️⃣ VÉRIFIER PYTHON & GPU
# ========================================

print("\n🐍 Step 2: Checking Python environment...")

print(f"  Python version: {sys.version}")

try:
    import torch
    print(f"  PyTorch installed: {torch.__version__}")
    
    if torch.cuda.is_available():
        print(f"  ✓ GPU available: {torch.cuda.get_device_name(0)}")
        print(f"    Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
    else:
        print(f"  ⚠️  GPU not available - will use CPU (slow!)")
except ImportError:
    print(f"  ✗ PyTorch not installed - run: pip install -r requirements.txt")

# ========================================
# 3️⃣ INITIALISER DJANGO
# ========================================

print("\n🔧 Step 3: Initializing Django...")

try:
    subprocess.check_call([
        sys.executable, 'manage.py', 'migrate'
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"  ✓ Database migrated")
except Exception as e:
    print(f"  ⚠️  Migration issue: {e}")

# ========================================
# 4️⃣ CRÉER SUPERUSER (OPTIONNEL)
# ========================================

create_user = input("\nCreate superuser? (y/n): ").lower() == 'y'

if create_user:
    print("\n👤 Creating superuser...")
    os.system(f"{sys.executable} manage.py createsuperuser")

# ========================================
# 5️⃣ TÉLÉCHARGER DATASET
# ========================================

print("\n" + "="*80)
print("Next step: Download dataset")
print("="*80)

download_choice = input("\nDownload dataset now? (1=Mini/2=Full/3=Skip): ").strip() or "3"

if download_choice == "1":
    print("\n📥 Mini dataset (2GB - fast)...")
    subprocess.Popen([sys.executable, 'download_faceforensics_zip.py'])
    
elif download_choice == "2":
    print("\n📥 Full dataset (150GB - better)...")
    subprocess.Popen([sys.executable, 'download_faceforensics_zip.py'])

# ========================================
# 6️⃣ AFFICHER LES PROCHAINES ÉTAPES
# ========================================

print("\n" + "="*80)
print("✅ SETUP COMPLETE!")
print("="*80)

print("""
📋 NEXT STEPS:

1️⃣  Download dataset:
    python download_faceforensics_zip.py

2️⃣  Filter the dataset:
    python apps/ai/datasets/filter_and_prepare.py \\
      --dataset "C:\\data\\datasets\\FaceForensics\\data" \\
      --output "C:\\data\\filtered_dataset"

3️⃣  Train the model:
    python run_training_windows.py

4️⃣  Make predictions:
    python predict_videos.py \\
      --video "path/to/video.mp4" \\
      --model "C:\\checkpoints_filtered\\best_model.pth"

5️⃣  Start the API server:
    python manage.py runserver

📚 Documentation:
   - API: Visit http://localhost:8000/api/
   - Admin: Visit http://localhost:8000/admin/
   - Docs: Read docs/README.md
""")

print("="*80)