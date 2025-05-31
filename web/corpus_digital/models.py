from django.db import models

# Create your models here.

class Obra(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    caminho_arquivo = models.CharField(max_length=300)  # caminho relativo ao app
    ordem = models.PositiveIntegerField(default=0)  # opcional, para ordenar a exibição

    def __str__(self):
        return f"{self.autor}: {self.titulo}"