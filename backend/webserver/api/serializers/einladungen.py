from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from webserver.models import Veranstaltung_Einladung, Veranstaltung_Ticket_Umfang

from .common import Veranstaltung_Ticket_UmfangSerializer


class Veranstaltung_EinladungSerializer(serializers.ModelSerializer):
    Veranstaltung_Ticket_Umfang = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Veranstaltung_Einladung
        fields = [
            "Veranstaltung_Einladung_ID",
            "VIP_anwesend",
            "Anfragesteller_ID",
            "Repraesentiert",
            "Veranstaltung_ID",
            "Ticket_Typ",
            "Veranstaltung_Grund",
            "Anzahl_Eingeladener_Gäste",
            "Einladung_Datum",
            "Status",
            "Veranstaltung_Ticket_Umfang",
        ]
        read_only_fields = [
            "Veranstaltung_Einladung_ID",
            "Einladung_Datum",
            "Veranstaltung_Ticket_Umfang",
        ]

    @extend_schema_field(Veranstaltung_Ticket_UmfangSerializer)
    def get_Veranstaltung_Ticket_Umfang(self, obj):
        ticket_umfang = Veranstaltung_Ticket_Umfang.objects.filter(
            Veranstaltung_ID=obj.Veranstaltung_ID,
            Ticket_Typ=obj.Ticket_Typ,
        ).first()

        if not ticket_umfang:
            return None

        return Veranstaltung_Ticket_UmfangSerializer(ticket_umfang, context=self.context).data

    def validate(self, attrs):
        veranstaltung = attrs.get("Veranstaltung_ID", getattr(self.instance, "Veranstaltung_ID", None))
        ticket_typ = attrs.get("Ticket_Typ", getattr(self.instance, "Ticket_Typ", None))

        if veranstaltung and ticket_typ:
            exists = Veranstaltung_Ticket_Umfang.objects.filter(
                Veranstaltung_ID=veranstaltung,
                Ticket_Typ=ticket_typ,
            ).exists()
            if not exists:
                raise serializers.ValidationError(
                    {"Ticket_Typ": "Der Ticket-Typ existiert nicht fuer diese Veranstaltung."}
                )

        return attrs


class Veranstaltung_EinladungCreateSerializer(serializers.ModelSerializer):
    Veranstaltung_Ticket_Umfang = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Veranstaltung_Einladung
        fields = [
            "Veranstaltung_Einladung_ID",
            "VIP_anwesend",
            "Anfragesteller_ID",
            "Repraesentiert",
            "Veranstaltung_ID",
            "Ticket_Typ",
            "Veranstaltung_Grund",
            "Anzahl_Eingeladener_Gäste",
            "Einladung_Datum",
            "Status",
            "Veranstaltung_Ticket_Umfang",
        ]
        read_only_fields = [
            "Veranstaltung_Einladung_ID",
            "Einladung_Datum",
            "Veranstaltung_Ticket_Umfang",
        ]

    @extend_schema_field(Veranstaltung_Ticket_UmfangSerializer)
    def get_Veranstaltung_Ticket_Umfang(self, obj):
        ticket_umfang = Veranstaltung_Ticket_Umfang.objects.filter(
            Veranstaltung_ID=obj.Veranstaltung_ID,
            Ticket_Typ=obj.Ticket_Typ,
        ).first()

        if not ticket_umfang:
            return None

        return Veranstaltung_Ticket_UmfangSerializer(ticket_umfang, context=self.context).data

    def validate(self, attrs):
        veranstaltung = attrs.get("Veranstaltung_ID", getattr(self.instance, "Veranstaltung_ID", None))
        ticket_typ = attrs.get("Ticket_Typ", getattr(self.instance, "Ticket_Typ", None))

        if veranstaltung and ticket_typ:
            exists = Veranstaltung_Ticket_Umfang.objects.filter(
                Veranstaltung_ID=veranstaltung,
                Ticket_Typ=ticket_typ,
            ).exists()
            if not exists:
                raise serializers.ValidationError(
                    {"Ticket_Typ": "Der Ticket-Typ existiert nicht fuer diese Veranstaltung."}
                )

        return attrs
