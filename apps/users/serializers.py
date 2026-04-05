from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firstName", "lastName", "email"]
        read_only_fields = ["id", "email"]
