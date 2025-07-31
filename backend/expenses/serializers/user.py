# User serializer for handling user-related data
from rest_framework import serializers
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']
        extra_kwargs = {
            'username': {'required': True, 'max_length': 150},
            'email': {'required': True, 'max_length': 254},
            'first_name': {'required': False, 'max_length': 30},
            'last_name': {'required': False, 'max_length': 150}
        }
    def create(self, validated_data):
        """
        Create a new user instance with the provided validated data.
        """
        user = User.objects.create_user(**validated_data)
        return user
    def update(self, instance, validated_data):
        """
        Update the user instance with the provided validated data.
        """
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance
     