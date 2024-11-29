from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_product, name='create_product'),
    path('list/', views.product_list, name='product_list'),
    # path('update/<int:id>/', views.update_product, name='update_product'),
    path('update/<int:id>/', views.update_product, name='update_product'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('export/', views.export_csv, name='export_csv'),
]
