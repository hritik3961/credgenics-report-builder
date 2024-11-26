from datetime import timedelta


CURRENT = "current"
ADJUSTED_TIME = timedelta(hours=5, minutes=30)
COMPLETE_ACCESS = ["chief admin", "super admin", "super user", "company admin", "api user"]

TABLES_MAPPING = {
    "LendingLoanDetails": ["company_id", "loan_id"],
    "LoanAllocations": ["company_id", "loan_id", "allocated_user_id"],
    "LendingDefaultDetails": ["company_id", "loan_id", "allocation_month"],
    "Tags": ["company_id", "loan_id", "allocation_month"],
    "DTMF_IVR": ["company_id", "loan_id", "allocation_month", "shoot_id"]
}
