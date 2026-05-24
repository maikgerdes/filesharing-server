from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from webserver.api import serializers
from webserver.models import Veranstaltung_Einladung, Einladung_Kommentar, Einladung_Entscheidung
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status


@extend_schema_view(
    get=extend_schema(
        operation_id='einladungen_list_filtered',
        summary='Einladungen auflisten und filtern',
        description=(
            'Gibt eine Liste von Einladungen zurück.'
        ),
        responses=serializers.Veranstaltung_EinladungSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name='veranstaltung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Einladungen nach der ID der Veranstaltung, zu welcher eingeladen wurde',
            ),
            OpenApiParameter(
                name='anfragesteller_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Einladungen nach der ID des Anfragestellers',
            ),
            OpenApiParameter(
                name='personengruppe_anfragesteller_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Einladungen nach der ID der jeweiligen Personengruppe des Anfragestellers',
            ),
            OpenApiParameter(
                name='datum',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert nach dem Einladungsdatum. Formate: exact:YYYY-MM-DD, lt:YYYY-MM-DD, gt:YYYY-MM-DD',
            ),
        ],
        examples=[
            OpenApiExample(
                'Filter nach Veranstaltung',
                value={
                    'curl': "curl -X GET 'https://api.example.com/api/v1/einladungen?veranstaltung_id=12'"
                },
            ),
            OpenApiExample(
                'Datumsfilter exact',
                value={
                    'curl': "curl -X GET 'https://api.example.com/api/v1/einladungen?datum=exact:2026-05-24'"
                },
            ),
            OpenApiExample(
                'Kombinierter Filter',
                value={
                    'curl': "curl -X GET 'https://api.example.com/api/v1/einladungen?anfragesteller_id=5&datum=lt:2026-06-01'"
                },
            ),
            OpenApiExample(
                'Beispiel-Response (Liste)',
                value=[
                    {
                        'Veranstaltung_Einladung_ID': 34,
                        'Veranstaltung_ID': 12,
                        'Anfragesteller_ID': 5,
                        'Einladung_Datum': '2026-06-01',
                        'Betreff': 'Einladung zur Konferenz',
                        'Status': 'Offen'
                    }
                ],
                response_only=True,
            ),
        ],
    ),
    post=extend_schema(
        operation_id='einladung_create',
        summary='Einladung anlegen',
        description=(
            'Legt eine neue Einladung an.'
        ),
        request=serializers.Veranstaltung_EinladungCreateSerializer(),
        responses=serializers.Veranstaltung_EinladungSerializer(),
        examples=[
            OpenApiExample(
                'Beispiel-Anfrage',
                value={
                    'Veranstaltung_ID': 12,
                    'Anfragesteller_ID': 5,
                    'Einladung_Datum': '2026-06-01',
                    'Betreff': 'Einladung zur Konferenz',
                    'Beschreibung': 'Wir möchten Sie herzlich einladen.'
                },
                request_only=True,
            ),
            OpenApiExample(
                'Beispiel-Response',
                value={
                    'Veranstaltung_Einladung_ID': 34,
                    'Veranstaltung_ID': 12,
                    'Anfragesteller_ID': 5,
                    'Einladung_Datum': '2026-06-01',
                    'Betreff': 'Einladung zur Konferenz',
                    'Beschreibung': 'Wir möchten Sie herzlich einladen.',
                    'Status': 'Offen'
                },
                response_only=True,
            ),
        ],
    ),
)
class EinladungListCreateView(GenericAPIView):
    queryset = Veranstaltung_Einladung.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.Veranstaltung_EinladungCreateSerializer
        return serializers.Veranstaltung_EinladungSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        veranstaltung_id = self.request.query_params.get('veranstaltung_id')
        if veranstaltung_id:
            queryset = queryset.filter(Veranstaltung_ID=veranstaltung_id)

        anfragesteller_id = self.request.query_params.get('anfragesteller_id')
        if anfragesteller_id:
            queryset = queryset.filter(Anfragesteller_ID=anfragesteller_id)

        personengruppe_anfragesteller_id = self.request.query_params.get('personengruppe_anfragesteller_id')
        if personengruppe_anfragesteller_id:
            queryset = queryset.filter(Repraesentiert=personengruppe_anfragesteller_id)

        datum = self.request.query_params.get('datum')
        if datum:
            operator = 'exact'
            datum_wert = datum

            if ':' in datum:
                operator, datum_wert = datum.split(':', 1)
                operator = operator.strip().lower()
                datum_wert = datum_wert.strip()

            datum_lookup_map = {
                'exact': 'Einladung_Datum__date',
                'lt': 'Einladung_Datum__date__lt',
                'gt': 'Einladung_Datum__date__gt',
            }

            lookup = datum_lookup_map.get(operator)
            if lookup:
                queryset = queryset.filter(**{lookup: datum_wert})

        return queryset

    def get(self, request, *args, **kwargs):
        serializer = serializers.Veranstaltung_EinladungSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        einladung = serializer.save()
        response_serializer = serializers.Veranstaltung_EinladungSerializer(einladung)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        operation_id='einladung_kommentar_create',
        summary='Kommentar zu Einladung anlegen',
        description=(
            'Erstellt einen Kommentar zur angegebenen Einladung.\n\nParameter:\n'
        ),
        request=serializers.Einladung_KommentarCreateNestedSerializer(),
        responses=serializers.Einladung_KommentarSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der Einladung, zu der der Kommentar gehört',
            ),
        ],
        examples=[
            OpenApiExample(
                'Root-Kommentar',
                value={
                    'Parent_ID': None,
                    'Absender_ID': 2,
                    'Kommentar_Inhalt': 'Ich habe die Einladung geprüft und lasse hier Feedback da.',
                },
                request_only=True,
            ),
            OpenApiExample(
                'Antwort auf Kommentar',
                value={
                    'Parent_ID': 5,
                    'Absender_ID': 2,
                    'Kommentar_Inhalt': 'Danke, ich habe es angepasst.',
                },
                request_only=True,
            ),
            OpenApiExample(
                'cURL-Beispiel',
                value={
                    'curl': "curl -X POST 'https://api.example.com/api/v1/einladungen/34/kommentare/' -H 'Content-Type: application/json' -d '{\"Parent_ID\": null, \"Absender_ID\": 2, \"Kommentar_Inhalt\": \"Sieht gut aus.\"}'"
                },
            ),
            OpenApiExample(
                'Beispiel-Response (Kommentar)',
                value={
                    'Einladung_Kommentar_ID': 78,
                    'Veranstaltung_Einladung_ID': 34,
                    'Parent_ID': None,
                    'Absender_ID': 2,
                    'Kommentar_Inhalt': 'Sieht gut aus.',
                    'Erstellt_Am': '2026-05-24T12:34:56Z'
                },
                response_only=True,
            ),
        ],
    ),
)
class EinladungKommentarCreateView(GenericAPIView):
    queryset = Einladung_Kommentar.objects.all()
    serializer_class = serializers.Einladung_KommentarCreateNestedSerializer

    def post(self, request, einladung_id, *args, **kwargs):
        einladung = get_object_or_404(Veranstaltung_Einladung, Veranstaltung_Einladung_ID=einladung_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        kommentar = serializer.save(Veranstaltung_Einladung_ID=einladung)
        response_serializer = serializers.Einladung_KommentarSerializer(kommentar)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        operation_id='einladung_entscheidung_create',
        summary='Entscheidung zu Einladung anlegen',
        description=(
            'Legt eine Entscheidung (z. B. Annahme/Ablehnung) für eine Einladung an.\n\n'
        ),
        request=serializers.Einladung_EntscheidungCreateNestedSerializer(),
        responses=serializers.Einladung_EntscheidungSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der Einladung, zu der die Entscheidung gehört',
            ),
        ],
        examples=[
            OpenApiExample(
                'Beispiel-Anfrage',
                value={
                    'Entscheidung': 'angenommen',
                    'Entscheidung_Datum': '2026-06-02',
                    'Entscheider_ID': 2
                },
                request_only=True,
            ),
            OpenApiExample(
                'cURL-Beispiel',
                value={
                    'curl': "curl -X POST 'https://api.example.com/api/v1/einladungen/34/entscheidungen/' -H 'Content-Type: application/json' -d '{\"Entscheidung\": \"angenommen\", \"Entscheidung_Datum\": \"2026-06-02\", \"Entscheider_ID\": 2}'"
                },
            ),
            OpenApiExample(
                'Beispiel-Response (Entscheidung)',
                value={
                    'Einladung_Entscheidung_ID': 21,
                    'Veranstaltung_Einladung_ID': 34,
                    'Entscheidung': 'angenommen',
                    'Entscheidung_Datum': '2026-06-02',
                    'Entscheider_ID': 2
                },
                response_only=True,
            ),
        ],
    ),
)
class EinladungEntscheidungCreateView(GenericAPIView):
    queryset = Einladung_Entscheidung.objects.all()
    serializer_class = serializers.Einladung_EntscheidungCreateNestedSerializer

    def post(self, request, einladung_id, *args, **kwargs):
        einladung = get_object_or_404(Veranstaltung_Einladung, Veranstaltung_Einladung_ID=einladung_id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        entscheidung = serializer.save(Veranstaltung_Einladung_ID=einladung)
        response_serializer = serializers.Einladung_EntscheidungSerializer(entscheidung)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        operation_id='einladung_detail',
        summary='Einladung anzeigen',
        description=(
            'Gibt die Detailinformationen einer einzelnen Einladung zurück.\n\n'
        ),
        responses=serializers.Veranstaltung_EinladungSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der spezifischen Einladung',
            ),
        ],
        examples=[
            OpenApiExample(
                'Beispiel-URL',
                value={
                    'curl': "curl -X GET 'https://api.example.com/api/v1/einladungen/34/'"
                },
            ),
            OpenApiExample(
                'Beispiel-Response (Detail)',
                value={
                    'Veranstaltung_Einladung_ID': 34,
                    'Veranstaltung_ID': 12,
                    'Anfragesteller_ID': 5,
                    'Einladung_Datum': '2026-06-01',
                    'Betreff': 'Einladung zur Konferenz',
                    'Beschreibung': 'Wir möchten Sie herzlich einladen.',
                    'Status': 'Offen'
                },
                response_only=True,
            ),
        ],
    ),
    patch=extend_schema(
        operation_id='einladung_partial_update',
        summary='Einladung anpassen',
        description=(
            'Führt ein partielles Update an einer bestehenden Einladung durch.\n'
        ),
        request=serializers.Veranstaltung_EinladungCreateSerializer(),
        responses=serializers.Veranstaltung_EinladungSerializer(),
        parameters=[
            OpenApiParameter(
                name='einladung_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID der spezifischen Einladung',
            ),
        ],
        examples=[
            OpenApiExample(
                'Patch-Beispiel',
                value={
                    'curl': "curl -X PATCH 'https://api.example.com/api/v1/einladungen/34/' -H 'Content-Type: application/json' -d '{\"Betreff\": \"Neuer Betreff\"}'"
                },
                request_only=True,
            ),
            OpenApiExample(
                'Beispiel-Response (Patch)',
                value={
                    'Veranstaltung_Einladung_ID': 34,
                    'Veranstaltung_ID': 12,
                    'Anfragesteller_ID': 5,
                    'Einladung_Datum': '2026-06-01',
                    'Betreff': 'Neuer Betreff',
                    'Beschreibung': 'Wir möchten Sie herzlich einladen.',
                    'Status': 'Offen'
                },
                response_only=True,
            ),
        ],
    ),
)
class EinladungDetailView(GenericAPIView):
    queryset = Veranstaltung_Einladung.objects.all()
    lookup_field = 'Veranstaltung_Einladung_ID'
    lookup_url_kwarg = 'einladung_id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.Veranstaltung_EinladungCreateSerializer
        return serializers.Veranstaltung_EinladungSerializer

    def get(self, request, einladung_id, *args, **kwargs):
        einladung = self.get_object()
        serializer = serializers.Veranstaltung_EinladungSerializer(einladung)
        return Response(serializer.data)

    def patch(self, request, einladung_id, *args, **kwargs):
        einladung = self.get_object()
        serializer = self.get_serializer(einladung, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        einladung = serializer.save()
        response_serializer = serializers.Veranstaltung_EinladungSerializer(einladung)
        return Response(response_serializer.data)
