# sample_repo/models.py

class InvoiceDTO:
    def __init__(self, invoice_id, amount, customer_id):
        self.invoice_id = invoice_id
        self.amount = amount
        self.customer_id = customer_id

class DatabaseClient:
    def save(self, data):
        print("Saving to DB...")
        return True
