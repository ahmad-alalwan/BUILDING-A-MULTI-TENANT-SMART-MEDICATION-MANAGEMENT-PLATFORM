from django.shortcuts import render
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .models import UserProfile, Role
from .serializers import (
    UserSerializer, RegisterUserSerializer, LoginSerializer,
    ChangePasswordSerializer, UpdateProfileSerializer, ChangeRoleSerializer,
    UserProfileSerializer
)
from .services import AuthService
from functools import wraps

def admin_required(view_func):
    """Decorator to check if user has admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            return Response(
                {'error': 'Admin access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper

def expert_required(view_func):
    """Decorator to check if user has expert role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not hasattr(request.user, 'profile') or not request.user.profile.is_expert:
            return Response(
                {'error': 'Expert access required'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper

class RegisterView(APIView):
    """User registration endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            # Extract profile data
            profile_data = {}
            for field in ['phone_number', 'address', 'bio']:
                if field in serializer.validated_data:
                    profile_data[field] = serializer.validated_data[field]
            
            # Register user using service
            result = AuthService.register_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                first_name=serializer.validated_data.get('first_name', ''),
                last_name=serializer.validated_data.get('last_name', ''),
                role_name=serializer.validated_data.get('role_name', 'user'),
                **profile_data
            )
            
            if result['success']:
                return Response({
                    'message': 'User registered successfully',
                    'user': result['user']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.profile.role.name if user.profile.role else 'user',
                    'is_admin': user.profile.is_admin,
                    'is_expert': user.profile.is_expert
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    """Get and update user profile"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user profile"""
        user_data = AuthService.get_user_by_id(request.user.id)
        if user_data:
            return Response(user_data, status=status.HTTP_200_OK)
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        """Update current user profile"""
        serializer = UpdateProfileSerializer(data=request.data)
        if serializer.is_valid():
            result = AuthService.update_user_profile(
                request.user.id,
                **serializer.validated_data
            )
            
            if result['success']:
                return Response({
                    'message': 'Profile updated successfully',
                    'user': result['user']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """Change user password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({
                    'error': 'Current password is incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminUserListView(APIView):
    """List all users (admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    
    @admin_required
    def get(self, request):
        users = User.objects.all()
        user_data = []
        
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.profile.role.name if user.profile.role else 'user',
                'is_active': user.profile.is_active,
                'date_joined': user.date_joined
            })
        
        return Response(user_data, status=status.HTTP_200_OK)

class AdminChangeRoleView(APIView):
    """Change user role (admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    
    @admin_required
    def post(self, request):
        serializer = ChangeRoleSerializer(data=request.data)
        if serializer.is_valid():
            result = AuthService.change_user_role(
                serializer.validated_data['user_id'],
                serializer.validated_data['new_role']
            )
            
            if result['success']:
                return Response({
                    'message': 'User role changed successfully',
                    'user': result['user']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminDeactivateUserView(APIView):
    """Deactivate user (admin only)"""
    permission_classes = [permissions.IsAuthenticated]
    
    @admin_required
    def post(self, request, user_id):
        result = AuthService.deactivate_user(user_id)
        
        if result['success']:
            return Response({
                'message': result['message']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['error']
            }, status=status.HTTP_400_BAD_REQUEST)

class ExpertUserListView(APIView):
    """List users (expert only - limited view)"""
    permission_classes = [permissions.IsAuthenticated]
    
    @expert_required
    def get(self, request):
        # Experts can only see basic user info, not admin details
        users = User.objects.filter(profile__is_active=True)
        user_data = []
        
        for user in users:
            user_data.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.profile.role.name if user.profile.role else 'user',
                'date_joined': user.date_joined
            })
        
        return Response(user_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_by_id(request, user_id):
    """Get user by ID (admin/expert only)"""
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Check if user has permission
    if not (request.user.profile.is_admin or request.user.profile.is_expert):
        return Response(
            {'error': 'Insufficient permissions'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    user_data = AuthService.get_user_by_id(user_id)
    if user_data:
        # If expert, limit the data returned
        if request.user.profile.is_expert and not request.user.profile.is_admin:
            limited_data = {
                'id': user_data['id'],
                'username': user_data['username'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'date_joined': user_data['created_at']
            }
            return Response(limited_data, status=status.HTTP_200_OK)
        
        return Response(user_data, status=status.HTTP_200_OK)
    
    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
