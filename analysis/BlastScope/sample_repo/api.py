# sample_repo/api.py
from sample_repo.services import BillingService

def handle_billing_request(request_data):
    customer_id = request_data.get("customer_id")
    amount = request_data.get("amount")
    
    service = BillingService()
    result = service.generate_invoice(customer_id, amount)
    
    if result:
        return {"status": "success", "invoice_id": result.invoice_id}
    return {"status": "error", "message": "Failed to generate billing"}
