from django.db import models
from django.utils.text import slugify # Boa prática para gerar slugs automaticamente

class Obra(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    slug = models.SlugField(
        unique=True,
        max_length=255, # É uma boa ideia dar um max_length explícito e generoso para slugs
        help_text="Identificador único para URLs, gerado automaticamente a partir do título se não for fornecido."
    )
    caminho_arquivo = models.CharField(
        max_length=300,
        help_text="Nome do arquivo XML (ex: 'documento.xml') ou caminho relativo dentro da pasta CORPUS_XML_ROOT (ex: 'subpasta/documento.xml')."
    )
    ordem = models.PositiveIntegerField(
        default=0,
        help_text="Opcional: para ordenação customizada na listagem de obras."
    )

    conteudo_html_processado = models.TextField(
        blank=True,    # Permite que o campo seja vazio no formulário do admin
        null=True,     # Permite que o valor no banco de dados seja NULL
        editable=False, # Geralmente não queremos que este campo seja editável diretamente no admin,
                       # já que é preenchido por um script.
        help_text="Conteúdo HTML gerado a partir do arquivo TEI-XML. Preenchido automaticamente."
    )

    data_referencia = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="Data/ano de referência da obra (ex: 1750, c. 1800, Século XVIII)."
    )

    class Meta:
        ordering = ['ordem', 'autor', 'titulo'] # Define uma ordem padrão para consultas

    def __str__(self):
        return f"{self.autor} - {self.titulo}" # Um pouco mais comum usar hífen ou outra formatação

    def save(self, *args, **kwargs):
        # Gerar slug automaticamente se estiver vazio e o título existir
        if not self.slug and self.titulo and self.autor:
            base_slug = slugify(f"{self.autor} {self.titulo}")
            slug_candidato = base_slug
            num = 1
            # Garante que o slug seja único
            while Obra.objects.filter(slug=slug_candidato).exclude(pk=self.pk).exists():
                slug_candidato = f"{base_slug}-{num}"
                num += 1
            self.slug = slug_candidato
        super().save(*args, **kwargs)