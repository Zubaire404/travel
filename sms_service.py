import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure API Token (defaults to env var or mock mode)
GREENWEB_API_TOKEN = os.environ.get("GREENWEB_API_TOKEN", None)

def send_booking_sms(phone_number, customer_name, ticket_id, bus_name, seat_number, travel_date, departure_time, price, api_token=None):
    """
    Sends an automated SMS notification to the passenger.
    Supports local Bangladeshi SMS gateways (e.g., Greenweb BD / BulkSMSBD).
    Defaults to Mock Mode if no API token is supplied.
    """
    token = api_token or GREENWEB_API_TOKEN
    
    # Compose SMS Text
    message_text = (
        f"Hello {customer_name}, your ticket is Confirmed!\n"
        f"Ticket ID: TKT{ticket_id}\n"
        f"Bus: {bus_name}\n"
        f"Seat: {seat_number}\n"
        f"Date: {travel_date} ({departure_time})\n"
        f"Fare: BDT {price}\n"
        f"Thank you for choosing us!"
    )
    
    # Standardize Phone Number format (e.g. convert 017... to 88017...)
    clean_phone = phone_number.strip()
    if clean_phone.startswith("0"):
        clean_phone = "88" + clean_phone
    elif not clean_phone.startswith("880"):
        clean_phone = "880" + clean_phone.lstrip("+")
        
    if not token:
        # Mock Mode
        logger.info(f"[MOCK SMS SENT] To: {clean_phone}\nContent:\n{message_text}\n" + "-"*40)
        return {
            "success": True,
            "mock": True,
            "phone": clean_phone,
            "message": "SMS simulated successfully (No API Token configured)."
        }
        
    try:
        # Greenweb / BulkSMSBD API endpoint
        url = "http://api.greenweb.com.bd/api.php"
        data = {
            "token": token,
            "to": clean_phone,
            "message": message_text
        }
        response = requests.post(url, data=data, timeout=8)
        res_text = response.text
        
        logger.info(f"[REAL SMS SENT] Response: {res_text}")
        return {
            "success": True,
            "mock": False,
            "phone": clean_phone,
            "response": res_text,
            "message": "Real SMS sent successfully."
        }
    except Exception as e:
        logger.error(f"[SMS ERROR] Failed to send SMS: {e}")
        return {
            "success": False,
            "mock": False,
            "error": str(e),
            "message": f"Failed to send SMS: {e}"
        }
