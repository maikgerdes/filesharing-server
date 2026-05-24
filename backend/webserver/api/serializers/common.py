from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

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


class InformationenGeprueftMixin:
    def validate(self, attrs):
        attrs = super().validate(attrs)
        informationen_geprueft = attrs.get(
            "Informationen_Geprueft", getattr(self.instance, "Informationen_Geprueft", False)
        )
        geprueft_von = attrs.get("Geprueft_Von", getattr(self.instance, "Geprueft_Von", None))

        if informationen_geprueft and not geprueft_von:
            raise serializers.ValidationError(
                {
                    "Geprueft_Von": "Wenn Informationen_Geprueft true ist, muss Geprueft_Von gesetzt sein."
                }
            )

        if geprueft_von and not informationen_geprueft:
            raise serializers.ValidationError(
                {
                    "Informationen_Geprueft": "Wenn Geprueft_Von gesetzt ist, muss Informationen_Geprueft true sein."
                }
            )

        return attrs


class Veranstaltung_Ticket_UmfangSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung_Ticket_Umfang
        fields = [
            "Veranstaltung_ID",
            "Ticket_Typ",
            "Aufnahmen",
            "Aufnahmen_Zensiert",
            "Umfang_der_Aufnahmen",
            "Kosten",
            "Informationen_Geprueft",
            "Geprueft_Von",
        ]


class Veranstaltung_Ticket_UmfangCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung_Ticket_Umfang
        fields = [
            "Ticket_Typ",
            "Aufnahmen",
            "Aufnahmen_Zensiert",
            "Umfang_der_Aufnahmen",
            "Kosten",
        ]


class Veranstaltung_Ticket_UmfangUpdateSerializer(InformationenGeprueftMixin, serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung_Ticket_Umfang
        fields = [
            "Aufnahmen",
            "Aufnahmen_Zensiert",
            "Umfang_der_Aufnahmen",
            "Kosten",
            "Informationen_Geprueft",
            "Geprueft_Von",
        ]


class Veranstaltung_Ticket_UmfangCreateNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung_Ticket_Umfang
        fields = [
            "Ticket_Typ",
            "Aufnahmen",
            "Aufnahmen_Zensiert",
            "Umfang_der_Aufnahmen",
            "Kosten",
        ]


class Veranstaltung_Ticket_UmfangNestedUpdateSerializer(InformationenGeprueftMixin, serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung_Ticket_Umfang
        fields = [
            "Aufnahmen",
            "Aufnahmen_Zensiert",
            "Umfang_der_Aufnahmen",
            "Kosten",
            "Informationen_Geprueft",
            "Geprueft_Von",
        ]


class PersonengruppeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Personengruppe
        fields = "__all__"


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


class DateiUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    Uploader = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())


class DateiModelValidationSerializer(serializers.Serializer):
    Datei_ID = serializers.PrimaryKeyRelatedField(queryset=Datei.objects.all())
    Zielmodell = serializers.ChoiceField(choices=["veranstalter", "veranstaltung", "einladung"], required=False)
    Zielmodelle = serializers.ListField(
        child=serializers.ChoiceField(choices=["veranstalter", "veranstaltung", "einladung"]),
        required=False,
        allow_empty=False,
    )
    Anlegen_Bei_Kompatibilitaet = serializers.BooleanField(required=False, default=False)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not attrs.get("Zielmodell") and not attrs.get("Zielmodelle"):
            raise serializers.ValidationError({"Zielmodell": "Mindestens ein Zielmodell muss angegeben werden."})
        return attrs


class DateiJsonUpdateSerializer(serializers.Serializer):
    Datei_ID = serializers.PrimaryKeyRelatedField(queryset=Datei.objects.all())
    Datei_Inhalt = serializers.DictField()


class DateiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datei
        fields = "__all__"


class Einladung_StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einladung_Status
        fields = "__all__"


class Einladung_EntscheidungSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einladung_Entscheidung
        fields = [
            "Veranstaltung_Einladung_ID",
            "Personengruppe_ID",
            "Zugesagt_von_Person_ID",
            "Zugesagt",
            "Anmerkung",
            "Entscheidungs_Datum",
        ]


class Einladung_EntscheidungCreateNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einladung_Entscheidung
        fields = [
            "Personengruppe_ID",
            "Zugesagt_von_Person_ID",
            "Zugesagt",
            "Anmerkung",
        ]


class Einladung_KommentarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einladung_Kommentar
        fields = "__all__"


class Einladung_KommentarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einladung_Kommentar
        fields = ["Parent_ID", "Absender_ID", "Kommentar_Inhalt"]
        extra_kwargs = {"Parent_ID": {"required": False, "allow_null": True}}


class Einladung_KommentarCreateNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Einladung_Kommentar
        fields = ["Parent_ID", "Absender_ID", "Kommentar_Inhalt"]
        extra_kwargs = {"Parent_ID": {"required": False, "allow_null": True}}


class Veranstaltung_KategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Veranstaltung_Kategorie
        fields = ["Veranstaltung_Kategorie_ID", "Kategorie_Name"]
