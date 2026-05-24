from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0011_einladung_status_delete_files_and_more'),
	]

	operations = [
		migrations.AddField(
			model_name='veranstalter',
			name='Geprueft_Von',
			field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webserver.person'),
		),
		migrations.AddField(
			model_name='veranstaltung',
			name='Geprueft_Von',
			field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webserver.person'),
		),
		migrations.AddField(
			model_name='veranstaltung_ticket_umfang',
			name='Geprueft_Von',
			field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webserver.person'),
		),
	]
