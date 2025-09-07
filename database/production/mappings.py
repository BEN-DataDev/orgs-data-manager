from datetime import date
import uuid, json, logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MAPPINGS = {
    'organisations': {
        'source_fields': {
            'name': {'target': 'entity_name', 'transform': lambda x: x.strip()},
            'established_date': {'target': 'date_established', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'description_text': {'target': 'description', 'transform': lambda x: x.strip() if x else None},
            'public_status': {'target': 'is_public', 'transform': lambda x: bool(x) if x is not None else True},
            'slug_value': {'target': 'slug', 'transform': lambda x: x.strip().lower().replace(' ', '-') if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'org_id': lambda: None,  # Handled by uuid_generate_v4()
            'created_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'dgr_endorsement': {
        'source_fields': {
            'start_date': {'target': 'endorsement_start_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'end_date': {'target': 'endorsement_end_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'items': {'target': 'dgr_items', 'transform': lambda x: x.strip() if x else None},
            'funds': {'target': 'dgr_funds', 'transform': lambda x: x.strip() if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'legal_id': {'target': 'legal_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'endorsement_id': lambda: None,  # Handled by uuid_generate_v4()
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'accreditation': {
        'source_fields': {
            'cert_type': {'target': 'certification_type', 'transform': lambda x: x.strip()[:255] if x else None},
            'issuer': {'target': 'issuing_body', 'transform': lambda x: x.strip()[:255] if x else None},
            'start_date': {'target': 'valid_from', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'end_date': {'target': 'valid_until', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'accreditation_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'contact_info': {
            'source_fields': {
                'physical_addr': {'target': 'physical_address', 'transform': lambda x: x.strip() if x else None},
                'postal_addr': {'target': 'postal_address', 'transform': lambda x: x.strip() if x else None},
                'phone_number': {'target': 'phone', 'transform': lambda x: x.strip()[:50] if x else None},
                'email_address': {'target': 'email', 'transform': lambda x: x.strip()[:255].lower() if x else None},
                'website_url': {'target': 'website', 'transform': lambda x: x.strip()[:255] if x else None},
                'social_media_data': {'target': 'social_media', 'transform': lambda x: json.loads(x) if x else None},
                'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
                'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
                'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
            },
            'defaults': {
                'contact_id': lambda: None,  # Handled by uuid_generate_v4()
                'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
                'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
            }
    },
    'aliases': {
        'source_fields': {
            'alias_type': {'target': 'alias_type', 'transform': lambda x: x if x in ['trading_name', 'abbreviation', 'former_name'] else None},
            'alias_name': {'target': 'alias', 'transform': lambda x: x.strip() if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'alias_id': lambda: None,  # Handled by uuid_generate_v4()
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'legal_details': {
        'source_fields': {
            'entity_type': {'target': 'entity_type', 'transform': lambda x: x.strip() if x else None},
            'abn': {'target': 'abn', 'transform': lambda x: x.strip() if x else None},
            'acn': {'target': 'acn', 'transform': lambda x: x.strip() if x else None},
            'acnc_status': {'target': 'acnc_status', 'transform': lambda x: bool(x) if x is not None else None},
            'tax_concession_date': {'target': 'tax_concession_endorsement', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'insurance_data': {'target': 'insurance_details', 'transform': lambda x: json.loads(x) if x else None},
            'charity_type': {'target': 'charity_type', 'transform': lambda x: x.strip() if x else None},
            'incorporation_num': {'target': 'incorporation_number', 'transform': lambda x: x.strip() if x else None},
            'incorporation_status': {'target': 'incorporation_status', 'transform': lambda x: bool(x) if x is not None else None},
            'incorporation_date': {'target': 'incorporation_registration_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'abn_status': {'target': 'abn_status', 'transform': lambda x: bool(x) if x is not None else None},
            'abn_active_date': {'target': 'abn_activated', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'abn_updated_date': {'target': 'abn_last_updated', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'acnc_registered': {'target': 'acnc_registered', 'transform': lambda x: bool(x) if x is not None else None},
            'acnc_registered_date': {'target': 'acnc_registered_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'gst_concession_date': {'target': 'gst_concession_endorsement_date', 'transform': lambda x: x.strip() if x else None},
            'dgr_endorsement': {'target': 'dgr_endorsement', 'transform': lambda x: bool(x) if x is not None else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'legal_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'relationships': {
        'source_fields': {
            'partner_organisation': {'target': 'partner_org', 'transform': lambda x: x.strip()[:255] if x else None},
            'rel_type': {'target': 'relationship_type', 'transform': lambda x: x.strip()[:100] if x else None},
            'start_date': {'target': 'start_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'end_date': {'target': 'end_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'relationship_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'programs_services': {
        'source_fields': {
            'program_name': {'target': 'program_name', 'transform': lambda x: x.strip()[:255] if x else None},
            'program_description': {'target': 'description', 'transform': lambda x: x.strip() if x else None},
            'fee_structure_data': {'target': 'fee_structure', 'transform': lambda x: json.loads(x) if x else None},
            'locations': {'target': 'delivery_location', 'transform': lambda x: x if isinstance(x, list) else json.loads(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'program_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'resources_assets': {
        'source_fields': {
            'asset_type': {'target': 'asset_type', 'transform': lambda x: x.strip() if x else None},
            'asset_description': {'target': 'asset_description', 'transform': lambda x: x.strip() if x else None},
            'acquisition_date': {'target': 'acquisition_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'asset_value': {'target': 'asset_value', 'transform': lambda x: float(x) if x is not None else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'asset_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'financial_info': {
        'source_fields': {
            'funding_sources': {'target': 'funding_sources', 'transform': lambda x: x if isinstance(x, list) else json.loads(x) if x else None},
            'annual_budget': {'target': 'annual_budget', 'transform': lambda x: float(x) if x is not None else None},
            'financial_year_end': {'target': 'financial_year_end', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'auditor_details': {'target': 'auditor_details', 'transform': lambda x: json.loads(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'finance_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'historical_info': {
        'source_fields': {
            'founding_members': {'target': 'founding_members', 'transform': lambda x: x if isinstance(x, list) else json.loads(x) if x else None},
            'milestone_date': {'target': 'milestone_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'milestone_description': {'target': 'milestone_description', 'transform': lambda x: x.strip() if x else None},
            'structural_changes': {'target': 'structural_changes', 'transform': lambda x: json.loads(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'history_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'governance': {
        'source_fields': {
            'board_structure': {'target': 'board_structure', 'transform': lambda x: json.loads(x) if x else None},
            'constitution': {'target': 'constitution', 'transform': lambda x: x.strip() if x else None},
            'org_chart': {'target': 'org_chart', 'transform': lambda x: x.strip() if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'governance_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'operational_details': {
        'source_fields': {
            'service_area': {'target': 'service_area', 'transform': lambda x: x.strip() if x else None},
            'target_demographics': {'target': 'target_demographics', 'transform': lambda x: x.strip() if x else None},
            'operating_hours': {'target': 'operating_hours', 'transform': lambda x: json.loads(x) if x else None},
            'staff_count_paid': {'target': 'staff_count_paid', 'transform': lambda x: int(x) if x is not None else None},
            'staff_count_volunteer': {'target': 'staff_count_volunteer', 'transform': lambda x: int(x) if x is not None else None},
            'languages_supported': {'target': 'languages_supported', 'transform': lambda x: x if isinstance(x, list) else json.loads(x) if x else None},
            'accessibility_features': {'target': 'accessibility_features', 'transform': lambda x: x if isinstance(x, list) else json.loads(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'op_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'performance_metrics': {
        'source_fields': {
            'metric_type': {'target': 'metric_type', 'transform': lambda x: x.strip() if x else None},
            'metric_value': {'target': 'metric_value', 'transform': lambda x: json.loads(x) if x else None},
            'measurement_date': {'target': 'measurement_date', 'transform': lambda x: date.fromisoformat(x) if x else None},
            'reporting_period': {'target': 'reporting_period', 'transform': lambda x: x.strip() if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'organisation_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'metric_id': lambda: None,  # Handled by uuid_generate_v4()
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'org_members': {
        'source_fields': {
            'user_id': {'target': 'user_id', 'transform': lambda x: uuid.UUID(x) if x else None},
            'role': {'target': 'role', 'transform': lambda x: x.strip() if x and x.strip() in ['admin', 'member', 'viewer'] else (logger.warning(f"Invalid role: {x}"), None)[1]},
            'org_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'member_id': lambda: None,  # Handled by uuid_generate_v4()
            'created_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    },
    'org_visibility': {
        'source_fields': {
            'visibility_type': {'target': 'visibility_type', 'transform': lambda x: x.strip() if x and x.strip() in ['public', 'limited', 'restricted'] else (logger.warning(f"Invalid visibility_type: {x}"), None)[1]},
            'allowed_org_ids': {'target': 'allowed_org_ids', 'transform': lambda x: [int(i) for i in (x if isinstance(x, list) else json.loads(x)) if str(i).isdigit()] if x else None},
            'org_id': {'target': 'org_id', 'transform': lambda x: uuid.UUID(x) if x else None},
            'inserted_by_id': {'target': 'inserted_by', 'transform': lambda x: uuid.UUID(x) if x else None},
            'last_edited_by_id': {'target': 'last_edited_by', 'transform': lambda x: uuid.UUID(x) if x else None},
        },
        'defaults': {
            'visibility_id': lambda: None,  # Handled by uuid_generate_v4()
            'created_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'inserted_at': lambda: None,  # Handled by CURRENT_TIMESTAMP
            'last_edited_at': lambda: None  # Handled by CURRENT_TIMESTAMP
        }
    }
}