"""
apps/core/validators.py

Validateurs personnalisés pour la sérialisation et les modèles.
"""

import os
import re
import mimetypes
from rest_framework import serializers
from apps.core.constants import FileLimits, MediaType
from apps.core.exceptions import InvalidFileError, FileTooLargeError


def _media_type_values():
    # Compatible selon implémentation de MediaType
    if hasattr(MediaType, "values"):
        vals = MediaType.values
        return vals() if callable(vals) else list(vals)
    return ["image", "video", "audio"]


def _infer_media_type(file):
    mime_type, _ = mimetypes.guess_type(file.name)
    if not mime_type:
        return None
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("video/"):
        return "video"
    if mime_type.startswith("audio/"):
        return "audio"
    return None


def validate_file_size(file, max_size):
    if file.size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise FileTooLargeError(f"Le fichier dépasse {max_size_mb:.0f} MB")


def validate_file_format(file, allowed_formats):
    filename = file.name
    ext = os.path.splitext(filename)[1][1:].lower()
    if ext not in allowed_formats:
        raise InvalidFileError(
            f"Format non autorisé: {ext}. "
            f"Formats autorisés: {', '.join(allowed_formats)}"
        )


def validate_media_file(file, media_type=None):
    """
    Validation complète d'un fichier média.
    media_type peut être fourni; sinon il est déduit du nom MIME.
    """
    if file is None:
        raise InvalidFileError("Aucun fichier fourni.")

    media_type = media_type or _infer_media_type(file)
    if media_type not in _media_type_values():
        raise InvalidFileError(f"Type de média invalide: {media_type}")

    max_size = FileLimits.get_max_size(media_type)
    allowed_formats = FileLimits.get_allowed_formats(media_type)

    validate_file_size(file, max_size)
    validate_file_format(file, allowed_formats)


def validate_email_format(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise serializers.ValidationError("L'adresse email n'est pas valide")


def validate_password_strength(password):
    if len(password) < 8:
        raise serializers.ValidationError("Le mot de passe doit contenir au moins 8 caractères")
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError("Le mot de passe doit contenir au moins une majuscule")
    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError("Le mot de passe doit contenir au moins une minuscule")
    if not re.search(r"[0-9]", password):
        raise serializers.ValidationError("Le mot de passe doit contenir au moins un chiffre")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
        raise serializers.ValidationError("Le mot de passe doit contenir au moins un caractère spécial")


def validate_url(url):
    pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    if not re.match(pattern, url):
        raise serializers.ValidationError("L'URL n'est pas valide")
