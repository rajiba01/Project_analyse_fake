"""
apps/core/constants.py

Constantes et énumérations utilisées partout dans l'application.
Permet d'éviter les typos et facilite la maintenance.
"""

from enum import Enum
from django.db import models
# ========================================
# 📁 MEDIA TYPES - Types de fichiers
# ========================================

class MediaType(str, Enum):
    """
    Énumération des types de médias autorisés.
    
    Explication:
    - str, Enum = crée une énumération avec des valeurs string
    - Permet d'utiliser: MediaType.IMAGE.value → "image"
    """
    
    IMAGE = "image"
    """Images: JPEG, PNG, etc."""
    
    VIDEO = "video"
    """Vidéos: MP4, AVI, etc."""
    
    AUDIO = "audio"
    """Audio: MP3, WAV, etc."""
    
    @classmethod
    def choices(cls):
        """Retourne les choix pour un ChoiceField Django"""
        return [(member.value, member.name) for member in cls]
    
    @classmethod
    def values(cls):
        """Retourne toutes les valeurs possibles"""
        return [member.value for member in cls]


# ========================================
# 🔄 ANALYSIS STATUS - État de l'analyse
# ========================================

class AnalysisStatus(str, Enum):
    """
    État possible d'une analyse.
    
    Workflow:
    PENDING → PROCESSING → COMPLETED
                    ↓
                 FAILED
    """
    
    PENDING = "PENDING"
    """En attente (vient d'être créée, pas encore lancée)"""
    
    PROCESSING = "PROCESSING"
    """En cours de traitement (le modèle IA tourne)"""
    
    COMPLETED = "COMPLETED"
    """Terminée avec succès"""
    
    FAILED = "FAILED"
    """Terminée avec erreur"""
    
    @classmethod
    def choices(cls):
        """Retourne les choix pour un ChoiceField Django"""
        return [(member.value, member.name) for member in cls]


# ========================================
# 🎯 VERDICT - Résultat de l'analyse
# ========================================

class Verdict(str, Enum):
    """
    Résultat final de l'analyse.
    
    Signification:
    - AUTHENTIC: Le média semble authentique
    - FAKE: Le média est clairement un deepfake
    - SUSPICIOUS: Il y a des signes suspects, à vérifier manuellement
    """
    
    AUTHENTIC = "AUTHENTIC"
    """Le média semble authentique"""
    
    FAKE = "FAKE"
    """Le média est un deepfake"""
    
    SUSPICIOUS = "SUSPICIOUS"
    """Le média est suspect (vérification manuelle recommandée)"""
    
    @classmethod
    def choices(cls):
        """Retourne les choix pour un ChoiceField Django"""
        return [(member.value, member.name) for member in cls]
    
    @classmethod
    def get_color(cls, verdict):
        """Retourne la couleur associée au verdict (pour le frontend)"""
        colors = {
            cls.AUTHENTIC.value: "green",
            cls.FAKE.value: "red",
            cls.SUSPICIOUS.value: "orange",
        }
        return colors.get(verdict, "gray")


# ========================================
# 👤 USER ROLES - Rôles utilisateur
# ========================================

class UserRole(str, Enum):
    """
    Rôles possibles pour un utilisateur.
    
    Utilisé pour les permissions:
    - ADMIN: Accès total
    - MODERATOR: Modère les contenus
    - USER: Utilisateur normal
    """
    
    ADMIN = "admin"
    """Administrateur: accès total"""
    
    MODERATOR = "moderator"
    """Modérateur: peut vérifier et approuver les résultats"""
    
    USER = "user"
    """Utilisateur normal: peut seulement utiliser la plateforme"""
    
    @classmethod
    def choices(cls):
        """Retourne les choix pour un ChoiceField Django"""
        return [(member.value, member.name) for member in cls]


# ========================================
# 📐 FILE LIMITS - Limites de fichiers
# ========================================

class FileLimits:
    """
    Limites de taille et d'upload pour les fichiers.
    
    Exemple:
    - MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB
    """
    
    # 🖼️ Images
    MAX_IMAGE_SIZE = 50 * 1024 * 1024  # 50 MB
    ALLOWED_IMAGE_FORMATS = ['jpeg', 'jpg', 'png', 'webp', 'bmp']
    
    # 🎬 Vidéos
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500 MB
    ALLOWED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'webm']
    
    # 🔊 Audio
    MAX_AUDIO_SIZE = 100 * 1024 * 1024  # 100 MB
    ALLOWED_AUDIO_FORMATS = ['mp3', 'wav', 'flac', 'aac', 'ogg']
    
    @classmethod
    def get_max_size(cls, media_type):
        """Retourne la taille max pour un type de média"""
        sizes = {
            MediaType.IMAGE.value: cls.MAX_IMAGE_SIZE,
            MediaType.VIDEO.value: cls.MAX_VIDEO_SIZE,
            MediaType.AUDIO.value: cls.MAX_AUDIO_SIZE,
        }
        return sizes.get(media_type)
    
    @classmethod
    def get_allowed_formats(cls, media_type):
        """Retourne les formats autorisés pour un type de média"""
        formats = {
            MediaType.IMAGE.value: cls.ALLOWED_IMAGE_FORMATS,
            MediaType.VIDEO.value: cls.ALLOWED_VIDEO_FORMATS,
            MediaType.AUDIO.value: cls.ALLOWED_AUDIO_FORMATS,
        }
        return formats.get(media_type, [])


# ========================================
# 🔢 API CONSTANTS - Constantes API
# ========================================

class APIConstants:
    """Constantes pour l'API"""
    
    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Token expiration (en minutes)
    ACCESS_TOKEN_LIFETIME = 15  # 15 minutes
    REFRESH_TOKEN_LIFETIME = 1440  # 24 heures
    
    # Rate limiting
    MAX_REQUESTS_PER_HOUR = 100
    MAX_ANALYSIS_PER_DAY = 50


# ========================================
# 📧 EMAIL TEMPLATES
# ========================================

class EmailTemplates(str, Enum):
    """Types d'emails envoyés"""
    
    WELCOME = "welcome"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    ANALYSIS_COMPLETE = "analysis_complete"
    ANALYSIS_FAILED = "analysis_failed"


# ========================================
# 🎨 CONFIDENCE LEVELS - Niveaux de confiance
# ========================================

class ConfidenceLevel(models.TextChoices):
    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"
    
    @classmethod
    def from_score(cls, score):
        """Convertir un score (0-1) en niveau de confiance"""
        if score < 0.3:
            return cls.LOW
        elif score < 0.7:
            return cls.MEDIUM
        else:
            return cls.HIGH
