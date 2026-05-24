from django.db import migrations


KATEGORIEN = [
	'Konzert',
	'Konferenz',
	'Workshop',
	'Messe',
	'Sportveranstaltung',
	'Theater',
	'Festival',
	'Networking-Event',
	'Webinar',
	'Ausstellung',
]


def seed_veranstaltung_kategorien(apps, schema_editor):
	Veranstaltung_Kategorie = apps.get_model('webserver', 'Veranstaltung_Kategorie')

	for kategorien_name in KATEGORIEN:
		Veranstaltung_Kategorie.objects.get_or_create(Kategorie_Name=kategorien_name)


def unseed_veranstaltung_kategorien(apps, schema_editor):
	Veranstaltung_Kategorie = apps.get_model('webserver', 'Veranstaltung_Kategorie')
	Veranstaltung_Kategorie.objects.filter(Kategorie_Name__in=KATEGORIEN).delete()


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0002_seed_veranstalter'),
	]

	operations = [
		migrations.RunPython(seed_veranstaltung_kategorien, unseed_veranstaltung_kategorien),
	]