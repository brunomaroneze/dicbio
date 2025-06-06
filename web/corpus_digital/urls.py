from django.urls import path
from . import views

app_name = 'corpus_digital'

urlpatterns = [
    path('', views.home, name='corpus'),
    path('<slug:slug>/', views.home, name='obra_detalhe'),
]
