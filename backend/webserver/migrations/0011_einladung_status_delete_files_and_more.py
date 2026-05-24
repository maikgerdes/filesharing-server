from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0010_alter_einladung_kommentar_parent_id'),
	]

	operations = [
		migrations.AddField(
			model_name='veranstalter',
			name='Informationen_Geprueft',
			field=models.BooleanField(default=False),
		),
		migrations.AddField(
			model_name='veranstaltung',
			name='Informationen_Geprueft',
			field=models.BooleanField(default=False),
		),
		migrations.AddField(
			model_name='veranstaltung_ticket_umfang',
			name='Informationen_Geprueft',
			field=models.BooleanField(default=False),
		),
	]
