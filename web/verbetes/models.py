from django.db import models
from django.utils.text import slugify

# Modelo principal: Verbete

class Verbete(models.Model):
    termo = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    classe_gramatical = models.CharField(max_length=50, blank=True)
    etimologia = models.TextField(blank=True)
    primeira_ocorrencia = models.TextField(blank=True)
    data_ocorrencia = models.CharField(max_length=100, blank=True)
    autores = models.CharField(max_length=200, blank=True)
    criado_em = models.DateField(null=True, blank=True)
    atualizado_em = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.termo)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.termo


# Modelo das definições lexicográficas

class Definition(models.Model):
    verbete = models.ForeignKey(Verbete, on_delete=models.CASCADE, related_name='definicoes')
    sensenumber = models.IntegerField()
    definition = models.TextField()

    def __str__(self):
        return f"{self.verbete.termo} ({self.sensenumber})"


# Modelo das ocorrências nos textos do corpus

class OcorrenciaCorpus(models.Model):
    verbete = models.ForeignKey(Verbete, on_delete=models.CASCADE, related_name='ocorrencias')
    definicao = models.ForeignKey(Definition, on_delete=models.SET_NULL, null=True, blank=True, related_name='ocorrencias')

    token = models.CharField(max_length=100)
    orth = models.CharField(max_length=100, blank=True)
    gram = models.CharField(max_length=100, blank=True)
    frase = models.TextField()
    autor = models.CharField(max_length=100, blank=True)
    data = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.token} em {self.verbete.termo}"
