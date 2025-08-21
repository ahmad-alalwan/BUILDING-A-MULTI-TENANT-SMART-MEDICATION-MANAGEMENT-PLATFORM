from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from .utils import generate_account_number, generate_verification_token

# Create your models here.

class Tenant(models.Model):
    """Tenant model for multi-tenant architecture"""
    name = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=100, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tenant'
        verbose_name_plural = 'Tenants'
    
    def __str__(self):
        return self.name

# Create your models here.

class Role(models.Model):
    """User roles for the system"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('expert', 'Expert'),
        ('user', 'User'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=20, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tenant', 'name']
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name

class Account(models.Model):
    """Extended account model with additional fields"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='accounts')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    account_number = models.CharField(max_length=20, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_login_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['tenant', 'account_number']
    
    class Meta:
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'
    
    def __str__(self):
        return f"Account {self.account_number} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.account_number:
            # Generate unique account number using ID
            super().save(*args, **kwargs)
            self.account_number = generate_account_number(self.id)
            super().save(update_fields=['account_number'])
        else:
            super().save(*args, **kwargs)

class AccessToken(models.Model):
    """Access token model for authentication"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='access_tokens')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_tokens')
    token = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['tenant', 'token']
    
    class Meta:
        verbose_name = 'Access Token'
        verbose_name_plural = 'Access Tokens'
    
    def __str__(self):
        return f"Token for {self.user.username} - {self.created_at}"
    
    def is_expired(self):
        """Check if token is expired"""
        return datetime.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Set expiration to 24 hours from now
            self.expires_at = datetime.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

class UserProfile(models.Model):
    """Extended user profile with role information"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='user_profiles')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def is_admin(self):
        return self.role and self.role.name == 'admin'
    
    @property
    def is_expert(self):
        return self.role and self.role.name == 'expert'

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when a new user is created"""
    if created:
        # Get default tenant (you can modify this logic based on your needs)
        default_tenant, _ = Tenant.objects.get_or_create(
            name='Default Tenant',
            defaults={'domain': 'default.local'}
        )
        
        # Get default role for this tenant
        default_role, _ = Role.objects.get_or_create(
            tenant=default_tenant,
            name='user',
            defaults={'description': 'Regular user'}
        )
        
        UserProfile.objects.create(user=instance, tenant=default_tenant, role=default_role)
        # Create account
        Account.objects.create(user=instance, tenant=default_tenant)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    instance.profile.save()
    if hasattr(instance, 'account'):
        instance.account.save()
