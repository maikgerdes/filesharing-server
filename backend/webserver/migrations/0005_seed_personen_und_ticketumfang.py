from django.db import migrations


PERSONENGRUPPEN = [
	'Presse',
	'Influencer',
	'Kooperationspartner',
]


PERSONEN = [
	{
		'Vorname': 'Anna',
		'Nachname': 'Bergmann',
		'Person_Email': 'anna.bergmann@example.com',
		'Person_HashedPassword': 'hashed_pw_anna',
		'Person_Salt': 'salt_anna_001',
		'Personengruppe_Name': 'Presse',
	},
	{
		'Vorname': 'Lukas',
		'Nachname': 'Schneider',
		'Person_Email': 'lukas.schneider@example.com',
		'Person_HashedPassword': 'hashed_pw_lukas',
		'Person_Salt': 'salt_lukas_001',
		'Personengruppe_Name': 'Influencer',
	},
	{
		'Vorname': 'Miriam',
		'Nachname': 'Klein',
		'Person_Email': 'miriam.klein@example.com',
		'Person_HashedPassword': 'hashed_pw_miriam',
		'Person_Salt': 'salt_miriam_001',
		'Personengruppe_Name': 'Kooperationspartner',
	},
	{
		'Vorname': 'Jonas',
		'Nachname': 'Weber',
		'Person_Email': 'jonas.weber@example.com',
		'Person_HashedPassword': 'hashed_pw_jonas',
		'Person_Salt': 'salt_jonas_001',
		'Personengruppe_Name': 'Presse',
	},
	{
		'Vorname': 'Sofia',
		'Nachname': 'Reuter',
		'Person_Email': 'sofia.reuter@example.com',
		'Person_HashedPassword': 'hashed_pw_sofia',
		'Person_Salt': 'salt_sofia_001',
		'Personengruppe_Name': 'Influencer',
	},
]


TICKET_VORLAGEN = [
	{
		'Ticket_Typ': 'Standard',
		'Aufnahmen': False,
		'Aufnahmen_Zensiert': False,
		'Umfang_der_Aufnahmen': 'Keine Aufnahmen erlaubt',
		'Kosten': 0.0,
	},
	{
		'Ticket_Typ': 'Presse',
		'Aufnahmen': True,
		'Aufnahmen_Zensiert': False,
		'Umfang_der_Aufnahmen': 'Foto- und Videoaufnahmen im Pressebereich erlaubt',
		'Kosten': 49.0,
	},
	{
		'Ticket_Typ': 'VIP',
		'Aufnahmen': True,
		'Aufnahmen_Zensiert': True,
		'Umfang_der_Aufnahmen': 'Aufnahmen in freigegebenen Bereichen mit Freigabe',
		'Kosten': 149.0,
	},
]


def seed_personen_und_ticketumfang(apps, schema_editor):
	Personengruppe = apps.get_model('webserver', 'Personengruppe')
	Person = apps.get_model('webserver', 'Person')
	Veranstaltung = apps.get_model('webserver', 'Veranstaltung')
	Veranstaltung_Ticket_Umfang = apps.get_model('webserver', 'Veranstaltung_Ticket_Umfang')

	gruppen = {}
	for gruppen_name in PERSONENGRUPPEN:
		gruppe, _ = Personengruppe.objects.get_or_create(Personengruppe_Name=gruppen_name)
		gruppen[gruppen_name] = gruppe

	for person in PERSONEN:
		Person.objects.get_or_create(
			Person_Email=person['Person_Email'],
			defaults={
				'Vorname': person['Vorname'],
				'Nachname': person['Nachname'],
				'Person_HashedPassword': person['Person_HashedPassword'],
				'Person_Salt': person['Person_Salt'],
				'Personengruppe_ID': gruppen[person['Personengruppe_Name']],
			},
		)

	veranstaltungen = Veranstaltung.objects.order_by('Veranstaltung_ID')
	for index, veranstaltung in enumerate(veranstaltungen):
		anzahl_ticketarten = (index % 3) + 1
		for ticket_vorlage in TICKET_VORLAGEN[:anzahl_ticketarten]:
			Veranstaltung_Ticket_Umfang.objects.get_or_create(
				Veranstaltung_ID=veranstaltung,
				Ticket_Typ=ticket_vorlage['Ticket_Typ'],
				defaults={
					'Aufnahmen': ticket_vorlage['Aufnahmen'],
					'Aufnahmen_Zensiert': ticket_vorlage['Aufnahmen_Zensiert'],
					'Umfang_der_Aufnahmen': ticket_vorlage['Umfang_der_Aufnahmen'],
					'Kosten': ticket_vorlage['Kosten'],
				},
			)


def unseed_personen_und_ticketumfang(apps, schema_editor):
	Personengruppe = apps.get_model('webserver', 'Personengruppe')
	Person = apps.get_model('webserver', 'Person')
	Veranstaltung_Ticket_Umfang = apps.get_model('webserver', 'Veranstaltung_Ticket_Umfang')

	Person.objects.filter(Person_Email__in=[person['Person_Email'] for person in PERSONEN]).delete()
	Personengruppe.objects.filter(Personengruppe_Name__in=PERSONENGRUPPEN).delete()
	Veranstaltung_Ticket_Umfang.objects.filter(
		Ticket_Typ__in=[ticket['Ticket_Typ'] for ticket in TICKET_VORLAGEN]
	).delete()


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0004_seed_veranstaltungen'),
	]

	operations = [
		migrations.RunPython(seed_personen_und_ticketumfang, unseed_personen_und_ticketumfang),
	]