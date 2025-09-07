from sqlalchemy import Column, Boolean, String, Integer, Numeric, ForeignKey, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, DATE, JSONB, ENUM, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import  relationship
from sqlalchemy.sql import func
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# SQLAlchemy setup
Base = declarative_base()

# Define SQLAlchemy models for production tables
# Schema 'community_orgs'
# Define the enumerations
alias_type_enum = ENUM('trading_name', 'abbreviation', 'former_name', name='alias_type_enum', schema='community_orgs', create_type=False)

class Organisations(Base):
    __tablename__ = 'organisations'
    __table_args__ = (
        {'schema': 'community_orgs',
         'indexes': [
             Index('idx_org_date', 'date_established'),
             Index('idx_org_legal_name', 'entity_name'),
             Index('idx_organisations_public', 'is_public', postgresql_where='is_public = TRUE')
         ],
         'postgresql': {
             'constraint_organisations_pkey': {'org_id': 'primary'},
             'constraint_organisations_slug_key': {'slug': 'unique'}
         }
        }
    )
    org_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    entity_name = Column(String, nullable=False)
    date_established = Column(DATE, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    slug = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    is_public = Column(Boolean, nullable=False, default=True, server_default='true')
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])
 
class Alias(Base):
    __tablename__ = 'aliases'
    __table_args__ = {'schema': 'community_orgs'}
    alias_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    alias_type = Column(alias_type_enum, nullable=True)
    alias = Column(String, nullable=True)
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='aliases')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class ContactInfo(Base):
    __tablename__ = 'contact_info'
    __table_args__ = {'schema': 'community_orgs'}
    contact_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    physical_address = Column(String, nullable=True)
    postal_address = Column(String, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    social_media = Column(JSONB, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='contact_info')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class LegalDetails(Base):
    __tablename__ = 'legal_details'
    __table_args__ = (
        {
            'schema': 'community_orgs',
            'indexes': [
                Index('idx_org_abn', 'abn')
            ]
        }
    )
    legal_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    entity_type = Column(String, nullable=True)
    abn = Column(String, nullable=True)
    acn = Column(String, nullable=True)
    acnc_status = Column(Boolean, nullable=True)
    tax_concession_endorsement = Column(DATE, nullable=True)
    insurance_details = Column(JSONB, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    charity_type = Column(String, nullable=True)
    incorporation_number = Column(String, nullable=True)
    incorporation_status = Column(Boolean, nullable=True)
    incorporation_registration_date = Column(DATE, nullable=True)
    abn_status = Column(Boolean, nullable=True)
    abn_activated = Column(DATE, nullable=True)
    abn_last_updated = Column(DATE, nullable=True)
    acnc_registered = Column(Boolean, nullable=True)
    acnc_registered_date = Column(DATE, nullable=True)
    gst_concession_endorsement_date = Column(String, nullable=True)
    dgr_endorsement = Column(Boolean, nullable=True)
    organisation = relationship('Organisation', backref='legal_details')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class DGREndorsement(Base):
    __tablename__ = 'dgr_endorsement'
    __table_args__ = (
        {
            'schema': 'community_orgs',
            'postgresql': {
                'constraint_dgr_endorsement_legal_id_key': {'legal_id': 'unique'}
            }
        }
    )
    endorsement_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    legal_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.legal_details.legal_id'), nullable=True, unique=True)
    endorsement_start_date = Column(DATE, nullable=True)
    endorsement_end_date = Column(DATE, nullable=True)
    dgr_items = Column(String, nullable=True)
    dgr_funds = Column(String, nullable=True)
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    legal_details = relationship('LegalDetails', backref='dgr_endorsements')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class Relationship(Base):
    __tablename__ = 'relationships'
    __table_args__ = {'schema': 'community_orgs'}
    relationship_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    partner_org = Column(String(255), nullable=True)
    relationship_type = Column(String(100), nullable=True)
    start_date = Column(DATE, nullable=True)
    end_date = Column(DATE, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='relationships')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class ProgramService(Base):
    __tablename__ = 'programs_services'
    __table_args__ = {'schema': 'community_orgs'}
    program_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    program_name = Column(String(255), nullable=True)
    description = Column(String, nullable=True)
    fee_structure = Column(JSONB, nullable=True)
    delivery_location = Column(ARRAY(String), nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='programs_services')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class ResourcesAssets(Base):
    __tablename__ = 'resources_assets'
    __table_args__ = {'schema': 'community_orgs'}
    asset_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    asset_type = Column(String, nullable=True)
    asset_description = Column(String, nullable=True)
    acquisition_date = Column(DATE, nullable=True)
    asset_value = Column(Numeric(precision=15, scale=2), nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='resources_assets')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class Accreditation(Base):
    __tablename__ = 'accreditation'
    __table_args__ = {'schema': 'community_orgs'}
    accreditation_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    certification_type = Column(String(255), nullable=True)
    issuing_body = Column(String(255), nullable=True)
    valid_from = Column(DATE, nullable=True)
    valid_until = Column(DATE, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='accreditations')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class FinancialInfo(Base):
    __tablename__ = 'financial_info'
    __table_args__ = {'schema': 'community_orgs'}
    finance_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    funding_sources = Column(ARRAY(String), nullable=True)
    annual_budget = Column(Numeric(precision=15, scale=2), nullable=True)
    financial_year_end = Column(DATE, nullable=True)
    auditor_details = Column(JSONB, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='financial_info')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class HistoricalInfo(Base):
    __tablename__ = 'historical_info'
    __table_args__ = {'schema': 'community_orgs'}
    history_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    founding_members = Column(ARRAY(String), nullable=True)
    milestone_date = Column(DATE, nullable=True)
    milestone_description = Column(String, nullable=True)
    structural_changes = Column(JSONB, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='historical_info')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class Governance(Base):
    __tablename__ = 'governance'
    __table_args__ = {'schema': 'community_orgs'}
    governance_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    board_structure = Column(JSONB, nullable=True)
    constitution = Column(String, nullable=True)
    org_chart = Column(String, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='governance')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class OperationalDetails(Base):
    __tablename__ = 'operational_details'
    __table_args__ = {'schema': 'community_orgs'}
    op_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    service_area = Column(String, nullable=True)
    target_demographics = Column(String, nullable=True)
    operating_hours = Column(JSONB, nullable=True)
    staff_count_paid = Column(Integer, nullable=True)
    staff_count_volunteer = Column(Integer, nullable=True)
    languages_supported = Column(ARRAY(String), nullable=True)
    accessibility_features = Column(ARRAY(String), nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='operational_details')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class PerformanceMetrics(Base):
    __tablename__ = 'performance_metrics'
    __table_args__ = {'schema': 'community_orgs'}
    metric_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    metric_type = Column(String, nullable=True)
    metric_value = Column(JSONB, nullable=True)
    measurement_date = Column(DATE, nullable=True)
    reporting_period = Column(String, nullable=True)
    inserted_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='performance_metrics')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class OrgMembers(Base):
    __tablename__ = 'org_members'
    __table_args__ = (
        {'schema': 'community_orgs'},
        CheckConstraint("role IN ('admin', 'member', 'viewer')", name='org_members_role_check')
    )
    member_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    role = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_at = Column(TIMESTAMP(timezone=False), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=False), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='org_members')
    user = relationship('User', foreign_keys=[user_id])
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class OrgVisibility(Base):
    __tablename__ = 'org_visibility'
    __table_args__ = (
        {'schema': 'community_orgs'},
        CheckConstraint("visibility_type IN ('public', 'limited', 'restricted')", name='org_visibility_visibility_type_check')
    )
    visibility_id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    org_id = Column(UUID(as_uuid=True), ForeignKey('community_orgs.organisations.org_id'), nullable=True)
    visibility_type = Column(String, nullable=True)
    allowed_org_ids = Column(ARRAY(Integer), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=True, server_default=func.current_timestamp())
    inserted_at = Column(TIMESTAMP(timezone=False), nullable=True, server_default=func.current_timestamp())
    last_edited_at = Column(TIMESTAMP(timezone=False), nullable=True, server_default=func.current_timestamp())
    inserted_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    last_edited_by = Column(UUID(as_uuid=True), ForeignKey('auth.users.id'), nullable=True)
    organisation = relationship('Organisation', backref='org_visibility')
    inserted_by_user = relationship('User', foreign_keys=[inserted_by])
    last_edited_by_user = relationship('User', foreign_keys=[last_edited_by])

class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'community_orgs'}

class UserOrganisationRoles(Base):
    __tablename__ = 'user_organisation_roles'
    __table_args__ = {'schema': 'community_orgs'}

class RoleRequests(Base):
    __tablename__ = 'role_requests'
    __table_args__ = {'schema': 'community_orgs'}

class RoleAuditLog(Base):
    __tablename__ = 'role_audit_log'
    __table_args__ = {'schema': 'community_orgs'}

class ReservedSlugs(Base):
    __tablename__ = 'reserved_slugs'
    __table_args__ = {'schema': 'community_orgs'}
