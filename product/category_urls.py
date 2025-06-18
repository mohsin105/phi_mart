from django.urls import path,include
from product import views

urlpatterns = [
    path('',views.CategoryView.as_view(),name='product-list'),
    path('<int:pk>/',views.CategoryDetails.as_view(),name='view-specific-category')
]