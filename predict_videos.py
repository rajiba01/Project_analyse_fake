"""
predict_videos.py

Faire des prédictions sur des vidéos.
"""

import sys
from pathlib import Path
import argparse
import logging
import torch
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent))

from apps.ai.models.deepfake_detector import DeepfakeDetector
from apps.ai.predictor.video_predictor import VideoPredictor

def main():
    parser = argparse.ArgumentParser(description='Predict deepfake on video')
    parser.add_argument('--video', type=str, required=True, help='Path to video')
    parser.add_argument('--model', type=str, required=True, help='Path to model checkpoint')
    
    args = parser.parse_args()
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    print("="*70)
    print("🔮 DEEPFAKE PREDICTION")
    print("="*70)
    
    # Initialiser predictor
    predictor = VideoPredictor(
        model_path=args.model,
        model_class=DeepfakeDetector,
        device=device,
        num_frames=30
    )
    
    # Prédire
    result = predictor.predict(args.video)
    
    # Afficher résultat
    print("\n" + "="*70)
    print("📊 RESULT")
    print("="*70)
    
    if result['status'] == 'success':
        print(f"\n✅ {result['prediction']}")
        print(f"Confidence: {result['percentage']}")
        print(f"\nScores:")
        print(f"  REAL: {result['score_real']:.4f} ({result['score_real']*100:.2f}%)")
        print(f"  FAKE: {result['score_fake']:.4f} ({result['score_fake']*100:.2f}%)")
    else:
        print(f"❌ Error: {result.get('error', 'Unknown')}")
    
    print("="*70)
    
    # Sauvegarder résultat
    output_file = Path(args.video).parent / f"{Path(args.video).stem}_prediction.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n✓ Result saved: {output_file}")

if __name__ == '__main__':
    main()