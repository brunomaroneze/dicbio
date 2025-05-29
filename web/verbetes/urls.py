from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='consulta'),  # página com a busca/lista
    path('<slug:slug>/', views.verbete_detalhe, name='verbetes_detalhe'),  # exibe verbete individual
]
