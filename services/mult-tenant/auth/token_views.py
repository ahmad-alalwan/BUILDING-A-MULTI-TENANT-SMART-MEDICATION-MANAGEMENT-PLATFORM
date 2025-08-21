from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from django.db import transaction
from .models import Account, AccessToken, Tenant
from .token_serializers import (
    TokenLoginSerializer, TokenResponseSerializer, RefreshTokenSerializer,
    LogoutSerializer, AccountSerializer, UserAccountSerializer,
    AccountBalanceSerializer, AccountVerificationSerializer,
    AccountTransactionSerializer, AccountStatementSerializer
)
from .token_services import TokenAuthService
from .services import AuthService
from functools import wraps
import json

def token_required(view_func):
    """Decorator to check if valid token is provided"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Authorization header with Bearer token required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = auth_header.split(' ')[1]
        tenant = getattr(request, 'tenant', None)
        user = TokenAuthService.validate_token(token, tenant)
        
        if not user:
            return Response(
                {'error': 'Invalid or expired token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        request.user = user
        request.token = token
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_token_required(view_func):
    """Decorator to check if user has admin role with valid token"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Get token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Authorization header with Bearer token required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = auth_header.split(' ')[1]
        tenant = getattr(request, 'tenant', None)
        user = TokenAuthService.validate_token(token, tenant)
        
        if not user:
            return Response(
                {'error': 'Invalid or expired token'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not hasattr(user, 'profile') or not user.profile.is_admin:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        request.user = user
        request.token = token
        return view_func(request, *args, **kwargs)
    return wrapper

class TokenLoginView(APIView):
    """Token-based login endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = TokenLoginSerializer(data=request.data)
        if serializer.is_valid():
            # Get IP address and user agent
            ip_address = self.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Get tenant from request
            tenant = getattr(request, 'tenant', None)
            if not tenant:
                return Response({
                    'error': 'Tenant not found'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Login with token
            result = TokenAuthService.login_with_token(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password'],
                tenant=tenant,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            if result['success']:
                return Response({
                    'message': 'Login successful',
                    'data': result['token']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class TokenLogoutView(APIView):
    """Token-based logout endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            tenant = getattr(request, 'tenant', None)
            result = TokenAuthService.logout_with_token(
                serializer.validated_data['token'],
                tenant
            )
            
            if result['success']:
                return Response({
                    'message': result['message']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TokenRefreshView(APIView):
    """Token refresh endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            tenant = getattr(request, 'tenant', None)
            result = TokenAuthService.refresh_token(
                serializer.validated_data['token'],
                tenant
            )
            
            if result['success']:
                return Response({
                    'message': 'Token refreshed successfully',
                    'data': result['token']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """Get current user profile with token authentication"""
    permission_classes = [permissions.AllowAny]
    
    @token_required
    def get(self, request):
        tenant = getattr(request, 'tenant', None)
        user_data = TokenAuthService.get_user_from_token(request.token, tenant)
        if user_data:
            return Response(user_data, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class AccountDetailView(APIView):
    """Get account details"""
    permission_classes = [permissions.AllowAny]
    
    @token_required
    def get(self, request):
        if hasattr(request.user, 'account'):
            serializer = AccountSerializer(request.user.account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Account not found'}, status=status.HTTP_404_NOT_FOUND)

class AccountBalanceView(APIView):
    """Update account balance (admin only)"""
    permission_classes = [permissions.AllowAny]
    
    @admin_token_required
    def post(self, request):
        serializer = AccountBalanceSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    account = request.user.account
                    amount = serializer.validated_data['amount']
                    operation = serializer.validated_data['operation']
                    
                    if operation == 'add':
                        account.balance += amount
                    elif operation == 'subtract':
                        if account.balance >= amount:
                            account.balance -= amount
                        else:
                            return Response({
                                'error': 'Insufficient balance'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    account.save()
                    
                    return Response({
                        'message': f'Balance {operation}ed successfully',
                        'new_balance': float(account.balance)
                    }, status=status.HTTP_200_OK)
                    
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountVerificationView(APIView):
    """Verify account"""
    permission_classes = [permissions.AllowAny]
    
    @token_required
    def post(self, request):
        serializer = AccountVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                account = request.user.account
                verification_token = serializer.validated_data['verification_token']
                
                if account.verification_token == verification_token:
                    account.is_verified = True
                    account.verification_token = ''
                    account.save()
                    
                    return Response({
                        'message': 'Account verified successfully'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'Invalid verification token'
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AccountTransactionView(APIView):
    """Handle account transactions"""
    permission_classes = [permissions.AllowAny]
    
    @token_required
    def post(self, request):
        serializer = AccountTransactionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    account = request.user.account
                    amount = serializer.validated_data['amount']
                    description = serializer.validated_data['description']
                    transaction_type = serializer.validated_data['transaction_type']
                    
                    if transaction_type == 'withdrawal':
                        if account.balance >= amount:
                            account.balance -= amount
                        else:
                            return Response({
                                'error': 'Insufficient balance'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    elif transaction_type == 'deposit':
                        account.balance += amount
                    elif transaction_type == 'transfer':
                        recipient_account = serializer.validated_data.get('recipient_account')
                        if not recipient_account:
                            return Response({
                                'error': 'Recipient account required for transfer'
                            }, status=status.HTTP_400_BAD_REQUEST)
                        
                        try:
                            recipient = Account.objects.get(account_number=recipient_account)
                            if account.balance >= amount:
                                account.balance -= amount
                                recipient.balance += amount
                                recipient.save()
                            else:
                                return Response({
                                    'error': 'Insufficient balance'
                                }, status=status.HTTP_400_BAD_REQUEST)
                        except Account.DoesNotExist:
                            return Response({
                                'error': 'Recipient account not found'
                            }, status=status.HTTP_404_NOT_FOUND)
                    
                    account.save()
                    
                    return Response({
                        'message': f'{transaction_type.capitalize()} successful',
                        'new_balance': float(account.balance),
                        'transaction': {
                            'amount': float(amount),
                            'description': description,
                            'type': transaction_type
                        }
                    }, status=status.HTTP_200_OK)
                    
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminAccountListView(APIView):
    """List all accounts (admin only)"""
    permission_classes = [permissions.AllowAny]
    
    @admin_token_required
    def get(self, request):
        accounts = Account.objects.all()
        serializer = AccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@token_required
def logout_with_header(request):
    """Logout using token from Authorization header"""
    tenant = getattr(request, 'tenant', None)
    result = TokenAuthService.logout_with_token(request.token, tenant)
    
    if result['success']:
        return Response({
            'message': result['message']
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': result['error']
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@token_required
def get_user_info(request):
    """Get user information from token"""
    tenant = getattr(request, 'tenant', None)
    user_data = TokenAuthService.get_user_from_token(request.token, tenant)
    if user_data:
        return Response(user_data, status=status.HTTP_200_OK)
    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
