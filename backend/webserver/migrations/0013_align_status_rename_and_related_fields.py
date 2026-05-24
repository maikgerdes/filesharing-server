from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webserver', '0012_add_geprueft_von_to_checked_models'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameModel(
                    old_name='Status',
                    new_name='Einladung_Status',
                ),
                migrations.AlterModelTable(
                    name='einladung_status',
                    table='webserver_status',
                ),
            ],
        ),
        migrations.DeleteModel(
            name='Files',
        ),
        migrations.AlterField(
            model_name='veranstaltung',
            name='Veranstalter_ID',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='Veranstaltungen',
                to='webserver.veranstalter',
            ),
        ),
        migrations.AlterField(
            model_name='veranstaltung_einladung',
            name='Veranstaltung_ID',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='Einladungen',
                to='webserver.veranstaltung',
            ),
        ),
        migrations.AlterField(
            model_name='veranstaltung_ticket_umfang',
            name='Veranstaltung_ID',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='Ticket_Arten',
                to='webserver.veranstaltung',
            ),
        ),
        migrations.AlterField(
            model_name='veranstaltung_einladung',
            name='Status',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='webserver.einladung_status',
            ),
        ),
    ]
