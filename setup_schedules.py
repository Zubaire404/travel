import database
import os

def setup():
    """Add default bus schedules with route-based fares."""
    print("Initializing Database...")
    database.init_db()

    print("Adding default bus schedules with fares...")
    
    # Bogura - Dhaka (Base Fare: BDT 700)
    database.add_bus_schedule("SR Travels (Non-AC)", "Bogura - Dhaka", "08:30 AM", base_fare=700)
    database.add_bus_schedule("Shyamoli Paribahan (AC)", "Bogura - Dhaka", "10:00 AM", base_fare=1200)
    database.add_bus_schedule("Hanif Enterprise (AC)", "Bogura - Dhaka", "11:30 PM", base_fare=1200)

    # Bogura - Chittagong (Base Fare: BDT 1400)
    database.add_bus_schedule("Ena Transport (Non-AC)", "Bogura - Chittagong", "07:00 PM", base_fare=1400)
    database.add_bus_schedule("Hanif Enterprise (AC)", "Bogura - Chittagong", "08:30 PM", base_fare=1800)
    database.add_bus_schedule("Desh Travels (AC)", "Bogura - Chittagong", "09:30 PM", base_fare=1800)

    # Bogura - Cox's Bazar (Base Fare: BDT 1800)
    database.add_bus_schedule("Shyamoli Paribahan (Non-AC)", "Bogura - Cox's Bazar", "05:30 PM", base_fare=1800)
    database.add_bus_schedule("Nabil Paribahan (AC)", "Bogura - Cox's Bazar", "07:30 PM", base_fare=2200)
    database.add_bus_schedule("Hanif Enterprise (AC)", "Bogura - Cox's Bazar", "08:45 PM", base_fare=2200)
    
    # Bogura - Rajshahi (Base Fare: BDT 300)
    database.add_bus_schedule("Desh Travels (Non-AC)", "Bogura - Rajshahi", "08:00 AM", base_fare=300)
    database.add_bus_schedule("Hanif Enterprise (Non-AC)", "Bogura - Rajshahi", "02:00 PM", base_fare=300)

    print("Bus schedules with fares added successfully!")

def run():
    """Full reset: delete DB and re-create with defaults."""
    if os.path.exists("travel_agency.db"):
        os.remove("travel_agency.db")
    setup()

if __name__ == "__main__":
    run()
