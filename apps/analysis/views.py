"""
apps/analysis/views.py

Vues (endpoints) pour l'analyse - AVEC INTÉGRATION IA.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from django.core.files.storage import default_storage
from django.utils import timezone
from pathlib import Path
import tempfile
import logging
import torch

from apps.analysis.models import Analysis, Media, AnalysisResult
from apps.analysis.serializers import (
    AnalysisUploadSerializer,
    AnalysisSerializer,
    AnalysisListSerializer,
    AnalysisResultSerializer,
    MediaSerializer,
)
from apps.core.exceptions import (
    AnalysisNotFoundError,
    AnalysisNotCompletedError,
    PermissionDeniedError,
)
from apps.core.constants import AnalysisStatus, Verdict, ConfidenceLevel
from apps.analysis.services import run_analysis_pipeline

# ========================================
# 🤖 IMPORT AI MODELS
# ========================================

from apps.analysis.services import run_analysis_pipeline

logger = logging.getLogger(__name__)

# ========================================
# 📊 ANALYSIS VIEWSET
# ========================================

class AnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour les analyses avec intégration IA.
    
    Endpoints:
    - POST   /api/v1/analysis/upload/ → Uploader et créer une analyse
    - GET    /api/v1/analysis/ → Lister mes analyses
    - GET    /api/v1/analysis/{id}/ → Détails d'une analyse
    - GET    /api/v1/analysis/{id}/result/ → Résultats
    - GET    /api/v1/analysis/{id}/status/ → Statut actuel
    - DELETE /api/v1/analysis/{id}/ → Supprimer une analyse
    """
    
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'media__media_type']
    search_fields = ['title', 'description', 'media__filename']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    # ========================================
    # 🔐 PERMISSIONS
    # ========================================
    
    def get_queryset(self):
        """Retourner seulement les analyses de l'utilisateur"""
        user = self.request.user
        
        if user.is_staff:
            return Analysis.objects.all()
        
        return Analysis.objects.filter(user=user)
    
    def check_object_permission(self, request, obj):
        """Vérifier que l'utilisateur a accès à l'analyse"""
        user = request.user
        
        if user.is_staff or obj.user == user:
            return True
        
        raise PermissionDeniedError(
            detail="Vous n'avez pas accès à cette analyse"
        )
    
    # ========================================
    # 📤 UPLOAD ENDPOINT
    # ========================================
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """
        POST /api/v1/analysis/upload/
        
        Uploader un fichier et créer une nouvelle analyse.
        
        Request:
        {
            "file": <fichier>,
            "media_type": "video",  # audio/image/video/document
            "title": "Mon analyse",
            "description": "Description optionnelle"
        }
        
        Response:
        {
            "id": 1,
            "media": {...},
            "status": "PROCESSING",
            "created_at": "2024-04-04T10:30:00Z",
            "message": "Analyse en cours..."
        }
        HTTP 201 CREATED
        """
        
        serializer = AnalysisUploadSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Créer l'analyse
            analysis = serializer.save()
            
            logger.info(
                f"✅ Nouvelle analyse créée: {analysis.id} "
                f"par {request.user.email}"
            )
            
            # Lancer l'analyse en arrière-plan (ASYNC)
            # self.run_analysis_async(analysis)
            run_analysis_pipeline(analysis)
            
            # Retourner les détails
            response_serializer = AnalysisSerializer(analysis)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )
        
        except Exception as e:
            logger.error(f"❌ Erreur création analyse: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ========================================
    # 🤖 RUN ANALYSIS
    # ========================================
    
    def run_analysis_async(self, analysis):
        """
        Lancer l'analyse IA.
        
        Détecte le type de média et utilise le modèle approprié.
        """
        
        try:
            # Marquer comme en cours
            analysis.status = AnalysisStatus.PROCESSING.value
            analysis.started_at = timezone.now()
            analysis.save()
            
            logger.info(f"🔄 Lancement analyse: {analysis.id}")
            
            # Obtenir le fichier
            media = analysis.media
            file_path = media.file.path
            
            # Déterminer le type et analyser
            if media.media_type == 'audio':
                result_data = self.analyze_audio(file_path)
            
            elif media.media_type == 'image':
                result_data = self.analyze_image(file_path)
            
            elif media.media_type == 'video':
                result_data = self.analyze_video(file_path)
            
            elif media.media_type == 'document':
                result_data = self.analyze_document(file_path)
            
            else:
                raise ValueError(f"Type de média inconnu: {media.media_type}")
            
            # Créer le résultat
            result = AnalysisResult.objects.create(
                analysis=analysis,
                verdict=result_data.get('verdict'),
                confidence_score=result_data.get('confidence_score'),
                authenticity_score=result_data.get('authenticity_score'),
                deepfake_score=result_data.get('deepfake_score'),
                confidence_level=result_data.get('confidence_level'),
                report=result_data.get('report'),
                recommendations=result_data.get('recommendations'),
                details=result_data.get('details', {})
            )
            
            # Mettre à jour l'analyse
            analysis.status = AnalysisStatus.COMPLETED.value
            analysis.completed_at = timezone.now()
            analysis.save()
            
            logger.info(
                f"✅ Analyse terminée: {analysis.id} - "
                f"Verdict: {result.verdict} - "
                f"Confiance: {result.confidence_score*100:.1f}%"
            )
        
        except Exception as e:
            logger.error(f"❌ Erreur analyse: {str(e)}", exc_info=True)
            
            analysis.status = AnalysisStatus.FAILED.value
            analysis.completed_at = timezone.now()
            analysis.error_message = str(e)
            analysis.save()
    
    # ========================================
    # ANALYZE AUDIO
    # ========================================
    
    def analyze_audio(self, file_path):
        """Analyser un fichier audio"""
        
        logger.info(f"🎵 Analyse audio: {Path(file_path).name}")
        
        result = audio_detector.analyze_audio(file_path)
        
        return {
            'verdict': Verdict.FAKE.value if result['is_fake'] else Verdict.AUTHENTIC.value,
            'confidence_score': result['confidence'],
            'authenticity_score': 1 - result['score'],
            'deepfake_score': result['score'],
            'confidence_level': self.get_confidence_level(result['confidence']),
            'report': f"Audio analysé - {'Synthétique' if result['is_fake'] else 'Authentique'} ({result['percentage']})",
            'recommendations': self.get_recommendations(
                Verdict.FAKE if result['is_fake'] else Verdict.AUTHENTIC,
                result['confidence']
            ),
            'details': result.get('analysis', {})
        }
    
    # ========================================
    # 🖼️ ANALYZE IMAGE
    # ========================================
    
    def analyze_image(self, file_path):
        """Analyser une image"""
        
        logger.info(f"🖼️  Analyse image: {Path(file_path).name}")
        
        result = image_detector.analyze_image(file_path)
        
        return {
            'verdict': Verdict.FAKE.value if result['is_fake'] else Verdict.AUTHENTIC.value,
            'confidence_score': result['confidence'],
            'authenticity_score': 1 - result['score'],
            'deepfake_score': result['score'],
            'confidence_level': self.get_confidence_level(result['confidence']),
            'report': f"Image analysée - {'Manipulée' if result['is_fake'] else 'Authentique'} ({result['percentage']})",
            'recommendations': self.get_recommendations(
                Verdict.FAKE if result['is_fake'] else Verdict.AUTHENTIC,
                result['confidence']
            ),
            'details': result.get('details', {})
        }
    
    # ========================================
    # 🎬 ANALYZE VIDEO
    # ========================================
    
    def analyze_video(self, file_path):
        """Analyser une vidéo"""
        
        logger.info(f"🎬 Analyse vidéo: {Path(file_path).name}")
        
        result = video_detector.analyze_video(file_path)
        
        return {
            'verdict': Verdict.FAKE.value if result['is_fake'] else Verdict.AUTHENTIC.value,
            'confidence_score': result['confidence'],
            'authenticity_score': 1 - result['score'],
            'deepfake_score': result['score'],
            'confidence_level': self.get_confidence_level(result['confidence']),
            'report': f"Vidéo analysée ({result.get('frames_analyzed', 0)} frames) - {'Deepfake' if result['is_fake'] else 'Authentique'} ({result['percentage']})",
            'recommendations': self.get_recommendations(
                Verdict.FAKE if result['is_fake'] else Verdict.AUTHENTIC,
                result['confidence']
            ),
            'details': {
                'frames_analyzed': result.get('frames_analyzed', 0),
                'metadata': result.get('metadata', {})
            }
        }
    
    # ========================================
    # 📄 ANALYZE DOCUMENT
    # ========================================
    
    def analyze_document(self, file_path):
        """Analyser un document"""
        
        logger.info(f"📄 Analyse document: {Path(file_path).name}")
        
        result = document_detector.analyze_document(file_path)
        
        return {
            'verdict': Verdict.FAKE.value if result['is_fake'] else Verdict.AUTHENTIC.value,
            'confidence_score': result['confidence'],
            'authenticity_score': 1 - result['score'],
            'deepfake_score': result['score'],
            'confidence_level': self.get_confidence_level(result['confidence']),
            'report': f"Document analysé - {'Suspect' if result['is_fake'] else 'Authentique'} ({result['percentage']})",
            'recommendations': self.get_recommendations(
                Verdict.FAKE if result['is_fake'] else Verdict.AUTHENTIC,
                result['confidence']
            ),
            'details': result.get('details', {})
        }
    
    # ========================================
    # 📊 LIST ENDPOINT
    # ========================================
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/v1/analysis/
        
        Lister toutes les analyses de l'utilisateur.
        
        Query params:
        - status=COMPLETED
        - media__media_type=video
        - search=mon%20titre
        - ordering=-created_at
        """
        
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = AnalysisListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = AnalysisListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    # ========================================
    # 📖 RETRIEVE ENDPOINT
    # ========================================
    
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/v1/analysis/{id}/
        
        Afficher les détails d'une analyse.
        """
        
        instance = self.get_object()
        serializer = AnalysisSerializer(instance)
        return Response(serializer.data)
    
    # ========================================
    # 🎯 STATUS ENDPOINT
    # ========================================
    
    @action(detail=True, methods=['get'], url_path='status')
    def status(self, request, pk=None):
        """
        GET /api/v1/analysis/{id}/status/
        
        Obtenir le statut actuel d'une analyse.
        
        Utile pour le polling du frontend.
        """
        
        analysis = self.get_object()
        self.check_object_permission(request, analysis)
        
        response_data = {
            'id': analysis.id,
            'status': analysis.status,
            'message': self.get_status_message(analysis),
        }
        
        if analysis.is_completed and analysis.has_result:
            response_data['verdict'] = analysis.result.verdict
            response_data['confidence_score'] = analysis.result.confidence_score
            response_data['percentage'] = f"{analysis.result.confidence_score*100:.1f}%"
        
        return Response(response_data)
    
    # ========================================
    # 📊 RESULT ENDPOINT
    # ========================================
    
    @action(detail=True, methods=['get'], url_path='result')
    def result(self, request, pk=None):
        """
        GET /api/v1/analysis/{id}/result/
        
        Obtenir les résultats complets de l'analyse.
        """
        
        analysis = self.get_object()
        self.check_object_permission(request, analysis)
        
        if not analysis.is_completed:
            raise AnalysisNotCompletedError(
                detail=f"L'analyse n'est pas encore terminée (status: {analysis.status})"
            )
        
        if not analysis.has_result:
            raise AnalysisNotFoundError(
                detail="Aucun résultat trouvé pour cette analyse"
            )
        
        serializer = AnalysisResultSerializer(analysis.result)
        return Response(serializer.data)
    
    # ========================================
    # 🗑️ DELETE ENDPOINT
    # ========================================
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/v1/analysis/{id}/
        
        Supprimer une analyse (soft delete).
        """
        
        instance = self.get_object()
        self.check_object_permission(request, instance)
        
        instance.is_active = False
        instance.save()
        
        logger.info(f"🗑️  Analyse supprimée: {instance.id}")
        
        return Response(
            {'detail': 'Analyse supprimée'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    # ========================================
    # 🔧 HELPER METHODS
    # ========================================
    
    def get_status_message(self, analysis):
        """Obtenir un message lisible du statut"""
        messages = {
            AnalysisStatus.PENDING.value: "En attente de traitement",
            AnalysisStatus.PROCESSING.value: "Analyse en cours...",
            AnalysisStatus.COMPLETED.value: "Analyse terminée",
            AnalysisStatus.FAILED.value: "Erreur lors de l'analyse",
        }
        return messages.get(analysis.status, "Statut inconnu")
    
    def get_confidence_level(self, confidence):
        """Déterminer le niveau de confiance"""
        if confidence > 0.85:
            return ConfidenceLevel.HIGH.value
        elif confidence > 0.60:
            return ConfidenceLevel.MEDIUM.value
        else:
            return ConfidenceLevel.LOW.value
    
    def get_recommendations(self, verdict, confidence):
        """Obtenir des recommandations basées sur le verdict"""
        
        if confidence < 0.6:
            return "Confiance faible - Vérification manuelle recommandée"
        
        if verdict == Verdict.FAKE.value:
            return "Ce contenu est probablement manipulé. À ne pas partager ou utiliser comme preuve."
        else:
            return "Ce contenu semble authentique. Cependant, aucune analyse n'est 100% fiable."


# ========================================
# 📁 MEDIA VIEWSET
# ========================================

class MediaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les médias (lecture seule).
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = MediaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['media_type']
    search_fields = ['filename']
    
    def get_queryset(self):
        """Retourner seulement les médias de l'utilisateur"""
        user = self.request.user
        
        if user.is_staff:
            return Media.objects.all()
        
        return Media.objects.filter(user=user)