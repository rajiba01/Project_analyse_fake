from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "firstName", "lastName", "email", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            firstName=validated_data["firstName"],
            lastName=validated_data["lastName"],
            password=validated_data["password"]
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Email ou mot de passe invalide")

        if not user.is_active:
            raise serializers.ValidationError("Ce compte est désactivé")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "firstName", "lastName", "email"]