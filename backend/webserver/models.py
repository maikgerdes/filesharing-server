from django.db import models

class Veranstalter(models.Model):
    Veranstalter_ID = models.AutoField(primary_key=True)
    Veranstalter_Name = models.CharField(max_length=150, null=False)
    Veranstalter_Email = models.EmailField(null=True)
    Veranstalter_Telefonnummer = models.CharField(max_length=100, null=True)
    Veranstalter_Hauptsitz = models.CharField(max_length=100, null=False)
    Informationen_Geprueft = models.BooleanField(default=False)
    Geprueft_Von = models.ForeignKey('Person', on_delete=models.CASCADE, null=True, blank=True)

class Veranstaltung_Kategorie(models.Model):
    Veranstaltung_Kategorie_ID = models.AutoField(primary_key=True)
    Kategorie_Name = models.CharField(max_length=150, null=False)

class Veranstaltung(models.Model):
    Veranstaltung_ID = models.AutoField(primary_key=True)
    Veranstalter_ID = models.ForeignKey(
        Veranstalter, 
        on_delete=models.CASCADE,
        related_name='Veranstaltungen'
        )
    Veranstaltung_Kategorie_ID = models.ForeignKey(Veranstaltung_Kategorie, on_delete=models.CASCADE)
    Veranstaltung_Beschreibung = models.TextField(null=False)
    Veranstaltung_Webseite = models.CharField(max_length=100, null=False)
    Veranstaltung_Sprache = models.CharField(max_length=50, null=False)
    Veranstaltung_Subevent = models.CharField(max_length=50)
    Veranstaltung_Name = models.CharField(max_length=150, null=False)
    Informationen_Geprueft = models.BooleanField(default=False)
    Geprueft_Von = models.ForeignKey('Person', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Veranstaltung_Name', 'Veranstaltung_Subevent'], name='Veranstaltung und Subevent')
        ]

class Personengruppe(models.Model):
    Personengruppe_ID = models.AutoField(primary_key=True)
    Personengruppe_Name = models.CharField(max_length=150, null=False)

class Person(models.Model):
    Person_ID = models.AutoField(primary_key=True)
    Vorname = models.CharField(max_length=150, null=False)
    Nachname = models.CharField(max_length=150, null=False)
    Person_Email = models.EmailField(null=False)
    Person_HashedPassword = models.CharField(max_length=150, null=False)
    Person_Salt = models.CharField(max_length=150, null=False)
    Personengruppe_ID = models.ForeignKey(Personengruppe, on_delete=models.CASCADE)

class Veranstaltung_Ticket_Umfang(models.Model):
    Veranstaltung_ID = models.ForeignKey(
        Veranstaltung, 
        on_delete=models.CASCADE,
        related_name='Ticket_Arten'
        )
    Ticket_Typ = models.CharField(max_length=150, null=False)
    pk = models.CompositePrimaryKey("Veranstaltung_ID", "Ticket_Typ")
    Aufnahmen = models.BooleanField(null=False)
    Aufnahmen_Zensiert = models.BooleanField(null=False)
    Umfang_der_Aufnahmen = models.TextField(null=False)
    Kosten = models.FloatField(null=False)
    Informationen_Geprueft = models.BooleanField(default=False)
    Geprueft_Von = models.ForeignKey('Person', on_delete=models.CASCADE, null=True, blank=True)

class Einladung_Status(models.Model):
    Status_ID = models.AutoField(primary_key=True)
    Status_Titel = models.CharField(max_length=100, null=False)
    Status_Bedeutung = models.TextField(null=False)

    class Meta:
        db_table = 'webserver_status'

class Veranstaltung_Einladung(models.Model):
    Veranstaltung_Einladung_ID = models.AutoField(primary_key=True)
    VIP_anwesend = models.BooleanField(null=False)
    Anfragesteller_ID = models.ForeignKey(Person, on_delete=models.CASCADE)
    Repraesentiert = models.ForeignKey(Personengruppe, on_delete=models.CASCADE)
    Veranstaltung_ID = models.ForeignKey(
        Veranstaltung, 
        on_delete=models.CASCADE,
        related_name='Einladungen'
        )
    Ticket_Typ = models.CharField(max_length=150, null=False)
    Veranstaltung_Ticket_Umfang_pk = models.ForeignObject(
        Veranstaltung_Ticket_Umfang, 
        on_delete=models.CASCADE,
        from_fields=("Veranstaltung_ID", "Ticket_Typ"),
        to_fields=("Veranstaltung_ID", "Ticket_Typ"))
    Veranstaltung_Grund = models.TextField(null=False)
    Anzahl_Eingeladener_Gäste = models.IntegerField(null=False)
    Einladung_Datum = models.DateTimeField(auto_now_add=True)
    Status = models.ForeignKey(Einladung_Status, on_delete=models.CASCADE)

class Einladung_Entscheidung(models.Model):
    Veranstaltung_Einladung_ID = models.ForeignKey(Veranstaltung_Einladung, on_delete=models.CASCADE)
    Personengruppe_ID = models.ForeignKey(Personengruppe, on_delete=models.CASCADE)
    pk = models.CompositePrimaryKey("Veranstaltung_Einladung_ID", "Personengruppe_ID")
    Zugesagt_von_Person_ID = models.ForeignKey(Person, on_delete=models.CASCADE)
    Zugesagt = models.BooleanField(null=False)
    Anmerkung = models.TextField(null=False)
    Entscheidungs_Datum = models.DateTimeField(auto_now_add=True)

class Einladung_Kommentar(models.Model):
    Veranstaltung_Einladung_ID = models.ForeignKey(Veranstaltung_Einladung, on_delete=models.CASCADE)
    Kommentar_ID = models.AutoField(primary_key=True)
    Parent_ID = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    Absender_ID =  models.ForeignKey(Person, on_delete=models.CASCADE) 
    Kommentar_Inhalt = models.TextField(null=False)
    Verfassungsdatum = models.DateTimeField(auto_now_add=True)
    
class Datei(models.Model):
    Datei_ID = models.AutoField(primary_key=True)
    Datei_Name = models.CharField(max_length=150, null=False)
    Datei_Pfad = models.CharField(max_length=100, null=False)
    Datei_Typ = models.CharField(max_length=100, null=False)
    Datei_Inhalt = models.JSONField()
    Uploaddatum = models.DateTimeField(auto_now_add=True)
    Uploader = models.ForeignKey(Person, on_delete=models.CASCADE)
    Datei_Inhalt_Benoetigt = models.BooleanField()
