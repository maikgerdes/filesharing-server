from django.core.management.base import BaseCommand
from django.utils import timezone

from webserver.models import (
    Personengruppe,
    Person,
    Veranstalter,
    Veranstaltung_Kategorie,
    Veranstaltung,
    Veranstaltung_Ticket_Umfang,
    Einladung_Status,
    Veranstaltung_Einladung,
    Einladung_Kommentar,
    Einladung_Entscheidung,
    Datei,
)


class Command(BaseCommand):
    help = 'Seed the database with example data for local development'

    def handle(self, *args, **options):
        created = {}

        # Personengruppen
        pg_journalisten, _ = Personengruppe.objects.get_or_create(Personengruppe_Name='Journalisten')
        pg_partner, _ = Personengruppe.objects.get_or_create(Personengruppe_Name='Partner')
        created['personengruppen'] = 2

        # Personen
        alice, _ = Person.objects.get_or_create(
            Vorname='Alice', Nachname='Muster', Person_Email='alice@example.com',
            Person_HashedPassword='hash', Person_Salt='salt', Personengruppe_ID=pg_journalisten
        )
        bob, _ = Person.objects.get_or_create(
            Vorname='Bob', Nachname='Beispiel', Person_Email='bob@example.com',
            Person_HashedPassword='hash', Person_Salt='salt', Personengruppe_ID=pg_partner
        )
        created['personen'] = 2

        # Veranstalter
        organiser, _ = Veranstalter.objects.get_or_create(
            Veranstalter_Name='Beispiel Veranstalter GmbH',
            Veranstalter_Email='kontakt@beispiel.de',
            Veranstalter_Telefonnummer='+49-30-123456',
            Veranstalter_Hauptsitz='Berlin',
        )
        created['veranstalter'] = 1

        # Kategorien
        cat_conf, _ = Veranstaltung_Kategorie.objects.get_or_create(Kategorie_Name='Konferenz')
        cat_meetup, _ = Veranstaltung_Kategorie.objects.get_or_create(Kategorie_Name='Meetup')
        created['kategorien'] = 2

        # Veranstaltungen
        event_conf, _ = Veranstaltung.objects.get_or_create(
            Veranstalter_ID=organiser,
            Veranstaltung_Kategorie_ID=cat_conf,
            Veranstaltung_Beschreibung='Jährliche Konferenz zu Beispielen',
            Veranstaltung_Webseite='https://example.com/konferenz',
            Veranstaltung_Sprache='de',
            Veranstaltung_Subevent='Haupttag',
            Veranstaltung_Name='Beispiel Konferenz 2026',
        )
        event_meetup, _ = Veranstaltung.objects.get_or_create(
            Veranstalter_ID=organiser,
            Veranstaltung_Kategorie_ID=cat_meetup,
            Veranstaltung_Beschreibung='Monatliches Meetup',
            Veranstaltung_Webseite='https://example.com/meetup',
            Veranstaltung_Sprache='de',
            Veranstaltung_Subevent='Abend',
            Veranstaltung_Name='Beispiel Meetup Mai',
        )
        created['veranstaltungen'] = 2

        # Ticket-Umfänge
        tu1, _ = Veranstaltung_Ticket_Umfang.objects.get_or_create(
            Veranstaltung_ID=event_conf,
            Ticket_Typ='Standard',
            defaults={
                'Aufnahmen': True,
                'Aufnahmen_Zensiert': False,
                'Umfang_der_Aufnahmen': 'Audio- und Videoaufnahmen',
                'Kosten': 99.0,
                'Informationen_Geprueft': True,
            }
        )
        tu2, _ = Veranstaltung_Ticket_Umfang.objects.get_or_create(
            Veranstaltung_ID=event_conf,
            Ticket_Typ='VIP',
            defaults={
                'Aufnahmen': True,
                'Aufnahmen_Zensiert': False,
                'Umfang_der_Aufnahmen': 'Aufnahmen + Backstage Zugang',
                'Kosten': 199.0,
                'Informationen_Geprueft': True,
            }
        )
        created['ticket_umfaenge'] = 2

        # Einladung Status
        status_offen, _ = Einladung_Status.objects.get_or_create(Status_Titel='Offen', defaults={'Status_Bedeutung': 'Einladung wurde noch nicht beantwortet'})
        status_angenommen, _ = Einladung_Status.objects.get_or_create(Status_Titel='Angenommen', defaults={'Status_Bedeutung': 'Einladung angenommen'})
        status_abgelehnt, _ = Einladung_Status.objects.get_or_create(Status_Titel='Abgelehnt', defaults={'Status_Bedeutung': 'Einladung abgelehnt'})
        created['einladung_status'] = 3

        # Einladungen
        invite, _ = Veranstaltung_Einladung.objects.get_or_create(
            VIP_anwesend=False,
            Anfragesteller_ID=alice,
            Repraesentiert=pg_journalisten,
            Veranstaltung_ID=event_conf,
            Ticket_Typ='Standard',
            Veranstaltung_Ticket_Umfang_pk=tu1,
            Veranstaltung_Grund='Berichterstattung über die Veranstaltung',
            Anzahl_Eingeladener_Gäste=1,
            Status=status_offen,
        )
        created['einladungen'] = 1

        # Kommentar
        komment, _ = Einladung_Kommentar.objects.get_or_create(
            Veranstaltung_Einladung_ID=invite,
            Parent_ID=None,
            Absender_ID=bob,
            Kommentar_Inhalt='Freue mich auf die Teilnahme.'
        )
        created['kommentare'] = 1

        # Entscheidung
        entscheid, _ = Einladung_Entscheidung.objects.get_or_create(
            Veranstaltung_Einladung_ID=invite,
            Personengruppe_ID=pg_journalisten,
            Zugesagt_von_Person_ID=alice,
            Zugesagt=True,
            Anmerkung='Bestätigt',
        )
        created['entscheidungen'] = 1

        # Datei-Beispiel
        Datei.objects.get_or_create(
            Datei_Name='beispiel.json',
            Datei_Pfad='/uploads/beispiel.json',
            Datei_Typ='application/json',
            Datei_Inhalt={'example': 'data'},
            Uploader=alice,
            Datei_Inhalt_Benoetigt=False,
        )
        created['dateien'] = 1

        # Zusammenfassung ausgeben
        self.stdout.write(self.style.SUCCESS('Seed-Daten wurden erstellt/gefunden:'))
        for k, v in created.items():
            self.stdout.write(f'- {k}: {v}')
