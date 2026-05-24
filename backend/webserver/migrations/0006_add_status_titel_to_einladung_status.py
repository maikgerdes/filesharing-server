from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webserver', '0005_seed_personen_und_ticketumfang'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='Status_Titel',
            field=models.CharField(default='Unbekannt', max_length=100),
            preserve_default=False,
        ),
    ]
