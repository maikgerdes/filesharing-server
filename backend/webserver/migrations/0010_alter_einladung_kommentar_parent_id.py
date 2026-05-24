from django.db import migrations, models


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0009_create_datei'),
	]

	operations = [
		migrations.AlterField(
			model_name='einladung_kommentar',
			name='Parent_ID',
			field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, to='webserver.einladung_kommentar'),
		),
	]
