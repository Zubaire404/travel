import sqlite3
import os

DB_NAME = "travel_agency.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            phone_number TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            address TEXT
        )
    ''')
    
    # Create Bus Schedules Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_schedules (
            schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_name TEXT NOT NULL,
            route TEXT NOT NULL,
            departure_time TEXT NOT NULL,
            total_seats INTEGER DEFAULT 40
        )
    ''')
    
    # Create Bookings Table with AUTOINCREMENT Ticket ID
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            schedule_id INTEGER NOT NULL,
            seat_number TEXT NOT NULL,
            travel_date TEXT NOT NULL,
            price REAL NOT NULL,
            payment_status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (phone_number) REFERENCES customers (phone_number),
            FOREIGN KEY (schedule_id) REFERENCES bus_schedules (schedule_id)
        )
    ''')
    
    # Safely add status and refund columns for cancellations if they don't exist
    try:
        cursor.execute("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'Booked'")
    except sqlite3.OperationalError:
        pass
        
    try:
        cursor.execute("ALTER TABLE bookings ADD COLUMN refund_amount REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE bookings ADD COLUMN refund_date TIMESTAMP")
    except sqlite3.OperationalError:
        pass

    # Safely add base_fare column to bus_schedules for route-based pricing
    try:
        cursor.execute("ALTER TABLE bus_schedules ADD COLUMN base_fare REAL DEFAULT 0.0")
    except sqlite3.OperationalError:
        pass

    # Set the starting sequence for bookings so ticket ID looks like TKT1000+
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sqlite_sequence'")
    if cursor.fetchone():
        cursor.execute("SELECT COUNT(*) FROM sqlite_sequence WHERE name='bookings'")
        if cursor.fetchone()[0] == 0:
            try:
                cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('bookings', 1000)")
            except sqlite3.Error:
                pass
    else:
        pass
            
    conn.commit()
    conn.close()

def get_customer(phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name, address FROM customers WHERE phone_number = ?', (phone,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"name": result[0], "address": result[1]}
    return None

def save_customer(phone, name, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (phone_number, name, address)
        VALUES (?, ?, ?)
        ON CONFLICT(phone_number) DO UPDATE SET
            name=excluded.name,
            address=excluded.address
    ''', (phone, name, address))
    conn.commit()
    conn.close()

def save_booking(phone, schedule_id, seat_number, travel_date, price, payment_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO bookings (phone_number, schedule_id, seat_number, travel_date, price, payment_status, status)
        VALUES (?, ?, ?, ?, ?, ?, 'Booked')
    ''', (phone, schedule_id, seat_number, travel_date, price, payment_status))
    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def cancel_booking(booking_id, refund_amount=0.0):
    """Cancel a booking. Returns a dict with success/error status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if booking exists and its current status
    cursor.execute('SELECT status, price FROM bookings WHERE booking_id = ?', (booking_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {"success": False, "message": f"Ticket TKT{booking_id} not found in the system."}
    
    current_status = row[0] or "Booked"
    original_price = row[1]
    
    if current_status == "Cancelled":
        conn.close()
        return {"success": False, "message": f"Ticket TKT{booking_id} is already cancelled."}
    
    if refund_amount > original_price:
        conn.close()
        return {"success": False, "message": f"Refund amount (BDT {refund_amount}) exceeds original fare (BDT {original_price})."}
    
    cursor.execute('''
        UPDATE bookings 
        SET status = 'Cancelled', refund_amount = ?, refund_date = CURRENT_TIMESTAMP 
        WHERE booking_id = ?
    ''', (refund_amount, booking_id))
    conn.commit()
    conn.close()
    return {"success": True, "message": f"Ticket TKT{booking_id} cancelled. Refund: BDT {refund_amount}."}

def get_all_bookings():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''
        SELECT b.booking_id, c.name as customer_name, b.phone_number, 
               s.route, s.bus_name, s.departure_time, b.seat_number,
               b.travel_date, b.price, b.payment_status, b.status, 
               b.refund_amount, b.refund_date, b.created_at
        FROM bookings b
        JOIN customers c ON b.phone_number = c.phone_number
        JOIN bus_schedules s ON b.schedule_id = s.schedule_id
        ORDER BY b.created_at DESC
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_routes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT route FROM bus_schedules')
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_schedules_by_route(route):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bus_schedules WHERE route = ?', (route,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_schedule_by_id(schedule_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bus_schedules WHERE schedule_id = ?', (schedule_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_booked_seats(schedule_id, travel_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT seat_number FROM bookings 
        WHERE schedule_id = ? AND travel_date = ? AND status != 'Cancelled'
    ''', (schedule_id, travel_date))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_booked_seat_count(schedule_id, travel_date):
    """Returns the count of booked (non-cancelled) seats for a given schedule and date."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM bookings 
        WHERE schedule_id = ? AND travel_date = ? AND status != 'Cancelled'
    ''', (schedule_id, travel_date))
    count = cursor.fetchone()[0]
    conn.close()
    return count

# Helper to add schedules
def add_bus_schedule(bus_name, route, departure_time, total_seats=40, base_fare=0.0):
    conn = get_connection()
    cursor = conn.cursor()
    # Check if exists
    cursor.execute('SELECT schedule_id FROM bus_schedules WHERE bus_name=? AND route=? AND departure_time=?', 
                   (bus_name, route, departure_time))
    existing = cursor.fetchone()
    if not existing:
        cursor.execute('''
            INSERT INTO bus_schedules (bus_name, route, departure_time, total_seats, base_fare)
            VALUES (?, ?, ?, ?, ?)
        ''', (bus_name, route, departure_time, total_seats, base_fare))
    else:
        # Update base_fare for existing schedules
        cursor.execute('UPDATE bus_schedules SET base_fare = ? WHERE schedule_id = ?', (base_fare, existing[0]))
    conn.commit()
    conn.close()
