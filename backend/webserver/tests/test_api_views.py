from unittest.mock import patch
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from webserver.models import (
    Datei,
    Einladung_Entscheidung,
    Einladung_Kommentar,
    Einladung_Status,
    Person,
    Personengruppe,
    Veranstaltung,
    Veranstaltung_Einladung,
    Veranstaltung_Kategorie,
    Veranstaltung_Ticket_Umfang,
    Veranstalter,
)


@override_settings(ALLOWED_HOSTS=["testserver", "localhost"])
class APIV1ViewsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.personengruppe = Personengruppe.objects.create(Personengruppe_Name="Testgruppe")
        cls.person = Person.objects.create(
            Vorname="Max",
            Nachname="Mustermann",
            Person_Email="max@example.com",
            Person_HashedPassword="secret",
            Person_Salt="salt",
            Personengruppe_ID=cls.personengruppe,
        )
        cls.pruefer = Person.objects.create(
            Vorname="Pruefer",
            Nachname="Person",
            Person_Email="pruefer@example.com",
            Person_HashedPassword="secret",
            Person_Salt="salt",
            Personengruppe_ID=cls.personengruppe,
        )

        cls.veranstalter = Veranstalter.objects.create(
            Veranstalter_Name="Unit Test Veranstalter",
            Veranstalter_Email="orga@example.com",
            Veranstalter_Telefonnummer="12345",
            Veranstalter_Hauptsitz="Berlin",
        )
        cls.veranstalter_detail = Veranstalter.objects.create(
            Veranstalter_Name="Unit Test Veranstalter Detail",
            Veranstalter_Email="detail@example.com",
            Veranstalter_Telefonnummer="67890",
            Veranstalter_Hauptsitz="Hamburg",
        )
        cls.veranstalter_patch = Veranstalter.objects.create(
            Veranstalter_Name="Unit Test Veranstalter Patch",
            Veranstalter_Email="patch@example.com",
            Veranstalter_Telefonnummer="54321",
            Veranstalter_Hauptsitz="Köln",
        )

        cls.kategorie = Veranstaltung_Kategorie.objects.create(Kategorie_Name="Konferenz")
        cls.veranstaltung = Veranstaltung.objects.create(
            Veranstalter_ID=cls.veranstalter,
            Veranstaltung_Kategorie_ID=cls.kategorie,
            Veranstaltung_Beschreibung="Beschreibung",
            Veranstaltung_Webseite="https://example.com",
            Veranstaltung_Sprache="de",
            Veranstaltung_Subevent="Subevent 1",
            Veranstaltung_Name="Unit Test Event",
        )
        cls.veranstaltung_patch = Veranstaltung.objects.create(
            Veranstalter_ID=cls.veranstalter_patch,
            Veranstaltung_Kategorie_ID=cls.kategorie,
            Veranstaltung_Beschreibung="Patch Beschreibung",
            Veranstaltung_Webseite="https://patch.example.com",
            Veranstaltung_Sprache="de",
            Veranstaltung_Subevent="Subevent 2",
            Veranstaltung_Name="Unit Test Event Patch",
        )

        cls.ticket = Veranstaltung_Ticket_Umfang.objects.create(
            Veranstaltung_ID=cls.veranstaltung,
            Ticket_Typ="A-01",
            Aufnahmen=True,
            Aufnahmen_Zensiert=False,
            Umfang_der_Aufnahmen="Foto",
            Kosten=10.0,
        )
        cls.ticket_patch = Veranstaltung_Ticket_Umfang.objects.create(
            Veranstaltung_ID=cls.veranstaltung_patch,
            Ticket_Typ="A-02",
            Aufnahmen=False,
            Aufnahmen_Zensiert=False,
            Umfang_der_Aufnahmen="Video",
            Kosten=20.0,
        )

        cls.status = Einladung_Status.objects.create(
            Status_Titel="Offen",
            Status_Bedeutung="Die Einladung ist offen",
        )
        cls.einladung = Veranstaltung_Einladung.objects.create(
            VIP_anwesend=False,
            Anfragesteller_ID=cls.person,
            Repraesentiert=cls.personengruppe,
            Veranstaltung_ID=cls.veranstaltung,
            Ticket_Typ=cls.ticket.Ticket_Typ,
            Veranstaltung_Grund="Grund",
            Anzahl_Eingeladener_Gäste=5,
            Status=cls.status,
        )
        cls.einladung_patch = Veranstaltung_Einladung.objects.create(
            VIP_anwesend=False,
            Anfragesteller_ID=cls.person,
            Repraesentiert=cls.personengruppe,
            Veranstaltung_ID=cls.veranstaltung_patch,
            Ticket_Typ=cls.ticket_patch.Ticket_Typ,
            Veranstaltung_Grund="Patch Grund",
            Anzahl_Eingeladener_Gäste=3,
            Status=cls.status,
        )

    def test_veranstalter_list_filters(self):
        response = self.client.get("/api/v1/veranstalter/", {"veranstalter_name": "Unit Test Veranstalter"})

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(any(item["Veranstalter_ID"] == self.veranstalter.Veranstalter_ID for item in payload))

    def test_veranstalter_create(self):
        response = self.client.post(
            "/api/v1/veranstalter/",
            {
                "Veranstalter_Name": "Neuer Veranstalter",
                "Veranstalter_Email": "neu@example.com",
                "Veranstalter_Telefonnummer": "999",
                "Veranstalter_Hauptsitz": "Leipzig",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["Veranstalter_Name"], "Neuer Veranstalter")

    def test_veranstalter_detail_get_and_patch(self):
        response = self.client.get(f"/api/v1/veranstalter/{self.veranstalter_detail.Veranstalter_ID}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Veranstalter_Name"], "Unit Test Veranstalter Detail")

        response = self.client.generic(
            "PATCH",
            f"/api/v1/veranstalter/{self.veranstalter_patch.Veranstalter_ID}/",
            data=json.dumps(
                {
                    "Informationen_Geprueft": True,
                    "Geprueft_Von": self.pruefer.Person_ID,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["Informationen_Geprueft"])
        self.assertEqual(response.json()["Geprueft_Von"], self.pruefer.Person_ID)

    def test_veranstaltung_list_create(self):
        response = self.client.post(
            "/api/v1/veranstaltungen/",
            {
                "Veranstalter_ID": self.veranstalter.Veranstalter_ID,
                "Veranstaltung_Name": "Neue Veranstaltung",
                "Veranstaltung_Beschreibung": "Beschreibung",
                "Veranstaltung_Webseite": "https://event.example.com",
                "Veranstaltung_Sprache": "de",
                "Veranstaltung_Subevent": "Unterevent",
                "Veranstaltung_Kategorie_ID": self.kategorie.Veranstaltung_Kategorie_ID,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["Veranstaltung_Name"], "Neue Veranstaltung")

    def test_veranstaltung_detail_get_and_patch(self):
        response = self.client.get(f"/api/v1/veranstaltungen/{self.veranstaltung.Veranstaltung_ID}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Veranstaltung_Name"], "Unit Test Event")

        response = self.client.generic(
            "PATCH",
            f"/api/v1/veranstaltungen/{self.veranstaltung_patch.Veranstaltung_ID}/",
            data=json.dumps(
                {
                    "Informationen_Geprueft": True,
                    "Geprueft_Von": self.pruefer.Person_ID,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["Informationen_Geprueft"])
        self.assertEqual(response.json()["Geprueft_Von"], self.pruefer.Person_ID)

    def test_veranstaltung_ticket_create_and_patch(self):
        response = self.client.post(
            f"/api/v1/veranstaltungen/{self.veranstaltung.Veranstaltung_ID}/tickets",
            {
                "Ticket_Typ": "A-03",
                "Aufnahmen": True,
                "Aufnahmen_Zensiert": False,
                "Umfang_der_Aufnahmen": "Foto",
                "Kosten": 15.5,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["Ticket_Typ"], "A-03")

        response = self.client.generic(
            "PATCH",
            f"/api/v1/veranstaltungen/{self.veranstaltung_patch.Veranstaltung_ID}/tickets/{self.ticket_patch.Ticket_Typ}",
            data=json.dumps(
                {
                    "Informationen_Geprueft": True,
                    "Geprueft_Von": self.pruefer.Person_ID,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["Informationen_Geprueft"])
        self.assertEqual(response.json()["Geprueft_Von"], self.pruefer.Person_ID)

    def test_einladung_list_create(self):
        response = self.client.get(
            "/api/v1/einladungen/",
            {"veranstaltung_id": self.veranstaltung.Veranstaltung_ID},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(any(item["Veranstaltung_Einladung_ID"] == self.einladung.Veranstaltung_Einladung_ID for item in payload))

        response = self.client.post(
            "/api/v1/einladungen/",
            {
                "VIP_anwesend": False,
                "Anfragesteller_ID": self.person.Person_ID,
                "Repraesentiert": self.personengruppe.Personengruppe_ID,
                "Veranstaltung_ID": self.veranstaltung.Veranstaltung_ID,
                "Ticket_Typ": self.ticket.Ticket_Typ,
                "Veranstaltung_Grund": "Neuer Grund",
                "Anzahl_Eingeladener_Gäste": 10,
                "Status": self.status.Status_ID,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["Veranstaltung_Grund"], "Neuer Grund")

    def test_einladung_kommentar_and_entscheidung_create(self):
        kommentar_response = self.client.post(
            f"/api/v1/einladungen/{self.einladung.Veranstaltung_Einladung_ID}/kommentare",
            {
                "Absender_ID": self.person.Person_ID,
                "Kommentar_Inhalt": "Kommentar",
            },
            format="json",
        )

        self.assertEqual(kommentar_response.status_code, 201)
        self.assertEqual(Einladung_Kommentar.objects.count(), 1)

        entscheidung_response = self.client.post(
            f"/api/v1/einladungen/{self.einladung.Veranstaltung_Einladung_ID}/entscheidungen",
            {
                "Personengruppe_ID": self.personengruppe.Personengruppe_ID,
                "Zugesagt_von_Person_ID": self.person.Person_ID,
                "Zugesagt": True,
                "Anmerkung": "Ja",
            },
            format="json",
        )

        self.assertEqual(entscheidung_response.status_code, 201)
        self.assertEqual(Einladung_Entscheidung.objects.count(), 1)

    def test_einladung_detail_get_and_patch(self):
        response = self.client.get(f"/api/v1/einladungen/{self.einladung.Veranstaltung_Einladung_ID}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Veranstaltung_Grund"], "Grund")

        response = self.client.generic(
            "PATCH",
            f"/api/v1/einladungen/{self.einladung_patch.Veranstaltung_Einladung_ID}/",
            data=json.dumps({"VIP_anwesend": True}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["VIP_anwesend"])

    @patch("webserver.uploads.views.upload_blob", return_value="https://storage.example.com/blob/test.docx")
    @patch("webserver.uploads.views.read_doc", return_value={"A-01": "Name der Veranstaltung"})
    def test_docx_upload_view(self, mock_read_doc, mock_upload_blob):
        uploaded_file = SimpleUploadedFile(
            "test.docx",
            b"dummy-docx-content",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        response = self.client.post(
            "/api/v1/upload/docx/",
            {
                "file": uploaded_file,
                "Uploader": self.person.Person_ID,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["Datei_Name"], "test.docx")
        self.assertEqual(response.json()["Datei_Pfad"], "https://storage.example.com/blob/test.docx")
        mock_upload_blob.assert_called_once()
        mock_read_doc.assert_called_once()

    def test_validate_datei_json_reports_problems(self):
        datei = Datei.objects.create(
            Datei_Name="input.json",
            Datei_Pfad="https://storage.example.com/blob/input.json",
            Datei_Typ="application/json",
            Datei_Inhalt={
                "veranstalter_name": "Mapped Name",
                "email": "ungueltige-email",
                "extra_key": "unused",
            },
            Uploader=self.person,
            Datei_Inhalt_Benoetigt=True,
        )

        response = self.client.post(
            "/api/v1/upload/docx/validate-model/",
            {
                "Datei_ID": datei.Datei_ID,
                "Zielmodell": "veranstalter",
                "Anlegen_Bei_Kompatibilitaet": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        report = payload["validierungsreport"]

        self.assertFalse(report["kompatibel"])
        self.assertIn("Veranstalter_Hauptsitz", report["fehlende_pflichtfelder"])
        self.assertIn("extra_key", report["ungenutzte_json_schluessel"])
        self.assertIn("Veranstalter_Email", report["feldfehler"])
        self.assertIsNone(payload["angelegter_eintrag"])

    def test_validate_datei_json_can_create_entry(self):
        initial_count = Veranstalter.objects.count()
        datei = Datei.objects.create(
            Datei_Name="input-valid.json",
            Datei_Pfad="https://storage.example.com/blob/input-valid.json",
            Datei_Typ="application/json",
            Datei_Inhalt={
                "veranstalter_name": "Mapped Name",
                "email": "mapped@example.com",
                "hauptsitz": "Frankfurt",
            },
            Uploader=self.person,
            Datei_Inhalt_Benoetigt=True,
        )

        response = self.client.post(
            "/api/v1/upload/docx/validate-model/",
            {
                "Datei_ID": datei.Datei_ID,
                "Zielmodell": "veranstalter",
                "Anlegen_Bei_Kompatibilitaet": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload["validierungsreport"]["kompatibel"])
        self.assertIsNotNone(payload["angelegter_eintrag"])
        self.assertEqual(payload["angelegter_eintrag"]["modell"], "Veranstalter")
        self.assertEqual(Veranstalter.objects.count(), initial_count + 1)

        datei.refresh_from_db()
        self.assertFalse(datei.Datei_Inhalt_Benoetigt)

    def test_validate_datei_json_multiple_models_with_invitation_derivations(self):
        datei = Datei.objects.create(
            Datei_Name="input-invitation.json",
            Datei_Pfad="https://storage.example.com/blob/input-invitation.json",
            Datei_Typ="application/json",
            Datei_Inhalt={
                "veranstaltung_name": "Unit Test Event",
                "vip_anwesend": False,
                "personengruppe_id": self.personengruppe.Personengruppe_ID,
                "ticket_typ": self.ticket.Ticket_Typ,
                "grund": "Einladung aus Dokument",
                "anzahl_eingeladener_gaeste": 25,
            },
            Uploader=self.person,
            Datei_Inhalt_Benoetigt=True,
        )

        response = self.client.post(
            "/api/v1/upload/docx/validate-model/",
            {
                "Datei_ID": datei.Datei_ID,
                "Zielmodelle": ["veranstaltung", "einladung"],
                "Anlegen_Bei_Kompatibilitaet": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["validierungsreport"]["zielmodelle"], ["veranstaltung", "einladung"])
        self.assertFalse(payload["validierungsreport"]["model_reports"]["veranstaltung"]["kompatibel"])
        self.assertTrue(payload["validierungsreport"]["model_reports"]["einladung"]["kompatibel"])
        self.assertEqual(
            payload["validierungsreport"]["model_reports"]["einladung"]["zuordnung_json_zu_modelfeld"]["Anfragesteller_ID"],
            self.person.Person_ID,
        )
        self.assertIn("Veranstaltung_ID", payload["validierungsreport"]["model_reports"]["einladung"]["abgeleitete_felder"])

    def test_update_datei_json_endpoint(self):
        datei = Datei.objects.create(
            Datei_Name="input-update.json",
            Datei_Pfad="https://storage.example.com/blob/input-update.json",
            Datei_Typ="application/json",
            Datei_Inhalt={"old_key": "old_value"},
            Uploader=self.person,
            Datei_Inhalt_Benoetigt=True,
        )

        response = self.client.post(
            "/api/v1/upload/docx/update-json/",
            {
                "Datei_ID": datei.Datei_ID,
                "Datei_Inhalt": {"veranstalter_name": "Neue JSON"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["datei"]["Datei_Inhalt_Benoetigt"])
        self.assertIn("Bitte validierungs Endpoint erneut ausfuehren", payload["hinweis"])

        datei.refresh_from_db()
        self.assertEqual(datei.Datei_Inhalt, {"veranstalter_name": "Neue JSON"})
        self.assertTrue(datei.Datei_Inhalt_Benoetigt)
