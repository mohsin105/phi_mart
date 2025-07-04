"""
URL configuration for phi_mart project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from debug_toolbar.toolbar import debug_toolbar_urls
from phi_mart.views import api_root_view
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Phimart API",
      default_version='v1',
      description="Backend API documentation for PhiMart ecommerce service",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="mohsinibnaftab@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('',api_root_view),
    path('admin/', admin.site.urls),
    # path('api-auth/', include('rest_framework.urls')), #keno comment korlam? api view te logout option hide korar jonno comment korsi
    
    # path('products/',include('product.urls'))
    path('api/v1/',include('api.urls'),name='api-root'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + debug_toolbar_urls()

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
