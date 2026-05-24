from django.db import migrations


VERANSTALTUNGEN = [
	{
		'Veranstaltung_Name': 'Sommermusik-Festival 2026',
		'Veranstaltung_Subevent': 'Hauptprogramm',
		'Veranstaltung_Beschreibung': 'Open-Air-Festival mit regionalen und internationalen Live-Acts an drei Sommerabenden.',
		'Veranstaltung_Webseite': 'https://muster-veranstaltungen.de/sommermusik-festival-2026',
		'Veranstaltung_Sprache': 'Deutsch',
		'Kategorie_Name': 'Festival',
	},
	{
		'Veranstaltung_Name': 'Zukunft der Arbeit Konferenz 2026',
		'Veranstaltung_Subevent': 'Fachprogramm',
		'Veranstaltung_Beschreibung': 'Fachkonferenz zu New Work, digitalen Prozessen und modernen Führungsmodellen.',
		'Veranstaltung_Webseite': 'https://muster-veranstaltungen.de/zukunft-der-arbeit-konferenz-2026',
		'Veranstaltung_Sprache': 'Deutsch',
		'Kategorie_Name': 'Konferenz',
	},
	{
		'Veranstaltung_Name': 'Kreativ-Workshopreihe Design Thinking',
		'Veranstaltung_Subevent': 'Tag 1',
		'Veranstaltung_Beschreibung': 'Praxisnaher Workshop für Teams, die neue Ideen strukturiert entwickeln und testen möchten.',
		'Veranstaltung_Webseite': 'https://muster-veranstaltungen.de/kreativ-workshop-design-thinking',
		'Veranstaltung_Sprache': 'Deutsch',
		'Kategorie_Name': 'Workshop',
	},
	{
		'Veranstaltung_Name': 'Hamburg Karriere Messe 2026',
		'Veranstaltung_Subevent': 'Ausstellerbereich',
		'Veranstaltung_Beschreibung': 'Karrieremesse mit Unternehmensständen, Bewerbungscoaching und Kurzvorträgen für Berufseinsteiger.',
		'Veranstaltung_Webseite': 'https://muster-veranstaltungen.de/hamburg-karriere-messe-2026',
		'Veranstaltung_Sprache': 'Deutsch',
		'Kategorie_Name': 'Messe',
	},
	{
		'Veranstaltung_Name': 'Stadtlauf & Charity Cup',
		'Veranstaltung_Subevent': 'Hauptlauf',
		'Veranstaltung_Beschreibung': 'Sportveranstaltung mit Laufstrecken für verschiedene Altersklassen und einem Benefizanteil.',
		'Veranstaltung_Webseite': 'https://muster-veranstaltungen.de/stadtlauf-charity-cup',
		'Veranstaltung_Sprache': 'Deutsch',
		'Kategorie_Name': 'Sportveranstaltung',
	},
	{
		'Veranstaltung_Name': 'Theaterabend: Moderne Klassiker',
		'Veranstaltung_Subevent': 'Premiere',
		'Veranstaltung_Beschreibung': 'Szenischer Abend mit zeitgenössischen Interpretationen bekannter Theaterstücke.',
		'Veranstaltung_Webseite': 'https://muster-veranstaltungen.de/theaterabend-moderne-klassiker',
		'Veranstaltung_Sprache': 'Deutsch',
		'Kategorie_Name': 'Theater',
	},
]


def seed_veranstaltungen(apps, schema_editor):
	Veranstalter = apps.get_model('webserver', 'Veranstalter')
	Veranstaltung = apps.get_model('webserver', 'Veranstaltung')
	Veranstaltung_Kategorie = apps.get_model('webserver', 'Veranstaltung_Kategorie')

	veranstalter = Veranstalter.objects.get(Veranstalter_Name='Muster Veranstaltungs GmbH')

	for veranstaltung in VERANSTALTUNGEN:
		kategorie = Veranstaltung_Kategorie.objects.get(Kategorie_Name=veranstaltung['Kategorie_Name'])
		Veranstaltung.objects.get_or_create(
			Veranstaltung_Name=veranstaltung['Veranstaltung_Name'],
			Veranstaltung_Subevent=veranstaltung['Veranstaltung_Subevent'],
			defaults={
				'Veranstalter_ID': veranstalter,
				'Veranstaltung_Kategorie_ID': kategorie,
				'Veranstaltung_Beschreibung': veranstaltung['Veranstaltung_Beschreibung'],
				'Veranstaltung_Webseite': veranstaltung['Veranstaltung_Webseite'],
				'Veranstaltung_Sprache': veranstaltung['Veranstaltung_Sprache'],
			},
		)


def unseed_veranstaltungen(apps, schema_editor):
	Veranstaltung = apps.get_model('webserver', 'Veranstaltung')
	Veranstaltung.objects.filter(
		Veranstaltung_Name__in=[eintrag['Veranstaltung_Name'] for eintrag in VERANSTALTUNGEN],
		Veranstaltung_Subevent__in=[eintrag['Veranstaltung_Subevent'] for eintrag in VERANSTALTUNGEN],
	).delete()


class Migration(migrations.Migration):

	dependencies = [
		('webserver', '0003_seed_veranstaltung_kategorien'),
	]

	operations = [
		migrations.RunPython(seed_veranstaltungen, unseed_veranstaltungen),
	]