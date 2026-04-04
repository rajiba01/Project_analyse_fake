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