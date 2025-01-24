from django.utils import timezone
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Authenticate user
        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
            }
        }

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        # You can add custom validation here if needed
        if not value:
            raise serializers.ValidationError("Refresh token is required.")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'full_name', 'password']

    def validate_email(self, value):
        """
        Validate if the email already exists in the system.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'table_number', 'capacity', 'availability_status']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = [ 'date', 'time' ]
        read_only_fields = ['id', 'user', 'table','status']
        

    def create(self, validated_data):
        # Logic to handle reservation creation
        if validated_data['date'] < timezone.now().date():
            raise serializers.ValidationError("Reservation date cannot be in the past.")
        reservation = Reservation.objects.create(**validated_data)
        return reservation


class WaitlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlist
        fields = ['id', 'user','table','date', 'status' ]

    def create(self, validated_data):
        # Handle waitlist addition if no table is available
        waitlist = Waitlist.objects.create(**validated_data)
        return waitlist
