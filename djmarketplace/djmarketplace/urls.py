"""djmarketplace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('app_users.urls', 'app_users'), namespace='app_users')),
    path('cart/', include(('app_cart.urls', 'app_cart'), namespace='app_cart')),
    path('order/', include(('app_order.urls', 'app_order'), namespace='app_order')),
    path('', include(('app_shop.urls', 'app_shop'), namespace='app_shop')),

    path('i18n', include('django.conf.urls.i18n')),
    # path('__debug__/', include('debug_toolbar.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)