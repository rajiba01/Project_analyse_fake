from apps.ai_models.detectors.deepfake_detector import FastDemoDetector
from apps.results.models import AnalysisResult

def run_analysis_pipeline(analysis_instance):
    """
    Exécute le détecteur sur le média et génère le résultat final.
    """
    # 1. Instancier le détecteur
    detector = FastDemoDetector()
    
    # 2. Récupérer le chemin du fichier sur le disque
    file_path = analysis_instance.media.file.path
    
    # 3. Lancer l'analyse (C'est ultra rapide)
    result_data = detector.process_media(file_path)
    
    # 4. Sauvegarder dans la base de données (Table des résultats)
    AnalysisResult.objects.create(
        analysis=analysis_instance,
        data=result_data,
        confidence=result_data.get("confidence", 0.0),
        verdict=result_data.get("verdict", "UNKNOWN")
    )
    
    # 5. Mettre à jour le statut de l'analyse (Optionnel mais recommandé)
    analysis_instance.status = "COMPLETED"
    analysis_instance.save()
    
    return result_data