

from datetime import datetime
from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Integer, Numeric, PrimaryKeyConstraint, SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class LoanAllocations(Base):
    __tablename__ = 'loan_allocations'

    id = Column(Integer, autoincrement=True)
    company_id = Column(String(36), nullable=False)
    loan_id = Column(String(64), nullable=False)
    allocated_user_id = Column(String(256))
    user_active = Column(Boolean, default=False)
    active = Column(Boolean, default=False)
    user_path = Column(Text)
    role_id = Column(String(256))
    profession = Column(String(256))
    team = Column(String(8))
    location = Column(String(64))
    department = Column(String(256))
    created = Column(DateTime)
    updated = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    audit_timestamp = Column(Integer)
    audit_operation = Column(String(255))

    __table_args__ = (
        PrimaryKeyConstraint('company_id', 'loan_id', 'allocated_user_id'),
    )


class LendingLoanDetails(Base):
    __tablename__ = 'lending_loan_details'

    id = Column(Integer, autoincrement=True)
    company_id = Column(String(36), nullable=False)
    loan_id = Column(String(64), nullable=False)
    created = Column(DateTime)
    updated = Column(DateTime)
    loan_type = Column(String(256))
    product_type = Column(String(256))
    loan_region = Column(String(256))
    loan_zone = Column(String(256))
    loan_branch = Column(String(256))
    applicant_pincode = Column(String(8))
    applicant_state = Column(String(64))
    applicant_city = Column(String(64))
    loan_nbfc_name = Column(String(256))
    legal_status = Column(String(64))
    settlement_status = Column(String(64))
    global_status = Column(String(64))
    applicant_language = Column(JSON)
    archive = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    audit_timestamp = Column(Integer)
    audit_operation = Column(String(255))

    __table_args__ = (
        PrimaryKeyConstraint('company_id', 'loan_id'),
    )


class LendingDefaultDetails(Base):
    __tablename__ = 'lending_default_details'

    id = Column(Integer, autoincrement=True)
    company_id = Column(String(36), nullable=False)
    loan_id = Column(String(64), nullable=False)
    allocation_month = Column(Date, nullable=False)
    amount_recovered = Column(Numeric(65, 2), default=None)
    principal_outstanding_amount = Column(Numeric(65, 2), default=None)
    total_outstanding_amount = Column(Numeric(65, 2), default=None)
    recovery_method = Column(String(128), default=None)
    payment_method = Column(String(128), default=None)
    final_status = Column(String(128), default=None)
    allocation_dpd_value = Column(Integer, default=None)
    total_claim_amount = Column(Numeric(65, 2), default=None)
    date_of_default = Column(Date, default=None)
    is_latest_allocation_month = Column(Boolean, default=False)
    recovery_status = Column(String(128), default=None)
    calling_status = Column(String(128), default=None)
    fos_status = Column(String(128), default=None)
    communication_status = Column(String(128), default=None)
    created = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    updated = Column(DateTime, server_default='CURRENT_TIMESTAMP')
    is_deleted = Column(Boolean, default=False)
    archive = Column(Boolean, default=False)
    audit_timestamp = Column(BigInteger, default=None)
    audit_operation = Column(String(255), default=None)
    loan_collection_stage = Column(Integer, default=None)
    allocation_dpd_bracket = Column(String(255), default=None)

    __table_args__ = (
        PrimaryKeyConstraint('company_id', 'loan_id', 'allocation_month'),
    )


class Tags(Base):
    __tablename__ = 'tags'

    id = Column(Integer, autoincrement=True)
    company_id = Column(String(36), nullable=False)
    loan_id = Column(String(64), nullable=False)
    allocation_month = Column(Date, nullable=False)
    tag_name = Column(String(256), nullable=False)
    created = Column(DateTime)
    updated = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    audit_timestamp = Column(Integer)
    audit_operation = Column(String(255))

    __table_args__ = (
        PrimaryKeyConstraint('company_id', 'loan_id', 'allocation_month', 'tag_name'),
    )


class UserHierarchy(Base):
    __tablename__ = 'user_hierarchy'

    id = Column(Integer, autoincrement=True)
    user_id = Column(String(64), nullable=False)
    company_id = Column(String(36))
    role_id = Column(String(256))
    profession = Column(String(256))
    team = Column(String(256))
    location = Column(String(256))
    department = Column(String(256))
    created = Column(DateTime)
    updated = Column(DateTime)
    active = Column(Boolean, default=True)
    audit_timestamp = Column(Integer)
    audit_operation = Column(String(255))
    path = Column(String)
    first_name = Column(String(255))
    last_name = Column(String(255))

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'company_id'),
    )


class DTMF_IVR(Base):
    __tablename__ = "fct_dtmf_ivr_communication"
    id = Column(Integer, autoincrement=True)
    updated = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    shoot_id = Column(String(50), nullable=False)
    company_id = Column(String(40), nullable=False)
    loan_id = Column(String(64), nullable=False)
    allocation_month = Column(Date, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    snapshot_dpd = Column(Integer, default=None)
    template_id = Column(String(50), nullable=False)
    template_name = Column(String(64), nullable=False)
    template_language = Column(String(1024), nullable=False)
    is_triggered = Column(SmallInteger, default=0)
    is_delivered = Column(SmallInteger, default=0)
    is_answered = Column(SmallInteger, default=0)
    is_responded = Column(SmallInteger, default=0)
    status = Column(SmallInteger, default=0)
    city = Column(String(512), default="")
    state = Column(String(256), default="")
    loan_type = Column(String(256), default="")
    product_type = Column(String(256), default="")
    date_of_default = Column(Date, default=None)
    is_loan_archive = Column(Boolean, default=False)
    is_loan_deleted = Column(Boolean, default=False)
    is_loan_default_archive = Column(Boolean, default=False)
    is_loan_default_deleted = Column(Boolean, default=False)
    is_latest_allocation_month = Column(Boolean, default=False)
    transaction_id = Column(String(46))
    
    __table_args__ = (PrimaryKeyConstraint("loan_id", "company_id", "allocation_month", "shoot_id"),)