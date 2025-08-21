from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from .models import AccessToken, Account, Tenant
from .utils import generate_simple_token
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class TokenAuthService:
    """Token-based authentication service"""
    

    
    @staticmethod
    def generate_token(user: User, tenant: Tenant, ip_address: str = None, user_agent: str = None) -> AccessToken:
        """
        Generate a new access token for user
        
        Args:
            user: User object
            tenant: Tenant object
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            AccessToken object
        """
        # Deactivate existing tokens for this user in this tenant
        AccessToken.objects.filter(user=user, tenant=tenant, is_active=True).update(is_active=False)
        
        # Create new token with simple token generation
        token = AccessToken.objects.create(
            user=user,
            tenant=tenant,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Update token with generated value
        token.token = generate_simple_token(user.id)
        token.save()
        
        return token
    
    @staticmethod
    def validate_token(token_string: str, tenant: Tenant = None) -> Optional[User]:
        """
        Validate access token and return user if valid
        
        Args:
            token_string: Token string to validate
            tenant: Tenant object (optional, for additional validation)
            
        Returns:
            User object if token is valid, None otherwise
        """
        try:
            filters = {'token': token_string, 'is_active': True}
            if tenant:
                filters['tenant'] = tenant
                
            token = AccessToken.objects.get(**filters)
            
            # Check if token is expired
            if token.is_expired():
                token.is_active = False
                token.save()
                return None
            
            return token.user
            
        except AccessToken.DoesNotExist:
            return None
    
    @staticmethod
    def login_with_token(
        username: str, 
        password: str, 
        tenant: Tenant,
        ip_address: str = None, 
        user_agent: str = None
    ) -> Dict[str, Any]:
        """
        Login user and generate access token
        
        Args:
            username: Username or email
            password: User password
            ip_address: IP address of the request
            user_agent: User agent string
            
        Returns:
            Dict containing success status and token data or error message
        """
        try:
            with transaction.atomic():
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
                    # Check if user belongs to this tenant
                    if not hasattr(user, 'profile') or user.profile.tenant != tenant:
                        return {
                            'success': False,
                            'error': 'User does not belong to this tenant'
                        }
                    
                    # Generate token
                    token = TokenAuthService.generate_token(user, tenant, ip_address, user_agent)
                    
                    # Update account login info
                    if hasattr(user, 'account') and user.account.tenant == tenant:
                        user.account.last_login_ip = ip_address
                        user.account.last_login_time = datetime.now()
                        user.account.save()
                    
                    return {
                        'success': True,
                        'token': {
                            'access_token': token.token,
                            'expires_at': token.expires_at,
                            'user': {
                                'id': user.id,
                                'username': user.username,
                                'email': user.email,
                                'role': user.profile.role.name if user.profile.role else 'user',
                                'is_admin': user.profile.is_admin,
                                'is_expert': user.profile.is_expert,
                                'account_number': user.account.account_number if hasattr(user, 'account') else None
                            }
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
    def logout_with_token(token_string: str, tenant: Tenant = None) -> Dict[str, Any]:
        """
        Logout user by deactivating token
        
        Args:
            token_string: Token string to deactivate
            tenant: Tenant object (optional, for additional validation)
            
        Returns:
            Dict containing success status and message
        """
        try:
            filters = {'token': token_string, 'is_active': True}
            if tenant:
                filters['tenant'] = tenant
                
            token = AccessToken.objects.get(**filters)
            token.is_active = False
            token.save()
            
            return {
                'success': True,
                'message': 'Logout successful'
            }
            
        except AccessToken.DoesNotExist:
            return {
                'success': False,
                'error': 'Invalid token'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def refresh_token(token_string: str, tenant: Tenant = None) -> Dict[str, Any]:
        """
        Refresh access token
        
        Args:
            token_string: Current token string
            tenant: Tenant object (optional, for additional validation)
            
        Returns:
            Dict containing success status and new token data or error message
        """
        try:
            with transaction.atomic():
                # Validate current token
                user = TokenAuthService.validate_token(token_string, tenant)
                if not user:
                    return {
                        'success': False,
                        'error': 'Invalid or expired token'
                    }
                
                # Get current token to copy IP and user agent
                filters = {'token': token_string}
                if tenant:
                    filters['tenant'] = tenant
                current_token = AccessToken.objects.get(**filters)
                
                # Generate new token
                new_token = TokenAuthService.generate_token(
                    user, 
                    current_token.tenant,
                    current_token.ip_address, 
                    current_token.user_agent
                )
                
                return {
                    'success': True,
                    'token': {
                        'access_token': new_token.token,
                        'expires_at': new_token.expires_at,
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'role': user.profile.role.name if user.profile.role else 'user',
                            'is_admin': user.profile.is_admin,
                            'is_expert': user.profile.is_expert,
                            'account_number': user.account.account_number if hasattr(user, 'account') else None
                        }
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_user_from_token(token_string: str, tenant: Tenant = None) -> Optional[Dict[str, Any]]:
        """
        Get user information from token
        
        Args:
            token_string: Token string
            tenant: Tenant object (optional, for additional validation)
            
        Returns:
            Dict containing user data or None if token is invalid
        """
        user = TokenAuthService.validate_token(token_string, tenant)
        if user:
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'tenant_id': user.profile.tenant.id if hasattr(user, 'profile') else None,
                'tenant_name': user.profile.tenant.name if hasattr(user, 'profile') else None,
                'role': user.profile.role.name if user.profile.role else 'user',
                'is_admin': user.profile.is_admin,
                'is_expert': user.profile.is_expert,
                'account_number': user.account.account_number if hasattr(user, 'account') else None,
                'balance': float(user.account.balance) if hasattr(user, 'account') else 0.0,
                'is_verified': user.account.is_verified if hasattr(user, 'account') else False
            }
        return None
    
    @staticmethod
    def cleanup_expired_tokens(tenant: Tenant = None):
        """Clean up expired tokens"""
        filters = {
            'is_active': True,
            'expires_at__lt': datetime.now()
        }
        if tenant:
            filters['tenant'] = tenant
            
        expired_tokens = AccessToken.objects.filter(**filters)
        expired_tokens.update(is_active=False)
        return expired_tokens.count()
