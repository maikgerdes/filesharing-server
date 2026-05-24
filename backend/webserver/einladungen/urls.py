from django.urls import path

from .views import (
    EinladungDetailView,
    EinladungEntscheidungCreateView,
    EinladungKommentarCreateView,
    EinladungListCreateView,
)


urlpatterns = [
    path('', EinladungListCreateView.as_view()),
    path('<int:einladung_id>/kommentare', EinladungKommentarCreateView.as_view()),
    path('<int:einladung_id>/entscheidungen', EinladungEntscheidungCreateView.as_view()),
    path('<int:einladung_id>/', EinladungDetailView.as_view()),
]
