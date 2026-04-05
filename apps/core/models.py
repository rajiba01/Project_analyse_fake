"""
apps/core/models.py

Ce fichier contient les modèles de base hérités par tous les autres modèles.
Permet de réutiliser les mêmes champs (created_at, updated_at, is_active) partout.
"""

from django.db import models
from django.utils import timezone


#  BASE MODEL - Classe de base pour tous les modèles


class BaseModel(models.Model):
    """
    Modèle abstrait de base avec champs communs.
    
    ABSTRAIT = ne crée pas de table dans la base de données
    Les autres modèles HÉRITENT de cette classe et créent leurs propres tables.
    
    Champs communs:
    - created_at: quand l'objet a été créé
    - updated_at: quand l'objet a été modifié
    - is_active: si l'objet est actif ou supprimé (soft delete)
    """
    
  
    #  TIMESTAMPS
  
    created_at = models.DateTimeField(
        auto_now_add=True,  # Défini automatiquement à la création
        help_text="Date et heure de création"
    )
    """
    Explication:
    - DateTimeField = stocke la date ET l'heure
    - auto_now_add=True = Django défini automatiquement la valeur à la création
    - Impossible de modifier manually après la création
    - Exemple: 2024-04-04 14:30:45.123456+00:00
    """
    
    updated_at = models.DateTimeField(
        auto_now=True,  # Défini automatiquement à chaque modification
        help_text="Date et heure de dernière modification"
    )
    """
    Explication:
    - auto_now=True = Django défini automatiquement la valeur à chaque save()
    - Mis à jour automatiquement quand on modifie l'objet
    - Exemple: Si on change le nom d'un utilisateur, updated_at change
    """
    
   
    #  SOFT DELETE
 
    is_active = models.BooleanField(
        default=True,
        help_text="Indique si l'objet est actif (soft delete)"
    )
    """
    Explication:
    - BooleanField = champ booléen (True ou False)
    - default=True = par défaut, tous les objets sont actifs
    - Au lieu de SUPPRIMER l'objet, on met is_active=False
    - Avantage: L'historique est conservé dans la base de données
    - Exemple: Un utilisateur supprime son compte → is_active=False
    """
    
 
    #  MANAGER PERSONNALISÉ
   
    objects = models.Manager()  # Manager par défaut (tous les objets)
    
    class Meta:
        abstract = True 
        """
        Explication:
        - abstract = True → Cette classe est juste un TEMPLATE
        - Quand on hérite de BaseModel, ON CRÉE une nouvelle table
        
        """
        
        ordering = ['-created_at']  # Trier par created_at décroissant (plus récent d'abord)
    
    def __str__(self):
        """Représentation en texte de l'objet"""
        return f"{self.__class__.__name__} - {self.id}"
    
    # ========================================
    # 💾 MÉTHODES UTILES
    # ========================================
    
    def save(self, *args, **kwargs):
        """
        Sauvegarde l'objet dans la base de données.
        
        Cette méthode est appelée automatiquement quand on fait:
         obj.save()
        """
        # Appeler la méthode save() du parent
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Supprime l'objet (soft delete).
        
        Au lieu de supprimer vraiment, on met is_active=False
        """
        self.is_active = False
        self.save()
        # Ne pas supprimer vraiment, juste désactiver
    
    def hard_delete(self, *args, **kwargs):
        """
        Suppression DÉFINITIVE (ne pas utiliser normalement!).
        
        Cette méthode supprime VRAIMENT l'objet de la base de données.
        Danger: Impossible de récupérer les données!
        """
        super().delete(*args, **kwargs)



#  TIMESTAMPS MIXIN (Optional)


class TimestampMixin(models.Model):
    """
    Mixin qui ajoute juste created_at et updated_at.
    Utile si vous ne voulez pas is_active
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True




class SearchableMixin(models.Model):
    """
    Mixin pour les modèles qui doivent être searchables.
    """
    search_vector = models.CharField(
        max_length=500,
        blank=True,
        help_text="Champ utilisé pour la recherche full-text"
    )
    
    class Meta:
        abstract = True
