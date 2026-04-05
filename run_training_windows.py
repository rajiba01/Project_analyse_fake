"""
run_training_windows.py

Script d'entraînement complet et automatisé.
"""

import sys
from pathlib import Path
import logging
import torch
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

print("="*80)
print("🚀 DEEPFAKE DETECTOR - TRAINING PIPELINE")
print("="*80)

# ========================================
# ÉTAPE 0: VÉRIFICATIONS
# ========================================

print("\n✅ ÉTAPE 0: Vérifications")
print("-"*80)

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Device: {device}")

if device == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")

dataset_path = Path("C:\\data\\datasets\\FaceForensics\\data")

if not dataset_path.exists():
    print(f"\n❌ ERROR: Dataset not found!")
    print(f"   Expected: {dataset_path}")
    print(f"\n   Download first:")
    print(f"   python download_faceforensics_zip.py")
    sys.exit(1)

print(f"✓ Dataset found: {dataset_path}")

# ========================================
# ÉTAPE 1: FILTRER LES DONNÉES
# ========================================

print("\n✅ ÉTAPE 1: Filtrage du dataset")
print("-"*80)

from apps.ai.datasets.filter_and_prepare import VideoFilter

filter_obj = VideoFilter("C:\\data\\filtered_dataset")

print("Filtering videos (may take 20-30 minutes)...")

result = filter_obj.filter_faceforensics(
    dataset_path=str(dataset_path),
    max_videos_per_class=500
)

filter_obj.save_filtered_dataset(
    real_videos=result['real_videos'],
    fake_videos=result['fake_videos']
)

stats = result['stats']
print(f"\n✓ Real videos: {stats['real_valid']}/{stats['real_total']}")
print(f"✓ Fake videos: {stats['fake_valid']}/{stats['fake_total']}")

# ========================================
# ÉTAPE 2: CRÉER LE MODÈLE
# ========================================

print("\n✅ ÉTAPE 2: Création du modèle")
print("-"*80)

from apps.ai.models.deepfake_detector import DeepfakeDetector

model = DeepfakeDetector(
    num_frames=30,
    hidden_size=256,
    num_layers=2,
    dropout=0.5
)

num_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Modèle créé: {num_params:,} paramètres")

# ========================================
# ÉTAPE 3: CRÉER LES DATALOADERS
# ========================================

print("\n✅ ÉTAPE 3: Chargement des données")
print("-"*80)

from apps.ai.optimized_data_loader import create_optimized_dataloaders

train_loader, val_loader, test_loader = create_optimized_dataloaders(
    dataset_dir="C:\\data\\filtered_dataset",
    batch_size=16,
    num_workers=0,
    num_frames=30,
    augment_train=True
)

print(f"✓ Train batches: {len(train_loader)}")
print(f"✓ Val batches: {len(val_loader)}")
print(f"✓ Test batches: {len(test_loader)}")

# ========================================
# ÉTAPE 4: ENTRAÎNER
# ========================================

print("\n✅ ÉTAPE 4: Entraînement du modèle")
print("-"*80)
print("⏳ This will take 4-6 hours on GPU...\n")

from apps.ai.trainer.video_trainer import VideoTrainer

output_dir = Path("C:\\checkpoints_filtered")

trainer = VideoTrainer(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    test_loader=test_loader,
    device=device,
    output_dir=str(output_dir)
)

history = trainer.train(
    epochs=100,
    lr=5e-5,
    weight_decay=1e-5,
    optimizer_type='adam',
    use_scheduler=True
)

# ========================================
# ÉTAPE 5: TESTER
# ========================================

print("\n✅ ÉTAPE 5: Test du modèle")
print("-"*80)

metrics = trainer.test()

# ========================================
# RÉSULTATS FINAUX
# ========================================

print("\n" + "="*80)
print("📊 RÉSULTATS FINAUX")
print("="*80)

results = {
    'device': device,
    'epochs_trained': len(history['train_loss']),
    'best_val_accuracy': max(history['val_acc']),
    'final_metrics': metrics
}

results_file = output_dir / "final_results.json"
with open(results_file, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Accuracy:  {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
print(f"Precision: {metrics['precision']:.4f}")
print(f"Recall:    {metrics['recall']:.4f}")
print(f"F1-Score:  {metrics['f1']:.4f}")
print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")

print("\n✅ Model trained and saved!")
print(f"   Location: {output_dir / 'best_model.pth'}")

print("\n" + "="*80)
print("🎉 TRAINING COMPLETE!")
print("="*80)

print(f"""
📝 Next steps:

1️⃣  Make predictions:
    python predict_videos.py \\
      --video "C:\\path\\to\\video.mp4" \\
      --model "{output_dir / 'best_model.pth'}"

2️⃣  Start API:
    python manage.py runserver

3️⃣  View results:
    Open: {results_file}
""")