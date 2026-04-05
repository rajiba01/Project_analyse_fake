"""
create_dummy_datasets.py

Créer des mini-datasets de test INSTANTANÉMENT.
"""

import os
import numpy as np
import cv2
import librosa
import soundfile as sf
from pathlib import Path
import json

print("="*80)
print("🎬 CREATING DUMMY DATASETS FOR TESTING")
print("="*80)

# Créer répertoires
Path("./media/videos/test").mkdir(parents=True, exist_ok=True)
Path("./media/images/real").mkdir(parents=True, exist_ok=True)
Path("./media/images/fake").mkdir(parents=True, exist_ok=True)
Path("./media/audio/real").mkdir(parents=True, exist_ok=True)
Path("./media/audio/fake").mkdir(parents=True, exist_ok=True)

# ========================================
# 🖼️ CRÉER IMAGES
# ========================================

print("\n🖼️  Creating images...")

# Vraies images (pattern aléatoire)
for i in range(10):
    img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    cv2.imwrite(f"./media/images/real/real_{i:04d}.jpg", img)

# Fakes (patterns différents)
for i in range(10):
    img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    # Ajouter du noise pour "fake"
    noise = np.random.normal(0, 25, img.shape)
    img = np.clip(img + noise, 0, 255).astype(np.uint8)
    cv2.imwrite(f"./media/images/fake/fake_{i:04d}.jpg", img)

print("   ✓ 20 images créées")

# ========================================
# 🎵 CRÉER AUDIOS
# ========================================

print("\n🎵 Creating audio files...")

sr = 16000

# Vrais audios (sinus)
for i in range(10):
    duration = 3
    t = np.linspace(0, duration, sr * duration)
    # Onde sine simple
    y = np.sin(2 * np.pi * 440 * t)  # 440 Hz
    y = y * 0.3
    sf.write(f"./media/audio/real/real_{i:04d}.wav", y, sr)

# Fakes (bruits)
for i in range(10):
    duration = 3
    y = np.random.randn(sr * duration) * 0.1
    sf.write(f"./media/audio/fake/fake_{i:04d}.wav", y, sr)

print("   ✓ 20 audios créés")

# ========================================
# 🎬 CRÉER VIDÉOS
# ========================================

print("\n🎬 Creating video files...")

# Vraies vidéos
for i in range(5):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f"./media/videos/test/real_{i:04d}.mp4", fourcc, 30.0, (224, 224))
    
    for frame_idx in range(30):  # 30 frames = 1 seconde à 30fps
        frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        out.write(frame)
    
    out.release()

# Fakes
for i in range(5):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(f"./media/videos/test/fake_{i:04d}.mp4", fourcc, 30.0, (224, 224))
    
    for frame_idx in range(30):
        frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        # Ajouter noise
        noise = np.random.normal(0, 25, frame.shape)
        frame = np.clip(frame + noise, 0, 255).astype(np.uint8)
        out.write(frame)
    
    out.release()

print("   ✓ 10 vidéos créées")

# ========================================
# 📊 CRÉER ANNOTATIONS
# ========================================

print("\n📊 Creating annotations...")

# Images
image_annotations = []

for i in range(10):
    image_annotations.append({
        'path': f'./media/images/real/real_{i:04d}.jpg',
        'label': 0,
        'label_name': 'REAL',
        'type': 'image'
    })

for i in range(10):
    image_annotations.append({
        'path': f'./media/images/fake/fake_{i:04d}.jpg',
        'label': 1,
        'label_name': 'FAKE',
        'type': 'image'
    })

with open('./media/images/annotations.json', 'w') as f:
    json.dump(image_annotations, f, indent=2)

# Audio
audio_annotations = []

for i in range(10):
    audio_annotations.append({
        'path': f'./media/audio/real/real_{i:04d}.wav',
        'label': 0,
        'label_name': 'REAL',
        'type': 'audio'
    })

for i in range(10):
    audio_annotations.append({
        'path': f'./media/audio/fake/fake_{i:04d}.wav',
        'label': 1,
        'label_name': 'FAKE',
        'type': 'audio'
    })

with open('./media/audio/annotations.json', 'w') as f:
    json.dump(audio_annotations, f, indent=2)

# Video
video_annotations = []

for i in range(5):
    video_annotations.append({
        'path': f'./media/videos/test/real_{i:04d}.mp4',
        'label': 0,
        'label_name': 'REAL',
        'type': 'video'
    })

for i in range(5):
    video_annotations.append({
        'path': f'./media/videos/test/fake_{i:04d}.mp4',
        'label': 1,
        'label_name': 'FAKE',
        'type': 'video'
    })

with open('./media/videos/annotations.json', 'w') as f:
    json.dump(video_annotations, f, indent=2)

print("   ✓ Annotations créées")

# ========================================
# RÉSUMÉ
# ========================================

print("\n" + "="*80)
print("✅ DUMMY DATASETS CREATED!")
print("="*80)

print(f"""
📊 Dataset structure:

./media/
├── images/
│   ├── real/ (10 images)
│   ├── fake/ (10 images)
│   └── annotations.json
├── audio/
│   ├── real/ (10 audios)
│   ├── fake/ (10 audios)
│   └── annotations.json
└── videos/
    ├── test/
    │   ├── real_*.mp4 (5 videos)
    │   ├── fake_*.mp4 (5 videos)
    │   └── annotations.json

Ready to train and test your models!
""")