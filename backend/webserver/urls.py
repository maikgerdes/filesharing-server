"""
URL configuration for webserver project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import include, path
from webserver.uploads.views import PostDocxDocument, PostUpdateDateiJson, PostValidateDateiJson
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path('api/v1/admin/', admin.site.urls),
    path('api/v1/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('api/v1/upload/docx/', PostDocxDocument.as_view()),
    path('api/v1/upload/docx/validate-model/', PostValidateDateiJson.as_view()),
    path('api/v1/upload/docx/update-json/', PostUpdateDateiJson.as_view()),
    path('api/v1/veranstalter/', include('webserver.veranstalter.urls')),
    path('api/v1/veranstaltungen/', include('webserver.veranstaltungen.urls')),
    path('api/v1/einladungen/', include('webserver.einladungen.urls')),
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc-v1'),
    # path('files/', views2.display_file)
]
