from django.contrib import admin
from .models import Tenant, Role, UserProfile, Account, AccessToken

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'domain', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'domain']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'description', 'created_at', 'updated_at']
    list_filter = ['name', 'tenant', 'created_at']
    search_fields = ['name', 'description', 'tenant__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'role', 'phone_number', 'is_active', 'created_at']
    list_filter = ['role', 'tenant', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number', 'tenant__name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('Profile Information', {
            'fields': ('bio', 'profile_picture')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'account_number', 'balance', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'tenant', 'created_at']
    search_fields = ['user__username', 'account_number', 'tenant__name']
    readonly_fields = ['account_number', 'created_at', 'updated_at']
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'account_number', 'balance')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_token')
        }),
        ('Login Information', {
            'fields': ('last_login_ip', 'last_login_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'tenant', 'token', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'tenant', 'created_at']
    search_fields = ['user__username', 'token', 'tenant__name']
    readonly_fields = ['token', 'created_at', 'expires_at']
    fieldsets = (
        ('Token Information', {
            'fields': ('user', 'token', 'is_active')
        }),
        ('Expiration', {
            'fields': ('created_at', 'expires_at')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent')
        })
    )
