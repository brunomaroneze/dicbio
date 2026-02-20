from django.urls import path
from . import views

app_name = 'verbetes'

urlpatterns = [
    path('', views.home, name='consulta'),  # página com a busca/lista
    path('concordancia/<int:def_id>/', views.concordancia_por_definicao, name='ajax_concordancia'),
    path('<slug:slug>/', views.verbete_detalhe, name='detalhe'),  # exibe verbete individual
    # Nova rota para o teste do Turtle
    path('teste-turtle/<str:lema>/', views.verbete_pelo_turtle, name='verbete_turtle'),
]

