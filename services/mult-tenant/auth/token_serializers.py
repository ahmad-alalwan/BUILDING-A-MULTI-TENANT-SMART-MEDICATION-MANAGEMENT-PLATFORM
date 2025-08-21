from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account, AccessToken, UserProfile, Role

class AccountSerializer(serializers.ModelSerializer):
    """Serializer for Account model"""
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Account
        fields = [
            'id', 'user', 'account_number', 'balance', 'is_verified',
            'last_login_ip', 'last_login_time', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'account_number', 'created_at', 'updated_at']

class TokenLoginSerializer(serializers.Serializer):
    """Serializer for token-based login"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
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

class TokenResponseSerializer(serializers.Serializer):
    """Serializer for token response"""
    access_token = serializers.CharField()
    expires_at = serializers.DateTimeField()
    user = serializers.DictField()

class RefreshTokenSerializer(serializers.Serializer):
    """Serializer for token refresh"""
    token = serializers.CharField()

class LogoutSerializer(serializers.Serializer):
    """Serializer for logout"""
    token = serializers.CharField()

class AccountBalanceSerializer(serializers.Serializer):
    """Serializer for account balance update"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    operation = serializers.ChoiceField(choices=['add', 'subtract'])

class AccountVerificationSerializer(serializers.Serializer):
    """Serializer for account verification"""
    verification_token = serializers.CharField()

class UserAccountSerializer(serializers.ModelSerializer):
    """Serializer for user with account information"""
    account = AccountSerializer(read_only=True)
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'date_joined', 'account', 'profile'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_profile(self, obj):
        """Get profile information"""
        if hasattr(obj, 'profile'):
            return {
                'role': obj.profile.role.name if obj.profile.role else 'user',
                'phone_number': obj.profile.phone_number,
                'address': obj.profile.address,
                'bio': obj.profile.bio,
                'is_admin': obj.profile.is_admin,
                'is_expert': obj.profile.is_expert
            }
        return None

class TokenInfoSerializer(serializers.ModelSerializer):
    """Serializer for token information"""
    user = serializers.StringRelatedField()
    
    class Meta:
        model = AccessToken
        fields = [
            'id', 'user', 'token', 'is_active', 'created_at',
            'expires_at', 'ip_address', 'user_agent'
        ]
        read_only_fields = ['id', 'token', 'created_at', 'expires_at']

class AccountTransactionSerializer(serializers.Serializer):
    """Serializer for account transactions"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField(max_length=255)
    transaction_type = serializers.ChoiceField(
        choices=['deposit', 'withdrawal', 'transfer', 'payment']
    )
    recipient_account = serializers.CharField(max_length=20, required=False)

class AccountStatementSerializer(serializers.Serializer):
    """Serializer for account statement request"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    transaction_type = serializers.ChoiceField(
        choices=['all', 'deposit', 'withdrawal', 'transfer', 'payment'],
        default='all'
    )
