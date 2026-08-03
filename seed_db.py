import database
import random
from datetime import datetime, timedelta

def seed():
    print("Generating 20 random dummy bookings...")
    
    names = ["Rahim", "Karim", "Arif", "Nasir", "Sakib", "Tania", "Rina", "Sumi", "Jashim", "Rubel"]
    addresses = ["Dhaka", "Sylhet", "Chittagong", "Rajshahi", "Khulna", "Barisal"]
    
    # Get available schedules
    schedules = []
    routes = database.get_routes()
    for r in routes:
        scheds = database.get_schedules_by_route(r)
        schedules.extend(scheds)
        
    if not schedules:
        print("No schedules found! Please run setup_schedules.py first.")
        return

    # Base date
    base_date = datetime.now().date()
    
    # Rows and cols for seats
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    cols = ['1', '2', '3', '4']
    all_seats = [f"{r}{c}" for r in rows for c in cols]

    for i in range(20):
        phone = f"0171{random.randint(100000, 999999)}"
        name = random.choice(names) + f" {random.randint(1, 99)}"
        address = random.choice(addresses)
        
        # Pick a random schedule
        sched = random.choice(schedules)
        
        # Pick a random date (today or next 2 days)
        travel_date = base_date + timedelta(days=random.randint(0, 2))
        travel_date_str = str(travel_date)
        
        # Get currently booked seats so we don't double book in this script
        booked_seats = database.get_booked_seats(sched['schedule_id'], travel_date_str)
        available_seats = [s for s in all_seats if s not in booked_seats]
        
        if not available_seats:
            continue
            
        seat = random.choice(available_seats)
        price = random.choice([1000, 1200, 1500, 2000])
        status = random.choice(["Paid", "Unpaid", "Partial"])
        
        # Save to DB
        database.save_customer(phone, name, address)
        database.save_booking(
            phone=phone,
            schedule_id=sched['schedule_id'],
            seat_number=seat,
            travel_date=travel_date_str,
            price=price,
            payment_status=status
        )
        
        print(f"Booked: {name} | Phone: {phone} | Bus: {sched['bus_name']} | Seat: {seat} | Date: {travel_date_str}")
        
    print("Done! 20 dummy bookings inserted.")

if __name__ == "__main__":
    seed()
