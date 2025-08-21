from django.urls import path
from . import views
from . import token_views

app_name = 'auth'

urlpatterns = [
    # Session-based authentication endpoints
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User profile management
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Admin endpoints
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin/change-role/', views.AdminChangeRoleView.as_view(), name='admin_change_role'),
    path('admin/deactivate-user/<int:user_id>/', views.AdminDeactivateUserView.as_view(), name='admin_deactivate_user'),
    
    # Expert endpoints
    path('expert/users/', views.ExpertUserListView.as_view(), name='expert_users'),
    
    # General user lookup (admin/expert only)
    path('user/<int:user_id>/', views.get_user_by_id, name='get_user_by_id'),
    
    # Token-based authentication endpoints
    path('token/login/', token_views.TokenLoginView.as_view(), name='token_login'),
    path('token/logout/', token_views.TokenLogoutView.as_view(), name='token_logout'),
    path('token/refresh/', token_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('token/profile/', token_views.UserProfileView.as_view(), name='token_profile'),
    path('token/user-info/', token_views.get_user_info, name='token_user_info'),
    path('token/logout-header/', token_views.logout_with_header, name='token_logout_header'),
    
    # Account management endpoints
    path('account/', token_views.AccountDetailView.as_view(), name='account_detail'),
    path('account/balance/', token_views.AccountBalanceView.as_view(), name='account_balance'),
    path('account/verify/', token_views.AccountVerificationView.as_view(), name='account_verify'),
    path('account/transaction/', token_views.AccountTransactionView.as_view(), name='account_transaction'),
    path('admin/accounts/', token_views.AdminAccountListView.as_view(), name='admin_accounts'),
]
