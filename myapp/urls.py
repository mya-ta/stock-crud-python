from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.create_product, name='create_product'),
    path('list/', views.product_list, name='product_list'),
    path('update/<int:id>', views.update_product, name='update_product'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('export/', views.export_data, name='export_data'),

]
