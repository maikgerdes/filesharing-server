from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0008_seed_veranstaltung_einladungen'),
	]

	operations = [
		migrations.CreateModel(
			name='Datei',
			fields=[
				('Datei_ID', models.AutoField(primary_key=True, serialize=False)),
				('Datei_Name', models.CharField(max_length=150)),
				('Datei_Pfad', models.CharField(max_length=100)),
				('Datei_Typ', models.CharField(max_length=100)),
				('Datei_Inhalt', models.JSONField()),
				('Uploaddatum', models.DateTimeField(auto_now_add=True)),
				('Datei_Inhalt_Benoetigt', models.BooleanField()),
				('Uploader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webserver.person')),
			],
		),
	]