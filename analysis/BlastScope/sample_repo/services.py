# sample_repo/services.py
from sample_repo.models import InvoiceDTO, DatabaseClient

class BillingService:
    def __init__(self):
        self.db = DatabaseClient()

    def generate_invoice(self, customer_id, amount):
        invoice = InvoiceDTO(invoice_id="INV-123", amount=amount, customer_id=customer_id)
        if self.db.save(invoice):
            print("Invoice generated and saved.")
            return invoice
        return None
