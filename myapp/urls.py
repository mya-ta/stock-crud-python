from django.urls import path
from . import views

urlpatterns = [
    path('', views.create_product, name='create_product'),
    path('search/', views.search_product, name='search_product'),
    path('childlist/', views.child_list, name='child_list'),
    path('list/', views.product_list, name='product_list'),
    path('update/<int:id>/<str:category>', views.update_product, name='update_product'),
    path('delete_product/<int:id>/<str:category>', views.delete_product, name='delete_product'),
    path('export_all/', views.export_data, name='export_data'),
    path('export/', views.export_csv, name='export_csv'),
]
