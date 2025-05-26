from django.urls import path
from . import views

urlpatterns = [
    path('', views.texto, name='documentacao'),
    path('<str:nome_arquivo>/', views.texto, name='texto_documentacao'),
]
