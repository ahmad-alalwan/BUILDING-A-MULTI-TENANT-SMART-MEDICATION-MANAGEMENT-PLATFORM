from django.urls import path,include
from . import views 


urlpatterns = [
    path('search/<str:pk>',views.search_mdicine,name='search'),
    path('sale/<str:pk>',views.sale),
    path('medicines/',views.all_medicine),
    path('register_add/<str:pk1>/<str:pk2>',views.register_add),
    path('register_show/',views.reqistes_show),
    path('add_medicien/',views.add_Medicien),


]