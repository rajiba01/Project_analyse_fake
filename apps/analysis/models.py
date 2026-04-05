"""
apps/analysis/models.py

Modèles pour gérer les analyses de détection de deepfakes.
- Media: Fichier uploadé
- Analysis: Une analyse
- AnalysisResult: Résultat de l'analyse
"""

from django.conf import settings
from django.db import models
from django.core.validators import FileExtensionValidator
from apps.core.models import BaseModel
from apps.users.models import User
from apps.core.constants import (
    MediaType,
    AnalysisStatus,
    Verdict,
    FileLimits,
    ConfidenceLevel,
)
import os



class Media(BaseModel):
    """
    Modèle pour stocker les fichiers uploadés.
    
    Peut être: Image, Vidéo, ou Audio
    
    Séparé du modèle Analysis pour:
    - Pouvoir réutiliser le même média dans plusieurs analyses
    - Gérer les uploads plus facilement
    - Tracker la taille de stockage
    """
    
   
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medias',
        help_text="L'utilisateur qui a uploadé"
    )
    """L'utilisateur qui a uploadé ce fichier"""
    
   
    
    file = models.FileField(
        upload_to='uploads/medias/%Y/%m/%d/',
        help_text="Le fichier uploadé"
    )
    """
    Explication:
    - upload_to='uploads/medias/%Y/%m/%d/': Organiser par date
    - Exemple: media/uploads/medias/2024/04/04/file.mp4
    - Remplace automatiquement les caractères spéciaux
    """
    
    filename = models.CharField(
        max_length=255,
        help_text="Nom du fichier original"
    )
    """Nom original du fichier (pour affichage)"""
    
 
    
    media_type = models.CharField(
        max_length=20,
        choices=MediaType.choices(),
        help_text="Type de média"
    )
    """
    Explication:
    - Valeurs: "image", "video", "audio"
    - Validé avec MediaType.choices()
    """
    
    file_size = models.BigIntegerField(
        help_text="Taille en bytes"
    )
    """
    Taille du fichier en bytes
    Exemple: 5242880 = 5 MB
    """
    
    file_extension = models.CharField(
        max_length=10,
        help_text="Extension du fichier"
    )
    """Exemple: .mp4, .jpg, .mp3"""
    
    mime_type = models.CharField(
        max_length=50,
        help_text="MIME type"
    )
    """
    Exemple: video/mp4, image/jpeg, audio/mpeg
    Utilisé pour servir le fichier avec le bon type
    """
    
    # ========================================
    # 📐 DIMENSIONS (pour images/vidéos)
    # ========================================
    
    width = models.IntegerField(
        null=True,
        blank=True,
        help_text="Largeur en pixels"
    )
    """Largeur pour images/vidéos"""
    
    height = models.IntegerField(
        null=True,
        blank=True,
        help_text="Hauteur en pixels"
    )
    """Hauteur pour images/vidéos"""
    
    duration = models.FloatField(
        null=True,
        blank=True,
        help_text="Durée en secondes (pour vidéos/audio)"
    )
    """
    Durée en secondes
    Exemple: 120.5 = 2 minutes 0.5 secondes
    """
    
    # ========================================
    # ⚙️ META
    # ========================================
    
    class Meta:
        db_table = 'medias'
        verbose_name = 'Media'
        verbose_name_plural = 'Medias'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['media_type']),
        ]
    
    def __str__(self):
        return f"{self.filename} ({self.media_type})"
    
    # ========================================
    # 🔧 PROPRIÉTÉS
    # ========================================
    
    @property
    def file_size_mb(self):
        """Retourner la taille en MB"""
        return self.file_size / (1024 * 1024)
    
    @property
    def file_size_gb(self):
        """Retourner la taille en GB"""
        return self.file_size / (1024 * 1024 * 1024)
    
    def delete(self, *args, **kwargs):
        """Supprimer le fichier quand on supprime le modèle"""
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)


# ========================================
# 🔬 ANALYSIS MODEL
# ========================================

class Analysis(BaseModel):
    """
    Modèle pour une analyse de détection de deepfake.
    
    Workflow:
    PENDING → PROCESSING → COMPLETED/FAILED
    
    Chaque analyse est une tâche de traitement.
    """
    
    # ========================================
    # 🔗 RELATIONS
    # ========================================
    
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="analyses",
   )
    """L'utilisateur propriétaire"""
    
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name='analyses',
        help_text="Le fichier à analyser"
    )
    """Le fichier médias à analyser"""
    
    # ========================================
    # 📊 STATUS
    # ========================================
    
    status = models.CharField(
        max_length=20,
        choices=AnalysisStatus.choices(),
        default=AnalysisStatus.PENDING.value,
        help_text="État de l'analyse"
    )
    """
    Explication:
    - PENDING: En attente
    - PROCESSING: En cours (le modèle IA tourne)
    - COMPLETED: Terminée avec succès
    - FAILED: Erreur lors du traitement
    """
    
    # ========================================
    # 📝 DESCRIPTION
    # ========================================
    
    title = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Titre/description de l'analyse"
    )
    """Titre optionnel donné par l'utilisateur"""
    
    description = models.TextField(
        blank=True,
        default="",
        help_text="Description détaillée"
    )
    """Description optionnelle"""
    
    # ========================================
    # ⏰ TIMESTAMPS DE TRAITEMENT
    # ========================================
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Quand le traitement a commencé"
    )
    """Timestamp du début du traitement"""
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Quand le traitement s'est terminé"
    )
    """Timestamp de fin du traitement"""
    
    # ========================================
    # 🔄 CELERY TASK
    # ========================================
    
    task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="ID de la task Celery"
    )
    """
    Explication:
    - ID unique de la tâche Celery
    - Permet de tracker la progression
    - Exemple: "a4e5b9c2-1234-5678-abcd-ef1234567890"
    """
    
    # ========================================
    # ⚙️ META
    # ========================================
    
    class Meta:
        db_table = 'analyses'
        verbose_name = 'Analysis'
        verbose_name_plural = 'Analyses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Analysis {self.id} - {self.status}"
    
    # ========================================
    # 🔧 PROPRIÉTÉS
    # ========================================
    
    @property
    def processing_time(self):
        """Temps de traitement en secondes"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None
    
    @property
    def is_completed(self):
        """Vérifier si l'analyse est terminée"""
        return self.status in [
            AnalysisStatus.COMPLETED.value,
            AnalysisStatus.FAILED.value
        ]
    
    @property
    def has_result(self):
        """Vérifier s'il y a un résultat"""
        return hasattr(self, 'result') and self.result is not None


# ========================================
# 📊 ANALYSIS RESULT MODEL
# ========================================

class AnalysisResult(BaseModel):
    """
    Modèle pour stocker les résultats d'une analyse.
    
    Relation OneToOne avec Analysis:
    - Une analyse = un résultat
    
    Contient:
    - Verdict final (AUTHENTIC, FAKE, SUSPICIOUS)
    - Score de confiance
    - Détails du traitement
    """
    
    # ========================================
    # 🔗 RELATIONS
    # ========================================
    
    analysis = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        related_name='result',
        help_text="L'analyse associée"
    )
    """
    Explication:
    - OneToOneField: Une analyse = un résultat
    - on_delete=models.CASCADE: Supprimer le résultat si l'analyse est supprimée
    - related_name='result': analysis.result pour accéder le résultat
    """
    
    # ========================================
    # 🎯 VERDICT
    # ========================================
    
    verdict = models.CharField(
        max_length=20,
        choices=Verdict.choices(),
        help_text="Verdict final"
    )
    """
    Explication:
    - AUTHENTIC: Le média semble authentique
    - FAKE: Le média est un deepfake
    - SUSPICIOUS: À vérifier manuellement
    """
    
    # ========================================
    # 📊 SCORES
    # ========================================
    
    confidence_score = models.FloatField(
        help_text="Score de confiance (0.0 à 1.0)"
    )
    """
    Explication:
    - Valeur entre 0.0 et 1.0
    - 0.0 = pas confiant du tout
    - 1.0 = très confiant
    - Exemple: 0.95 = 95% de confiance
    """
    
    authenticity_score = models.FloatField(
        help_text="Score d'authenticité (0.0 à 1.0)"
    )
    """
    Score d'authenticité du média
    - 0.0 = Sûrement un deepfake
    - 1.0 = Sûrement authentique
    """
    
    deepfake_score = models.FloatField(
        help_text="Score de deepfake (0.0 à 1.0)"
    )
    """
    Score de probabilité d'être un deepfake
    - 0.0 = Probablement pas un deepfake
    - 1.0 = Probablement un deepfake
    """
    
    # ========================================
    # 📝 DÉTAILS
    # ========================================
    
    confidence_level = models.CharField(
    max_length=20,
    choices=ConfidenceLevel.choices,  # <= pas de ()
    default=ConfidenceLevel.MEDIUM,
)
    """Catégorie de confiance"""
    
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Détails supplémentaires (JSON)"
    )
    """
    Exemple:
    {
        "faces_detected": 1,
        "artifacts_found": ["compression", "color_mismatch"],
        "model_predictions": {
            "cnn": 0.92,
            "rnn": 0.88,
            "ensemble": 0.90
        }
    }
    """
    
    # ========================================
    # 📝 RAPPORT
    # ========================================
    
    report = models.TextField(
        blank=True,
        default="",
        help_text="Rapport détaillé en texte"
    )
    """Rapport lisible pour l'utilisateur"""
    
    recommendations = models.TextField(
        blank=True,
        default="",
        help_text="Recommandations"
    )
    """Recommandations basées sur les résultats"""
    
    # ========================================
    # ⚙️ META
    # ========================================
    
    class Meta:
        db_table = 'analysis_results'
        verbose_name = 'Analysis Result'
        verbose_name_plural = 'Analysis Results'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Result - {self.verdict} ({self.confidence_score:.2f})"
    
    # ========================================
    # 🔧 PROPRIÉTÉS
    # ========################################
    
    @property
    def verdict_color(self):
        """Retourner la couleur du verdict (pour le frontend)"""
        return Verdict.get_color(self.verdict)
    
    @property
    def is_high_confidence(self):
        """Vérifier si c'est une haute confiance"""
        return self.confidence_level == ConfidenceLevel.HIGH.value


# ========================================
# 🔍 ANALYSIS DETAIL MODEL (Optionnel)
# ========================================

class AnalysisDetail(BaseModel):
    """
    Modèle pour les détails détaillés d'une analyse.
    
    Utile pour:
    - Stocker les frames extraites (pour vidéos)
    - Faces détectées
    - Artefacts trouvés
    - Métadonnées détaillées
    """
    
    # ========================================
    # 🔗 RELATIONS
    # ========================================
    
    analysis = models.OneToOneField(
        Analysis,
        on_delete=models.CASCADE,
        related_name='detail',
        help_text="L'analyse associée"
    )
    """Relation OneToOne avec Analysis"""
    
    # ========================================
    # 🔍 DÉTAILS
    # ========================================
    
    frames_analyzed = models.IntegerField(
        default=0,
        help_text="Nombre de frames analysées (pour vidéos)"
    )
    """Nombre de frames/images analysées"""
    
    faces_detected = models.IntegerField(
        default=0,
        help_text="Nombre de visages détectés"
    )
    """Nombre de visages trouvés"""
    
    artifacts = models.JSONField(
        default=list,
        blank=True,
        help_text="Artefacts détectés"
    )
    """
    Exemple:
    [
        "color_mismatch",
        "edge_artifacts",
        "inconsistent_lighting"
    ]
    """
    
    processing_models = models.JSONField(
        default=dict,
        blank=True,
        help_text="Modèles utilisés et leurs scores"
    )
    """
    Exemple:
    {
        "face_detection": "yolo_v8",
        "deepfake_detection": "xception",
        "ensemble": "voting"
    }
    """
    
    # ========================================
    # ⚙️ META
    # ========================================
    
    class Meta:
        db_table = 'analysis_details'
        verbose_name = 'Analysis Detail'
        verbose_name_plural = 'Analysis Details'
    
    def __str__(self):
        return f"Detail - Analysis {self.analysis.id}"
