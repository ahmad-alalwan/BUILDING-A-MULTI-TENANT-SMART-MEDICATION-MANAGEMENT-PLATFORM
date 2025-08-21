from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from .models import UserProfile, Role
from typing import Optional, Dict, Any

class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        role_name: str = "user",
        **extra_fields
    ) -> Dict[str, Any]:
        """
        Register a new user with specified role
        
        Args:
            username: Username for the new user
            email: Email address
            password: User password
            first_name: First name (optional)
            last_name: Last name (optional)
            role_name: Role name (admin, expert, user)
            **extra_fields: Additional profile fields
            
        Returns:
            Dict containing success status and user data or error message
        """
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }
                
                if User.objects.filter(email=email).exists():
                    return {
                        'success': False,
                        'error': 'Email already exists'
                    }
                
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )
                
                # Get or create role
                role, created = Role.objects.get_or_create(name=role_name)
                
                # Update profile with role and extra fields
                profile = user.profile
                profile.role = role
                
                # Set extra fields if provided
                for field, value in extra_fields.items():
                    if hasattr(profile, field):
                        setattr(profile, field, value)
                
                profile.save()
                
                return {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': role.name,
                        'profile_id': profile.id
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def login_user(username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate and login user
        
        Args:
            username: Username or email
            password: User password
            
        Returns:
            Dict containing success status and user data or error message
        """
        try:
            # Try to authenticate with username
            user = authenticate(username=username, password=password)
            
            # If not found, try with email
            if user is None:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user is not None and user.is_active:
                return {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.profile.role.name if user.profile.role else 'user',
                        'is_admin': user.profile.is_admin,
                        'is_expert': user.profile.is_expert
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid credentials or inactive account'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def change_user_role(user_id: int, new_role_name: str) -> Dict[str, Any]:
        """
        Change user role (admin only)
        
        Args:
            user_id: ID of the user to change role
            new_role_name: New role name (admin, expert, user)
            
        Returns:
            Dict containing success status and updated user data or error message
        """
        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                role, created = Role.objects.get_or_create(name=new_role_name)
                
                user.profile.role = role
                user.profile.save()
                
                return {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': role.name
                    }
                }
                
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user information by ID
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing user data or None if not found
        """
        try:
            user = User.objects.get(id=user_id)
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.profile.role.name if user.profile.role else 'user',
                'is_admin': user.profile.is_admin,
                'is_expert': user.profile.is_expert,
                'phone_number': user.profile.phone_number,
                'address': user.profile.address,
                'bio': user.profile.bio,
                'is_active': user.profile.is_active,
                'created_at': user.profile.created_at
            }
        except User.DoesNotExist:
            return None
    
    @staticmethod
    def update_user_profile(user_id: int, **profile_data) -> Dict[str, Any]:
        """
        Update user profile information
        
        Args:
            user_id: User ID
            **profile_data: Profile fields to update
            
        Returns:
            Dict containing success status and updated user data or error message
        """
        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                profile = user.profile
                
                # Update profile fields
                for field, value in profile_data.items():
                    if hasattr(profile, field):
                        setattr(profile, field, value)
                
                profile.save()
                
                return {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': profile.role.name if profile.role else 'user'
                    }
                }
                
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def deactivate_user(user_id: int) -> Dict[str, Any]:
        """
        Deactivate user account
        
        Args:
            user_id: User ID to deactivate
            
        Returns:
            Dict containing success status and message
        """
        try:
            with transaction.atomic():
                user = User.objects.get(id=user_id)
                user.profile.is_active = False
                user.profile.save()
                
                return {
                    'success': True,
                    'message': f'User {user.username} has been deactivated'
                }
                
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
