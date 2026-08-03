import database
import pdf_generator
import sms_service
import os

print("1. Initializing DB...")
database.init_db()

print("2. Saving customer...")
database.save_customer("01712345678", "Test Passenger", "Dhaka")

print("3. Fetching customer...")
cust = database.get_customer("01712345678")
print("Found Customer:", cust)

print("4. Fetching schedule...")
schedules = database.get_schedules_by_route("Dhaka - Cox's Bazar")
if not schedules:
    import setup_schedules
    setup_schedules.setup()
    schedules = database.get_schedules_by_route("Dhaka - Cox's Bazar")
sched = schedules[0]

print("5. Saving booking...")
bid = database.save_booking(
    phone="01712345678",
    schedule_id=sched['schedule_id'],
    seat_number="A1",
    travel_date="2026-10-15",
    price=1500.0,
    payment_status="Paid"
)
print("Created Booking ID:", bid)

print("6. Generating PDF Ticket...")
pdf_path = pdf_generator.generate_ticket(
    booking_id=bid,
    name="Test Passenger",
    phone="01712345678",
    address="Dhaka",
    bus_name=sched['bus_name'],
    route=sched['route'],
    departure_time=sched['departure_time'],
    seat_number="A1",
    travel_date="2026-10-15",
    price=1500.0,
    payment_status="Paid"
)
print("PDF saved at:", pdf_path)
print("Does PDF exist?", os.path.exists(pdf_path))

print("7. Testing SMS Service (Mock Mode)...")
sms_res = sms_service.send_booking_sms(
    phone_number="01712345678",
    customer_name="Test Passenger",
    ticket_id=bid,
    bus_name=sched['bus_name'],
    seat_number="A1",
    travel_date="2026-10-15",
    departure_time=sched['departure_time'],
    price=1500.0
)
print("SMS Result:", sms_res)

print("\n[SUCCESS] WORKFLOW TEST COMPLETED SUCCESSFULLY!")
