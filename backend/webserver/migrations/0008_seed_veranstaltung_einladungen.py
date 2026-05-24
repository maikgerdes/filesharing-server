from django.db import migrations


EINLADUNGEN = [
	{
		'Veranstaltung_Name': 'Sommermusik-Festival 2026',
		'Anfragesteller_Email': 'anna.bergmann@example.com',
		'Repraesentiert_Gruppe': 'Presse',
		'Ticket_Typ': 'Standard',
		'VIP_anwesend': False,
		'Veranstaltung_Grund': 'Berichterstattung über regionale Kultur-Highlights.',
		'Anzahl_Eingeladener_Gäste': 2,
		'Status_Titel': 'in Bewertung',
	},
	{
		'Veranstaltung_Name': 'Zukunft der Arbeit Konferenz 2026',
		'Anfragesteller_Email': 'lukas.schneider@example.com',
		'Repraesentiert_Gruppe': 'Influencer',
		'Ticket_Typ': 'Presse',
		'VIP_anwesend': True,
		'Veranstaltung_Grund': 'Content-Serie zu Trends im Bereich New Work.',
		'Anzahl_Eingeladener_Gäste': 1,
		'Status_Titel': 'angenommen und Koordinator übergeben',
	},
	{
		'Veranstaltung_Name': 'Kreativ-Workshopreihe Design Thinking',
		'Anfragesteller_Email': 'miriam.klein@example.com',
		'Repraesentiert_Gruppe': 'Kooperationspartner',
		'Ticket_Typ': 'VIP',
		'VIP_anwesend': False,
		'Veranstaltung_Grund': 'Partnerschaftsgespräch zur Entwicklung gemeinsamer Workshops.',
		'Anzahl_Eingeladener_Gäste': 3,
		'Status_Titel': 'angenommen und abgeschlossen',
	},
	{
		'Veranstaltung_Name': 'Hamburg Karriere Messe 2026',
		'Anfragesteller_Email': 'jonas.weber@example.com',
		'Repraesentiert_Gruppe': 'Presse',
		'Ticket_Typ': 'Standard',
		'VIP_anwesend': False,
		'Veranstaltung_Grund': 'Pressebeitrag zu Arbeitgebermarken auf Karrieremessen.',
		'Anzahl_Eingeladener_Gäste': 2,
		'Status_Titel': 'abgelehnt',
	},
	{
		'Veranstaltung_Name': 'Stadtlauf & Charity Cup',
		'Anfragesteller_Email': 'sofia.reuter@example.com',
		'Repraesentiert_Gruppe': 'Influencer',
		'Ticket_Typ': 'Presse',
		'VIP_anwesend': True,
		'Veranstaltung_Grund': 'Social-Media-Begleitung des Charity-Laufs.',
		'Anzahl_Eingeladener_Gäste': 1,
		'Status_Titel': 'in Bewertung',
	},
	{
		'Veranstaltung_Name': 'Theaterabend: Moderne Klassiker',
		'Anfragesteller_Email': 'anna.bergmann@example.com',
		'Repraesentiert_Gruppe': 'Presse',
		'Ticket_Typ': 'VIP',
		'VIP_anwesend': False,
		'Veranstaltung_Grund': 'Kulturkritik zur Premiere mit Fokus auf Inszenierung.',
		'Anzahl_Eingeladener_Gäste': 2,
		'Status_Titel': 'angenommen und Koordinator übergeben',
	},
	{
		'Veranstaltung_Name': 'Sommermusik-Festival 2026',
		'Anfragesteller_Email': 'lukas.schneider@example.com',
		'Repraesentiert_Gruppe': 'Influencer',
		'Ticket_Typ': 'Standard',
		'VIP_anwesend': False,
		'Veranstaltung_Grund': 'Live-Storytelling vor Ort für Musik-Community.',
		'Anzahl_Eingeladener_Gäste': 1,
		'Status_Titel': 'abgelehnt',
	},
	{
		'Veranstaltung_Name': 'Zukunft der Arbeit Konferenz 2026',
		'Anfragesteller_Email': 'miriam.klein@example.com',
		'Repraesentiert_Gruppe': 'Kooperationspartner',
		'Ticket_Typ': 'Standard',
		'VIP_anwesend': False,
		'Veranstaltung_Grund': 'Sondierung neuer Partner für Panel-Formate.',
		'Anzahl_Eingeladener_Gäste': 2,
		'Status_Titel': 'angenommen und abgeschlossen',
	},
	{
		'Veranstaltung_Name': 'Kreativ-Workshopreihe Design Thinking',
		'Anfragesteller_Email': 'jonas.weber@example.com',
		'Repraesentiert_Gruppe': 'Presse',
		'Ticket_Typ': 'Presse',
		'VIP_anwesend': False,
		'Veranstaltung_Grund': 'Fachartikel über Methoden und Lernergebnisse.',
		'Anzahl_Eingeladener_Gäste': 2,
		'Status_Titel': 'in Bewertung',
	},
	{
		'Veranstaltung_Name': 'Theaterabend: Moderne Klassiker',
		'Anfragesteller_Email': 'sofia.reuter@example.com',
		'Repraesentiert_Gruppe': 'Influencer',
		'Ticket_Typ': 'Standard',
		'VIP_anwesend': True,
		'Veranstaltung_Grund': 'Behind-the-scenes-Reihe für Kulturinteressierte.',
		'Anzahl_Eingeladener_Gäste': 1,
		'Status_Titel': 'angenommen und abgeschlossen',
	},
]


def seed_veranstaltung_einladungen(apps, schema_editor):
	Veranstaltung = apps.get_model('webserver', 'Veranstaltung')
	Person = apps.get_model('webserver', 'Person')
	Personengruppe = apps.get_model('webserver', 'Personengruppe')
	Status = apps.get_model('webserver', 'Status')
	Veranstaltung_Einladung = apps.get_model('webserver', 'Veranstaltung_Einladung')

	veranstaltungen = {
		veranstaltung.Veranstaltung_Name: veranstaltung
		for veranstaltung in Veranstaltung.objects.all()
	}
	personen = {person.Person_Email: person for person in Person.objects.all()}
	gruppen = {gruppe.Personengruppe_Name: gruppe for gruppe in Personengruppe.objects.all()}
	status_map = {status.Status_Titel: status for status in Status.objects.all()}

	for einladung in EINLADUNGEN:
		Veranstaltung_Einladung.objects.get_or_create(
			Veranstaltung_ID=veranstaltungen[einladung['Veranstaltung_Name']],
			Anfragesteller_ID=personen[einladung['Anfragesteller_Email']],
			Ticket_Typ=einladung['Ticket_Typ'],
			Veranstaltung_Grund=einladung['Veranstaltung_Grund'],
			defaults={
				'VIP_anwesend': einladung['VIP_anwesend'],
				'Repraesentiert': gruppen[einladung['Repraesentiert_Gruppe']],
				'Anzahl_Eingeladener_Gäste': einladung['Anzahl_Eingeladener_Gäste'],
				'Status': status_map[einladung['Status_Titel']],
			},
		)


def unseed_veranstaltung_einladungen(apps, schema_editor):
	Veranstaltung_Einladung = apps.get_model('webserver', 'Veranstaltung_Einladung')
	Veranstaltung_Einladung.objects.filter(
		Veranstaltung_Grund__in=[einladung['Veranstaltung_Grund'] for einladung in EINLADUNGEN]
	).delete()


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0007_seed_einladung_status'),
	]

	operations = [
		migrations.RunPython(seed_veranstaltung_einladungen, unseed_veranstaltung_einladungen),
	]