from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from django.apps import apps

from webserver.api import serializers as api_serializers


TARGET_SERIALIZER_MAP = {
    "veranstalter": api_serializers.VeranstalterCreateSerializer,
    "veranstaltung": api_serializers.VeranstaltungCreateSerializer,
    "einladung": api_serializers.Veranstaltung_EinladungCreateSerializer,
}


def _is_unanswered(value: Any) -> bool:
    return value is None or (isinstance(value, str) and value.strip() == "")


def _mapping_file_path() -> Path:
    return Path(__file__).with_name("json_model_field_mapping.yml")


def _load_mapping_config() -> dict[str, Any]:
    with _mapping_file_path().open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def _get_django_model(model_path: str):
    parts = model_path.split(".")
    if len(parts) < 2:
        raise LookupError(f"Ungueltiger Modelpfad: {model_path}")

    app_label = parts[0]
    model_name = parts[-1]
    return apps.get_model(app_label, model_name)


def _first_payload_value(payload: dict[str, Any], keys: list[str]) -> tuple[str | None, Any | None]:
    lowered_payload_keys = {key.lower(): key for key in payload.keys()}
    for candidate_key in keys:
        if candidate_key in payload:
            return candidate_key, payload[candidate_key]
        lowered_key = candidate_key.lower()
        if lowered_key in lowered_payload_keys:
            original_key = lowered_payload_keys[lowered_key]
            return original_key, payload[original_key]
    return None, None


def _normalize_payload_with_mapping(
    payload: dict[str, Any],
    field_mappings: dict[str, Any],
) -> tuple[dict[str, Any], list[str], dict[str, str], list[dict[str, Any]]]:
    normalized_payload: dict[str, Any] = {}
    key_source_by_model_field: dict[str, str] = {}
    collisions: list[dict[str, Any]] = []
    used_keys: set[str] = set()

    for model_field, mapping_config in field_mappings.items():
        accepted_keys = list(mapping_config.get("accepted_json_keys") or [])
        if model_field not in accepted_keys:
            accepted_keys.insert(0, model_field)

        matched_keys: list[str] = []
        seen_matches: set[str] = set()
        for accepted_key in accepted_keys:
            if accepted_key in payload and accepted_key not in seen_matches:
                matched_keys.append(accepted_key)
                seen_matches.add(accepted_key)
                continue

            lowered_key = accepted_key.lower()
            lowered_payload_keys = {key.lower(): key for key in payload.keys()}
            if lowered_key in lowered_payload_keys:
                original_key = lowered_payload_keys[lowered_key]
                if original_key not in seen_matches:
                    matched_keys.append(original_key)
                    seen_matches.add(original_key)

        if matched_keys:
            source_key = matched_keys[0]
            normalized_payload[model_field] = payload[source_key]
            key_source_by_model_field[model_field] = source_key
            used_keys.add(source_key)

            if len(matched_keys) > 1:
                collisions.append(
                    {
                        "model_field": model_field,
                        "matched_json_keys": matched_keys,
                        "selected_json_key": source_key,
                    }
                )

    unused_keys = sorted(key for key in payload.keys() if key not in used_keys)
    return normalized_payload, unused_keys, key_source_by_model_field, collisions


def _resolve_derived_fields(
    payload: dict[str, Any],
    model_config: dict[str, Any],
    context: dict[str, Any],
    created_objects: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], list[str], list[dict[str, Any]]]:
    derived_fields_config = model_config.get("derived_fields") or {}
    derived_values: dict[str, Any] = {}
    derived_sources: dict[str, Any] = {}
    missing_dependencies: list[str] = []
    derived_issues: list[dict[str, Any]] = []

    for field_name, rule in derived_fields_config.items():
        source = rule.get("source")

        if source == "context":
            context_key = rule.get("context_key")
            value = context.get(context_key)
            if _is_unanswered(value):
                missing_dependencies.append(field_name)
                derived_issues.append(
                    {
                        "feld": field_name,
                        "quelle": "context",
                        "problem": f"Kontextwert '{context_key}' fehlt.",
                    }
                )
                continue
            derived_values[field_name] = value
            derived_sources[field_name] = {"source": "context", "context_key": context_key}
            continue

        if source == "system_default":
            lookup_model = _get_django_model(rule["lookup_model"])
            lookup_field = rule["lookup_field"]
            lookup_value = rule["lookup_value"]
            instance = lookup_model.objects.filter(**{lookup_field: lookup_value}).first()
            if instance is None:
                missing_dependencies.append(field_name)
                derived_issues.append(
                    {
                        "feld": field_name,
                        "quelle": "system_default",
                        "problem": f"Systemwert '{lookup_value}' in '{rule['lookup_model']}' nicht gefunden.",
                    }
                )
                continue
            derived_values[field_name] = instance.pk
            derived_sources[field_name] = {
                "source": "system_default",
                "lookup_model": rule["lookup_model"],
                "lookup_field": lookup_field,
                "lookup_value": lookup_value,
            }
            continue

        if source == "db_lookup":
            payload_keys = list(rule.get("payload_keys") or [])
            lookup_key, lookup_value = _first_payload_value(payload, payload_keys)
            if _is_unanswered(lookup_value):
                missing_dependencies.append(field_name)
                derived_issues.append(
                    {
                        "feld": field_name,
                        "quelle": "db_lookup",
                        "problem": "Kein passender JSON-Schluessel fuer die Lookup-Information gefunden.",
                    }
                )
                continue

            # Prefer a just-created object from the same validation run.
            created_target_model = rule.get("created_target_model")
            if created_target_model and created_target_model in created_objects:
                derived_values[field_name] = created_objects[created_target_model].pk
                derived_sources[field_name] = {
                    "source": "db_lookup",
                    "lookup_key": lookup_key,
                    "lookup_value": lookup_value,
                    "resolved_from": "created_objects",
                    "target_model": created_target_model,
                }
                continue

            lookup_model = _get_django_model(rule["lookup_model"])
            lookup_field = rule["lookup_field"]
            instance = lookup_model.objects.filter(**{lookup_field: lookup_value}).first()
            if instance is None:
                missing_dependencies.append(field_name)
                derived_issues.append(
                    {
                        "feld": field_name,
                        "quelle": "db_lookup",
                        "problem": f"Kein Datensatz in '{rule['lookup_model']}' fuer '{lookup_value}' gefunden.",
                        "lookup_key": lookup_key,
                    }
                )
                continue

            derived_values[field_name] = instance.pk
            derived_sources[field_name] = {
                "source": "db_lookup",
                "lookup_model": rule["lookup_model"],
                "lookup_field": lookup_field,
                "lookup_key": lookup_key,
                "lookup_value": lookup_value,
            }
            continue

        derived_issues.append(
            {
                "feld": field_name,
                "quelle": source,
                "problem": "Unbekannte Ableitungsquelle in der Mapping-Konfiguration.",
            }
        )
        missing_dependencies.append(field_name)

    return derived_values, derived_sources, missing_dependencies, derived_issues


def _resolve_target_models(target_models: list[str] | str) -> list[str]:
    if isinstance(target_models, str):
        return [target_models]
    return list(target_models)


def validate_payload_against_models_with_mapping(
    payload: dict[str, Any],
    target_models: list[str] | str,
    *,
    context: dict[str, Any] | None = None,
    create_objects: bool = False,
) -> dict[str, Any]:
    config = _load_mapping_config()
    context = context or {}
    models_config = config.get("models") or {}
    resolved_target_models = _resolve_target_models(target_models)

    results: dict[str, Any] = {}
    created_objects: dict[str, Any] = {}

    for target_model in resolved_target_models:
        serializer_cls = TARGET_SERIALIZER_MAP.get(target_model)
        model_config = models_config.get(target_model) or {}

        if serializer_cls is None or not model_config:
            results[target_model] = {
                "kompatibel": False,
                "zielmodell": target_model,
                "fehler": "Unbekanntes Zielmodell.",
                "unterstuetzte_modelle": sorted(TARGET_SERIALIZER_MAP.keys()),
            }
            continue

        if not isinstance(payload, dict):
            results[target_model] = {
                "kompatibel": False,
                "zielmodell": target_model,
                "fehler": "Datei_Inhalt muss ein JSON-Objekt sein.",
            }
            continue

        serializer = serializer_cls()
        accepted_fields = {name for name, field in serializer.fields.items() if not field.read_only}
        required_fields = {name for name, field in serializer.fields.items() if field.required and not field.read_only}

        mapped_payload, unused_keys, source_by_field, collisions = _normalize_payload_with_mapping(
            payload=payload,
            field_mappings=model_config.get("field_mappings") or {},
        )

        derived_values, derived_sources, missing_dependencies, derived_issues = _resolve_derived_fields(
            payload=payload,
            model_config=model_config,
            context=context,
            created_objects=created_objects,
        )
        mapped_payload.update(derived_values)

        filtered_payload = {key: value for key, value in mapped_payload.items() if key in accepted_fields}
        source_by_field.update(derived_sources)

        missing_required_fields = sorted(field for field in required_fields if field not in filtered_payload)
        empty_required_fields = sorted(
            field for field in required_fields if field in filtered_payload and _is_unanswered(filtered_payload.get(field))
        )

        validating_serializer = serializer_cls(data=filtered_payload)
        serializer_valid = validating_serializer.is_valid()
        compatible = bool(
            not missing_required_fields
            and not empty_required_fields
            and not collisions
            and not missing_dependencies
            and serializer_valid
        )

        result = {
            "kompatibel": compatible,
            "zielmodell": target_model,
            "fehlende_pflichtfelder": missing_required_fields,
            "leere_pflichtfelder": empty_required_fields,
            "fehlende_voraussetzungen": missing_dependencies,
            "ungenutzte_json_schluessel": unused_keys,
            "mapping_kollisionen": collisions,
            "zuordnung_json_zu_modelfeld": source_by_field,
            "normalisierte_daten": filtered_payload,
            "feldfehler": validating_serializer.errors if not serializer_valid else {},
            "abgeleitete_felder": derived_sources,
            "abgeleitete_felder_fehler": derived_issues,
            "created_entry": None,
        }

        if create_objects and compatible and serializer_valid:
            created_object = validating_serializer.save()
            created_objects[target_model] = created_object
            result["created_entry"] = {
                "modell": created_object.__class__.__name__,
                "id": getattr(created_object, created_object._meta.pk.attname),
            }

        results[target_model] = result

    overall_compatible = all(result.get("kompatibel", False) for result in results.values())
    return {
        "kompatibel": overall_compatible,
        "zielmodelle": resolved_target_models,
        "model_reports": results,
        "created_entries": {
            model_name: report["created_entry"]
            for model_name, report in results.items()
            if report.get("created_entry")
        },
    }


def validate_payload_against_target_with_mapping(
    payload: dict[str, Any],
    target_model: str,
    *,
    context: dict[str, Any] | None = None,
    create_objects: bool = False,
) -> dict[str, Any]:
    return validate_payload_against_models_with_mapping(
        payload=payload,
        target_models=[target_model],
        context=context,
        create_objects=create_objects,
    )
