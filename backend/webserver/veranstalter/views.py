from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework import status

from webserver.api import serializers
from webserver.models import Veranstalter


@extend_schema_view(
    get=extend_schema(
        operation_id='veranstalter_list_filtered',
        summary='Veranstalter auflisten und filtern',
        responses=serializers.VeranstalterListSerializer(many=True),
        parameters=[
            OpenApiParameter(
                name='veranstalter_name',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Veranstalter nach Name',
            ),
            OpenApiParameter(
                name='veranstalter_hauptsitz',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Filtert Veranstalter nach Hauptsitz',
            ),
        ],
    ),
    post=extend_schema(
        operation_id='veranstalter_create',
        summary='Veranstalter anlegen',
        request=serializers.VeranstalterCreateSerializer(),
        responses=serializers.VeranstalterDetailSerializer(),
    ),
)
class VeranstalterListCreateView(GenericAPIView):

    queryset = Veranstalter.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.VeranstalterCreateSerializer
        return serializers.VeranstalterListSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        veranstalter_name = self.request.query_params.get('veranstalter_name')
        if veranstalter_name:
            queryset = queryset.filter(Veranstalter_Name__icontains=veranstalter_name)

        veranstalter_hauptsitz = self.request.query_params.get('veranstalter_hauptsitz')
        if veranstalter_hauptsitz:
            queryset = queryset.filter(Veranstalter_Hauptsitz__icontains=veranstalter_hauptsitz)

        return queryset

    def get(self, request, *args, **kwargs):
        serializer = serializers.VeranstalterListSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        veranstalter = serializer.save()
        response_serializer = serializers.VeranstalterDetailSerializer(veranstalter)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    get=extend_schema(
        operation_id='veranstalter_detail',
        summary='Veranstalter anzeigen',
        responses=serializers.VeranstalterDetailSerializer(),
        parameters=[
            OpenApiParameter(
                name='veranstalter_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID des spezifischen Veranstalters',
            ),
        ],
    ),
    patch=extend_schema(
        operation_id='veranstalter_partial_update',
        summary='Veranstalter anpassen',
        request=serializers.VeranstalterUpdateSerializer(),
        responses=serializers.VeranstalterDetailSerializer(),
        parameters=[
            OpenApiParameter(
                name='veranstalter_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                required=True,
                description='ID des spezifischen Veranstalters',
            ),
        ],
    ),
)
class VeranstalterDetailView(GenericAPIView):
    queryset = Veranstalter.objects.all()
    lookup_field = 'Veranstalter_ID'
    lookup_url_kwarg = 'veranstalter_id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return serializers.VeranstalterUpdateSerializer
        return serializers.VeranstalterDetailSerializer

    def get(self, request, veranstalter_id, *args, **kwargs):
        veranstalter = self.get_object()
        serializer = serializers.VeranstalterDetailSerializer(veranstalter)
        return Response(serializer.data)

    def patch(self, request, veranstalter_id, *args, **kwargs):
        veranstalter = self.get_object()
        serializer = self.get_serializer(veranstalter, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        veranstalter = serializer.save()
        response_serializer = serializers.VeranstalterDetailSerializer(veranstalter)
        return Response(response_serializer.data)
