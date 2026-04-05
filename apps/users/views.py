from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def list_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response({"status": "success", "data": serializer.data})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "Utilisateur non trouvé"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserSerializer(user)
    return Response({"status": "success", "data": serializer.data})


@api_view(["PATCH"])
@permission_classes([permissions.IsAuthenticated])
def update_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "Utilisateur non trouvé"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            "status": "success",
            "message": "Utilisateur mis à jour",
            "data": serializer.data
        })

    return Response({
        "status": "error",
        "errors": serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([permissions.IsAuthenticated])
def delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(
            {"status": "error", "message": "Utilisateur non trouvé"},
            status=status.HTTP_404_NOT_FOUND
        )

    user.delete()
    return Response({
        "status": "success",
        "message": "Utilisateur supprimé"
    }, status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_user(request):
    """
    Création sécurisée (spécial Hackathon)
    """
    email = request.data.get("email")
    password = request.data.get("password")
    # Changement ici : utilisation de tes noms de champs exacts
    first_name = request.data.get("firstName", "Utilisateur")
    last_name = request.data.get("lastName", "Démo")

    if not email or not password:
        return Response({
            "status": "error",
            "message": "L'email et le mot de passe sont obligatoires."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier si l'email existe (hors comptes vides buggués)
    if User.objects.filter(email=email).exists():
        return Response({
            "status": "error",
            "message": "Cet utilisateur existe déjà."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Passage des arguments exacts demandés par ton UserManager
        user = User.objects.create_user(
            email=email,
            password=password,
            firstName=first_name,
            lastName=last_name
        )
        
        # Forcer l'activation
        user.is_active = True
        user.save()

        return Response({
            "status": "success",
            "message": "Utilisateur créé et activé avec succès",
            "data": {"id": user.id, "email": user.email}
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "status": "error",
            "errors": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
