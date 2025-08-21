from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Role

class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model"""
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'role', 'role_id', 'phone_number', 'address', 
            'bio', 'profile_picture', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'date_joined']

class RegisterUserSerializer(serializers.Serializer):
    """Serializer for user registration"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    role_name = serializers.ChoiceField(
        choices=[('user', 'User'), ('expert', 'Expert'), ('admin', 'Admin')],
        default='user'
    )
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """Validate registration data"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already exists")
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        return attrs

class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to authenticate with username
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            
            # If not found, try with email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user and user.is_active:
                attrs['user'] = user
                return attrs
            else:
                raise serializers.ValidationError("Invalid credentials or inactive account")
        else:
            raise serializers.ValidationError("Must include username and password")

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate password change data"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs

class UpdateProfileSerializer(serializers.Serializer):
    """Serializer for updating user profile"""
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_picture = serializers.ImageField(required=False)

class ChangeRoleSerializer(serializers.Serializer):
    """Serializer for changing user role (admin only)"""
    user_id = serializers.IntegerField()
    new_role = serializers.ChoiceField(
        choices=[('user', 'User'), ('expert', 'Expert'), ('admin', 'Admin')]
    )
