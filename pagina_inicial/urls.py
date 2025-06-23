from django.urls import path
from . import views

app_name = 'pagina_inicial'

# path('', include('pagina_inicial.urls', namespace='pagina_inicial')), # já deve estar lá

urlpatterns = [
    path('', views.pagina_inicial_view, name='home'),
]