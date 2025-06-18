from django.urls import path,include
from product import views

urlpatterns = [
    path('',views.ProductView.as_view(),name='product-list'),
    path('<int:pk>',views.ProductDetails.as_view(),name='specific-product')
]
