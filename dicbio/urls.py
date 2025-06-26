"""
URL configuration for dicbio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', include('pagina_inicial.urls', namespace='pagina_inicial')),
    path('documentacao/', include('documentacao.urls', namespace='documentacao')),
    path('consulta/', include('verbetes.urls', namespace='verbetes')),
    path('corpus/', include('corpus_digital.urls', namespace='corpus_digital')),
]

urlpatterns += [
    re_path(r'static/(?P<path>.*)$', serve, {
        'document_root': settings.STATIC_ROOT
    })
]
