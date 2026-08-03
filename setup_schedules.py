import database
import os

def setup():
    """Add default bus schedules with route-based fares."""
    print("Initializing Database...")
    database.init_db()

    print("Adding default bus schedules with fares...")
    
    # Dhaka - Sylhet (Base Fare: BDT 800)
    database.add_bus_schedule("Bus-1", "Dhaka - Sylhet", "10:00 AM", base_fare=800)
    database.add_bus_schedule("Bus-2", "Dhaka - Sylhet", "12:00 PM", base_fare=800)
    database.add_bus_schedule("Bus-3", "Dhaka - Sylhet", "08:00 PM", base_fare=800)

    # Dhaka - Cox's Bazar (Base Fare: BDT 1600)
    database.add_bus_schedule("Bus-1", "Dhaka - Cox's Bazar", "08:00 AM", base_fare=1600)
    database.add_bus_schedule("Bus-2", "Dhaka - Cox's Bazar", "10:00 AM", base_fare=1600)
    database.add_bus_schedule("Bus-3", "Dhaka - Cox's Bazar", "09:00 PM", base_fare=1600)

    # Dhaka - Chittagong (Base Fare: BDT 900)
    database.add_bus_schedule("Bus-1", "Dhaka - Chittagong", "07:30 AM", base_fare=900)
    database.add_bus_schedule("Bus-2", "Dhaka - Chittagong", "11:00 AM", base_fare=900)
    database.add_bus_schedule("Bus-3", "Dhaka - Chittagong", "11:30 PM", base_fare=900)

    print("Bus schedules with fares added successfully!")

def run():
    """Full reset: delete DB and re-create with defaults."""
    if os.path.exists("travel_agency.db"):
        os.remove("travel_agency.db")
    setup()

if __name__ == "__main__":
    run()
