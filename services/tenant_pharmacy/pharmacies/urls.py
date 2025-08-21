from django.urls import path, include
from . import views 

urlpatterns = [
    # Class-based views for Medicine
    path('api/medicines/', views.MedicineListCreateView.as_view(), name='medicine-list-create'),
    path('api/medicines/<int:id>/', views.MedicineDetailView.as_view(), name='medicine-detail'),
    path('api/medicines/search/<str:name>/', views.MedicineSearchView.as_view(), name='medicine-search'),
    path('api/medicines/sale/<str:name>/', views.MedicineSaleView.as_view(), name='medicine-sale'),
    
    # Class-based views for Register_Financial
    path('api/financial/', views.RegisterFinancialListCreateView.as_view(), name='financial-list-create'),
    path('api/financial/<int:invoice>/', views.RegisterFinancialDetailView.as_view(), name='financial-detail'),
    
    # Class-based views for Register_pharmacy
    path('api/pharmacy/', views.RegisterPharmacyListCreateView.as_view(), name='pharmacy-list-create'),
    path('api/pharmacy/<int:id>/', views.RegisterPharmacyDetailView.as_view(), name='pharmacy-detail'),
    path('api/pharmacy/ordered/', views.RegisterPharmacyOrderedView.as_view(), name='pharmacy-ordered'),
    path('api/pharmacy/add/<str:name_medicine>/<int:quantity>/', views.RegisterPharmacyAddView.as_view(), name='pharmacy-add'),
    
    # Legacy function-based views (keeping for backward compatibility)
    path('search/<str:pk>', views.search_mdicine, name='search'),
    path('sale/<str:pk>', views.sale),
    path('medicines/', views.all_medicine),
    path('register_add/<str:pk1>/<str:pk2>', views.register_add),
    path('register_show/', views.reqistes_show),
    path('add_medicien/', views.add_Medicien),
]