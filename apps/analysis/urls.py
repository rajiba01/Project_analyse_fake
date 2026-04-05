"""
apps/analysis/urls.py

Routes pour l'analyse.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalysisViewSet, MediaViewSet

# Créer un router pour les ViewSets
router = DefaultRouter()
# Ajoute un "s" ici pour mettre les mots au pluriel
router.register(r'analyses', AnalysisViewSet, basename='analysis')
router.register(r'medias', MediaViewSet, basename='media')

app_name = 'analysis'

urlpatterns = [
    path('', include(router.urls)),
]
