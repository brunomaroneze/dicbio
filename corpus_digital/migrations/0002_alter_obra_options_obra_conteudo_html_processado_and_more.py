# Generated by Django 5.2.1 on 2025-06-04 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus_digital', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='obra',
            options={'ordering': ['ordem', 'autor', 'titulo']},
        ),
        migrations.AddField(
            model_name='obra',
            name='conteudo_html_processado',
            field=models.TextField(blank=True, editable=False, help_text='Conteúdo HTML gerado a partir do arquivo TEI-XML. Preenchido automaticamente.', null=True),
        ),
        migrations.AlterField(
            model_name='obra',
            name='caminho_arquivo',
            field=models.CharField(help_text="Nome do arquivo XML (ex: 'documento.xml') ou caminho relativo dentro da pasta CORPUS_XML_ROOT (ex: 'subpasta/documento.xml').", max_length=300),
        ),
        migrations.AlterField(
            model_name='obra',
            name='ordem',
            field=models.PositiveIntegerField(default=0, help_text='Opcional: para ordenação customizada na listagem de obras.'),
        ),
        migrations.AlterField(
            model_name='obra',
            name='slug',
            field=models.SlugField(help_text='Identificador único para URLs, gerado automaticamente a partir do título se não for fornecido.', max_length=255, unique=True),
        ),
    ]
