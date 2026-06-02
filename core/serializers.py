from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Product

class UserSerializer(serializers.ModelSerializer):
    is_vendor = serializers.BooleanField(write_only=True, default=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_vendor']
    def create(self, validated_data):
        is_vendor = validated_data.pop('is_vendor', False)
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, is_vendor=is_vendor)
        return user

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['vendor']
