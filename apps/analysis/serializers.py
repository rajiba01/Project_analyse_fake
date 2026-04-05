"""
apps/analysis/serializers.py

Sérializers pour l'analyse.
"""

from rest_framework import serializers
from apps.analysis.models import Media, Analysis, AnalysisResult, AnalysisDetail
from apps.users.models import User
from apps.core.constants import MediaType, AnalysisStatus, Verdict
from apps.core.validators import validate_media_file

# ========================================
# 📁 MEDIA SERIALIZER
# ========================================

class MediaSerializer(serializers.ModelSerializer):
    """Sérializer pour afficher un média"""
    
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = [
            'id',
            'filename',
            'media_type',
            'file_size',
            'file_size_mb',
            'file_extension',
            'mime_type',
            'width',
            'height',
            'duration',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'file_size',
            'file_size_mb',
            'file_extension',
            'mime_type',
            'width',
            'height',
            'duration',
            'created_at',
        ]
    
    def get_file_size_mb(self, obj):
        """Retourner la taille en MB"""
        return round(obj.file_size_mb, 2)


# ========================================
# 🎯 ANALYSIS UPLOAD SERIALIZER
# ========================================

class AnalysisUploadSerializer(serializers.Serializer):
    """
    Sérializer pour uploader un fichier et créer une analyse.
    
    Utilisé pour:
    - POST /api/v1/analysis/upload/ → Créer une nouvelle analyse
    """
    
    file = serializers.FileField(
        required=True,
        help_text="Le fichier à analyser"
    )
    
    media_type = serializers.ChoiceField(
        choices=MediaType.values(),
        required=True,
        help_text="Type de média (image, video, audio)"
    )
    
    title = serializers.CharField(
        required=False,
        max_length=255,
        allow_blank=True,
        help_text="Titre optionnel"
    )
    
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Description optionnelle"
    )
    
    def validate(self, data):
        """Valider le fichier"""
        file = data['file']
        media_type = data['media_type']
        
        # Valider avec notre validateur personnalisé
        validate_media_file(file, media_type)
        
        return data
    
    def create(self, validated_data):
        """
        Créer le Media et l'Analysis.
        """
        from django.utils import timezone
        from apps.analysis.tasks import analyze_media_task
        import mimetypes
        import os
        
        file = validated_data['file']
        media_type = validated_data['media_type']
        user = self.context['request'].user
        
        # Créer le Media
        filename = file.name
        ext = os.path.splitext(filename)[1][1:].lower()
        mime_type, _ = mimetypes.guess_type(filename)
        
        media = Media.objects.create(
            user=user,
            file=file,
            filename=filename,
            media_type=media_type,
            file_size=file.size,
            file_extension=ext,
            mime_type=mime_type or 'application/octet-stream'
        )
        
        # Créer l'Analysis
        analysis = Analysis.objects.create(
            user=user,
            media=media,
            title=validated_data.get('title', ''),
            description=validated_data.get('description', ''),
            status=AnalysisStatus.PENDING.value
        )
        
        # Lancer la tâche Celery
        task = analyze_media_task.delay(analysis.id)
        analysis.task_id = task.id
        analysis.save()
        
        return analysis


# ========================================
# 📊 ANALYSIS RESULT SERIALIZER
# ========================================

class AnalysisResultSerializer(serializers.ModelSerializer):
    """Sérializer pour afficher les résultats d'une analyse"""
    
    verdict_color = serializers.CharField(read_only=True)
    
    class Meta:
        model = AnalysisResult
        fields = [
            'id',
            'verdict',
            'verdict_color',
            'confidence_score',
            'authenticity_score',
            'deepfake_score',
            'confidence_level',
            'report',
            'recommendations',
            'details',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'verdict',
            'confidence_score',
            'authenticity_score',
            'deepfake_score',
            'confidence_level',
            'report',
            'recommendations',
            'details',
            'created_at',
        ]


# ========================================
# 📝 ANALYSIS DETAIL SERIALIZER
# ========================================

class AnalysisDetailSerializer(serializers.ModelSerializer):
    """Sérializer pour les détails d'une analyse"""
    
    class Meta:
        model = AnalysisDetail
        fields = [
            'id',
            'frames_analyzed',
            'faces_detected',
            'artifacts',
            'processing_models',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'frames_analyzed',
            'faces_detected',
            'artifacts',
            'processing_models',
            'created_at',
        ]


# ========================================
# 🔬 ANALYSIS SERIALIZER - COMPLET
# ========================================

class AnalysisSerializer(serializers.ModelSerializer):
    """
    Sérializer complet pour une analyse.
    
    Inclut:
    - Infos de l'analyse
    - Infos du média
    - Résultats (si terminée)
    """
    
    media = MediaSerializer(read_only=True)
    result = AnalysisResultSerializer(read_only=True)
    detail = AnalysisDetailSerializer(read_only=True)
    processing_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Analysis
        fields = [
            'id',
            'media',
            'status',
            'title',
            'description',
            'result',
            'detail',
            'started_at',
            'completed_at',
            'processing_time',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'media',
            'status',
            'result',
            'detail',
            'started_at',
            'completed_at',
            'created_at',
            'updated_at',
        ]
    
    def get_processing_time(self, obj):
        """Retourner le temps de traitement"""
        if obj.processing_time:
            return round(obj.processing_time, 2)
        return None


# ========================================
# 📋 ANALYSIS LIST SERIALIZER
# ========================================

class AnalysisListSerializer(serializers.ModelSerializer):
    """
    Sérializer allégé pour lister les analyses.
    
    Moins de données que AnalysisSerializer pour économiser la bande passante.
    """
    
    media = MediaSerializer(read_only=True)
    verdict = serializers.SerializerMethodField()
    
    class Meta:
        model = Analysis
        fields = [
            'id',
            'media',
            'status',
            'title',
            'verdict',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'media',
            'status',
            'title',
            'created_at',
            'updated_at',
        ]
    
    def get_verdict(self, obj):
        """Retourner le verdict s'il existe"""
        if hasattr(obj, 'result') and obj.result:
            return obj.result.verdict
        return None
