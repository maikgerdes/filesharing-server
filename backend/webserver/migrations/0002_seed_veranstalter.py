from django.db import migrations


def seed_veranstalter(apps, schema_editor):
	Veranstalter = apps.get_model('webserver', 'Veranstalter')

	Veranstalter.objects.get_or_create(
		Veranstalter_Name='Muster Veranstaltungs GmbH',
		defaults={
			'Veranstalter_Email': 'info@muster-veranstaltungs-gmbh.de',
			'Veranstalter_Telefonnummer': '+49 40 12345678',
			'Veranstalter_Hauptsitz': 'Hamburg',
		},
	)


def unseed_veranstalter(apps, schema_editor):
	Veranstalter = apps.get_model('webserver', 'Veranstalter')
	Veranstalter.objects.filter(Veranstalter_Name='Muster Veranstaltungs GmbH').delete()


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0001_initial'),
	]

	operations = [
		migrations.RunPython(seed_veranstalter, unseed_veranstalter),
	]