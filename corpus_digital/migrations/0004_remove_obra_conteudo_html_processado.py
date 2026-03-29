from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus_digital', '0003_obra_data_referencia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='obra',
            name='conteudo_html_processado',
        ),
    ]
