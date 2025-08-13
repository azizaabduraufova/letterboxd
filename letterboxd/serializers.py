from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from letterboxd.models import Genre, Movie, User, Profile


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class UserProfileSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True, validators=[
        UniqueValidator(queryset=User.objects.all(), message='Username already exists')])
    first_name = serializers.CharField(max_length=50, allow_blank=True, required=False)
    last_name = serializers.CharField(max_length=50, allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=True, validators=[
        UniqueValidator(queryset=User.objects.all(), message='Email already exists')])
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    img = serializers.ImageField(allow_empty_file=True, allow_null=True, required=False)

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        img = validated_data.pop('img', None)
        validated_data.pop('password_confirm')
        with transaction.atomic():
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            Profile.objects.create(user=user, img=img)
        return user


    def to_representation(self, instance):
        request = self.context.get('request')
        profile = getattr(instance, 'profile', None)
        if profile is None:
            profile = Profile.objects.create(user=instance)
        return {
            "id": instance.id,
            "username": instance.username,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "email": instance.email,
            "img": request.build_absolute_uri(
                instance.profile.img.url) if request and instance.profile and instance.profile.img else None
        }
