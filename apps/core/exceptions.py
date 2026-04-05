"""
apps/core/exceptions.py

Exceptions personnalisées pour toute l'application.
Permet de gérer les erreurs de manière uniforme et professionnelle.
"""

from rest_framework import status
from rest_framework.exceptions import APIException


#  EXCEPTIONS PERSONNALISÉES


class BaseAPIException(APIException):
    """
    Classe de base pour toutes les exceptions personnalisées.
    
    Hérite de rest_framework.exceptions.APIException
    pour que Django REST Framework les gère automatiquement.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Une erreur est survenue"
    default_code = "error"
    
    def __init__(self, detail=None, code=None):
        """
        Initialiser l'exception avec un message personnalisé.
        
        Args:
            detail (str): Message d'erreur personnalisé
            code (str): Code d'erreur (pour le frontend)
        """
        if detail is not None:
            self.detail = detail
        else:
            self.detail = self.default_detail
        
        if code is not None:
            self.code = code
        else:
            self.code = self.default_code



# EXCEPTIONS UTILISATEUR


class UserNotFoundError(BaseAPIException):
    """Levée quand un utilisateur n'existe pas"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "L'utilisateur n'existe pas"
    default_code = "user_not_found"


class UserAlreadyExistsError(BaseAPIException):
    """Levée quand on essaie de créer un utilisateur avec un email qui existe"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Cet email est déjà utilisé"
    default_code = "user_already_exists"


class InvalidCredentialsError(BaseAPIException):
    """Levée quand le login/password est incorrect"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Email ou mot de passe incorrect"
    default_code = "invalid_credentials"


class UserNotVerifiedError(BaseAPIException):
    """Levée quand un utilisateur n'a pas vérifié son email"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Votre email n'a pas été vérifié"
    default_code = "user_not_verified"



#  EXCEPTIONS AUTHENTIFICATION


class InvalidTokenError(BaseAPIException):
    """Levée quand le token JWT est invalide"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token invalide ou expiré"
    default_code = "invalid_token"


class TokenExpiredError(BaseAPIException):
    """Levée quand le token JWT a expiré"""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Token expiré, veuillez vous reconnecter"
    default_code = "token_expired"



#  EXCEPTIONS FICHIER


class InvalidFileError(BaseAPIException):
    """Levée quand le fichier n'est pas valide"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Type de fichier non autorisé"
    default_code = "invalid_file"


class FileTooLargeError(BaseAPIException):
    """Levée quand le fichier est trop volumineux"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Le fichier est trop volumineux (max 500MB)"
    default_code = "file_too_large"


class FileUploadError(BaseAPIException):
    """Levée quand le fichier n'a pas pu être uploadé"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Erreur lors de l'upload du fichier"
    default_code = "file_upload_error"


#  EXCEPTIONS ANALYSE


class AnalysisNotFoundError(BaseAPIException):
    """Levée quand une analyse n'existe pas"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "L'analyse n'existe pas"
    default_code = "analysis_not_found"


class AnalysisFailedError(BaseAPIException):
    """Levée quand l'analyse échoue"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "L'analyse a échoué, veuillez réessayer"
    default_code = "analysis_failed"


class AnalysisNotCompletedError(BaseAPIException):
    """Levée quand on essaie d'accéder les résultats avant que l'analyse soit terminée"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "L'analyse n'est pas encore terminée"
    default_code = "analysis_not_completed"



#  EXCEPTIONS IA/ML


class ModelNotFoundError(BaseAPIException):
    """Levée quand un modèle IA n'est pas trouvé"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Le modèle IA n'est pas disponible"
    default_code = "model_not_found"


class ModelLoadError(BaseAPIException):
    """Levée quand on ne peut pas charger un modèle IA"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Erreur lors du chargement du modèle IA"
    default_code = "model_load_error"



# EXCEPTIONS BASE DE DONNÉES


class DatabaseError(BaseAPIException):
    """Levée quand il y a une erreur de base de données"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = "Erreur de base de données"
    default_code = "database_error"



#  EXCEPTIONS VALIDATION


class ValidationError(BaseAPIException):
    """Levée quand les données ne sont pas valides"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Les données saisies ne sont pas valides"
    default_code = "validation_error"


class PermissionDeniedError(BaseAPIException):
    """Levée quand l'utilisateur n'a pas la permission"""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Vous n'avez pas la permission de faire cette action"
    default_code = "permission_denied"
