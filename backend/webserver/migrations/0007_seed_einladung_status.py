from django.db import migrations


STATUS_EINTRAEGE = [
	{
		'Status_Titel': 'angenommen und Koordinator übergeben',
		'Status_Bedeutung': 'Die Einladung wurde angenommen und zur weiteren Organisation an den Koordinator weitergeleitet.',
	},
	{
		'Status_Titel': 'angenommen und abgeschlossen',
		'Status_Bedeutung': 'Die Einladung wurde angenommen und der gesamte Vorgang ist abgeschlossen.',
	},
	{
		'Status_Titel': 'abgelehnt',
		'Status_Bedeutung': 'Die Einladung wurde geprüft und abgelehnt.',
	},
	{
		'Status_Titel': 'in Bewertung',
		'Status_Bedeutung': 'Die Einladung wird aktuell intern geprüft und bewertet.',
	},
]


def seed_einladung_status(apps, schema_editor):
	Status = apps.get_model('webserver', 'Status')

	for status in STATUS_EINTRAEGE:
		Status.objects.get_or_create(
			Status_Titel=status['Status_Titel'],
			defaults={
				'Status_Bedeutung': status['Status_Bedeutung'],
			},
		)


def unseed_einladung_status(apps, schema_editor):
	Status = apps.get_model('webserver', 'Status')
	Status.objects.filter(
		Status_Titel__in=[status['Status_Titel'] for status in STATUS_EINTRAEGE]
	).delete()


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0006_add_status_titel_to_einladung_status'),
	]

	operations = [
		migrations.RunPython(seed_einladung_status, unseed_einladung_status),
	]