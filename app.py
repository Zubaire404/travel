import streamlit as st
import importlib
import database
importlib.reload(database)
import pdf_generator
importlib.reload(pdf_generator)
import sms_service
importlib.reload(sms_service)
import os
import pandas as pd
from datetime import datetime

# Initialize Database
database.init_db()

# --- THEME MANAGEMENT ---
def set_theme(is_dark):
    os.makedirs(".streamlit", exist_ok=True)
    config_path = ".streamlit/config.toml"
    
    current_config = ""
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            current_config = f.read()
            
    if is_dark:
        new_config = """[theme]
base="dark"
primaryColor="#2563eb"
backgroundColor="#0f172a"
secondaryBackgroundColor="#1e293b"
textColor="#f8fafc"
font="sans serif"
"""
    else:
        new_config = """[theme]
base="light"
primaryColor="#1d4ed8"
backgroundColor="#f8fafc"
secondaryBackgroundColor="#f1f5f9"
textColor="#0f172a"
font="sans serif"
"""
    if current_config != new_config:
        with open(config_path, "w") as f:
            f.write(new_config)
            
# Default to checking session state for theme
if 'is_dark_theme' not in st.session_state:
    st.session_state.is_dark_theme = True
    set_theme(True)

if 'sms_logs' not in st.session_state:
    st.session_state.sms_logs = []

# MOBILE-FIRST: Use default centered layout, not wide
st.set_page_config(page_title="Bus Booking", layout="centered", initial_sidebar_state="collapsed")

# Add SMS API Setting in Sidebar
st.sidebar.markdown("#### ⚙️ SMS API Settings")
st.sidebar.caption("Provide a [Greenweb BD](http://api.greenweb.com.bd/) or BulkSMSBD token to send real SMS. Without this, SMS is simulated.")
user_sms_token = st.sidebar.text_input(
    "API Token (Optional)", 
    type="password", 
    value=os.environ.get("GREENWEB_API_TOKEN", ""),
    help="Paste your Greenweb API token here for live SMS sending."
)
if user_sms_token:
    os.environ["GREENWEB_API_TOKEN"] = user_sms_token

# ==========================================
#   MOBILE-FIRST CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Compact header */
    .app-header {
        padding: 1rem 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, var(--primary-color), #1e40af);
        color: #ffffff;
        text-align: center;
    }
    .app-header h2 {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .app-header p {
        margin: 0.25rem 0 0 0;
        opacity: 0.85;
        font-size: 0.8rem;
    }
    
    /* Step tracker - compact pills */
    .step-pills {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
        justify-content: center;
    }
    .pill {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.35rem 0.75rem;
        border-radius: 20px;
        white-space: nowrap;
    }
    .pill.active {
        background-color: var(--primary-color);
        color: #fff;
    }
    .pill.inactive {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        opacity: 0.5;
    }
    
    /* Quick Book cards */
    .qb-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.15s ease;
    }
    .qb-card:hover {
        border-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(37,99,235,0.15);
    }
    .qb-card .route-name {
        font-weight: 700;
        font-size: 1rem;
        margin-bottom: 0.3rem;
    }
    .qb-card .route-meta {
        font-size: 0.8rem;
        opacity: 0.7;
        display: flex;
        gap: 1rem;
    }
    
    /* Bus selection cards */
    .bus-select-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.5rem;
    }
    
    /* Touch-friendly buttons */
    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
        min-height: 44px;
        transition: all 0.15s;
        font-size: 0.9rem;
    }
    
    /* Forms */
    [data-testid="stForm"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* Prevent seat grid from stacking on mobile */
    @media (max-width: 768px) {
        div[data-testid="stVerticalBlock"]:has(> div > div > .seat-marker) > div > div > [data-testid="stHorizontalBlock"],
        div:has(> .seat-marker) [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 4px !important;
        }
        
        div:has(> .seat-marker) .stButton button {
            min-height: 40px !important;
            padding: 0 !important;
            font-size: 0.75rem !important;
        }
    }

    /* Mobile overrides */
    @media (max-width: 768px) {
        .stButton button {
            min-height: 48px !important;
            font-size: 0.85rem !important;
        }
        
        .app-header h2 {
            font-size: 1.1rem;
        }
        
        /* Bigger inputs on mobile */
        input, textarea, select {
            font-size: 16px !important; /* Prevents iOS zoom */
        }
        
        .step-pills {
            gap: 0.3rem;
        }
        .pill {
            font-size: 0.65rem;
            padding: 0.25rem 0.5rem;
        }
    }
    
    .stDataFrame {
        overflow-x: auto;
    }
    
    /* Metric cards compact */
    [data-testid="stMetric"] {
        background: var(--secondary-background-color);
        border-radius: 8px;
        padding: 0.75rem;
        border: 1px solid rgba(128,128,128,0.1);
    }

</style>
""", unsafe_allow_html=True)

# ==========================================
#   HEADER + THEME TOGGLE (Compact)
# ==========================================
h_col1, h_col2 = st.columns([8, 1])
with h_col2:
    if st.session_state.is_dark_theme:
        if st.button(":material/light_mode:", help="Light Theme"):
            st.session_state.is_dark_theme = False
            set_theme(False)
            st.rerun()
    else:
        if st.button(":material/dark_mode:", help="Dark Theme"):
            st.session_state.is_dark_theme = True
            set_theme(True)
            st.rerun()

with h_col1:
    st.markdown("""
    <div class="app-header">
        <h2>Bus Booking System</h2>
        <p>Quick Ticketing & SMS Dispatch</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
#   SMS CONFIG BAR (Always visible, compact)
# ==========================================
with st.expander("SMS & Notifications", expanded=False):
    sms_col1, sms_col2 = st.columns([3, 1])
    with sms_col1:
        sms_token = st.text_input(
            "API Token",
            type="password",
            help="Leave blank for Simulated Mode",
            label_visibility="collapsed",
            placeholder="Enter SMS API token or leave blank for simulation"
        )
    with sms_col2:
        if sms_token:
            st.success("Live SMS")
        else:
            st.info("Simulation")
    
    # Show SMS logs inline
    if st.session_state.sms_logs:
        st.caption(f"{len(st.session_state.sms_logs)} simulated message(s) sent")
        for i, log in enumerate(reversed(st.session_state.sms_logs[-3:])):
            with st.popover(f"View SMS to {log['phone']}", use_container_width=True):
                st.markdown(f"""
                <div style="background: #f0f2f5; border-radius: 16px; padding: 12px; border: 3px solid #444; max-width: 280px; margin: auto;">
                    <div style="text-align: center; font-size: 10px; color: #888; margin-bottom: 8px;">SMS Preview</div>
                    <div style="background: #dcf8c6; padding: 10px; border-radius: 10px 10px 0 10px; font-size: 12px; color: #000; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
                        {log['message'].replace(chr(10), '<br>')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
#   TABS
# ==========================================
tab1, tab2 = st.tabs(["Book", "History"])

# ==========================================
#   TAB 1: BOOKING
# ==========================================
with tab1:
    # Session State Initialization
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'selected_route' not in st.session_state:
        st.session_state.selected_route = None
    if 'travel_date' not in st.session_state:
        st.session_state.travel_date = datetime.now().date()
    if 'selected_schedule' not in st.session_state:
        st.session_state.selected_schedule = None
    if 'selected_seats' not in st.session_state:
        st.session_state.selected_seats = []
    if 'customer_phone' not in st.session_state:
        st.session_state.customer_phone = ""
    if 'customer_name' not in st.session_state:
        st.session_state.customer_name = ""
    if 'customer_address' not in st.session_state:
        st.session_state.customer_address = ""
    if 'autofill_done' not in st.session_state:
        st.session_state.autofill_done = False

    # Step Tracker (compact pills)
    s1 = "pill active" if st.session_state.step == 1 else "pill inactive"
    s2 = "pill active" if st.session_state.step == 2 else "pill inactive"
    s3 = "pill active" if st.session_state.step == 3 else "pill inactive"
    
    st.markdown(f"""
    <div class="step-pills">
        <div class="{s1}">1. Route</div>
        <div class="{s2}">2. Bus</div>
        <div class="{s3}">3. Book</div>
    </div>
    """, unsafe_allow_html=True)

    # ---- STEP 1: Route Selection with Quick Book ----
    if st.session_state.step == 1:
        routes = database.get_routes()
        
        if not routes:
            st.warning("No bus schedules found. Initializing defaults...")
            import setup_schedules
            setup_schedules.setup()
            routes = database.get_routes()

        # --- QUICK BOOK: Popular Routes ---
        st.markdown("#### Quick Book")
        popular = database.get_popular_routes(limit=3)
        
        for pr in popular:
            fare_text = f"From BDT {int(pr['min_fare']):,}" if pr['min_fare'] and pr['min_fare'] > 0 else ""
            bookings_text = f"{pr['booking_count']} bookings" if pr['booking_count'] > 0 else "New route"
            
            qb_col1, qb_col2 = st.columns([4, 1])
            with qb_col1:
                st.markdown(f"""
                <div class="qb-card">
                    <div class="route-name">{pr['route']}</div>
                    <div class="route-meta">
                        <span>{fare_text}</span>
                        <span>Next: {pr['next_departure']}</span>
                        <span>{bookings_text}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with qb_col2:
                if st.button("Book", key=f"qb_{pr['route']}", type="primary", use_container_width=True):
                    st.session_state.selected_route = pr['route']
                    st.session_state.travel_date = datetime.now().date()
                    st.session_state.step = 2
                    st.session_state.selected_schedule = None
                    st.session_state.selected_seats = []
                    st.rerun()
        
        # --- Full Route Selection ---
        st.markdown("---")
        with st.expander("All Routes & Custom Date", expanded=False):
            route = st.selectbox(
                "Select Route", 
                routes, 
                index=routes.index(st.session_state.selected_route) if st.session_state.selected_route in routes else 0
            )
            travel_date = st.date_input("Travel Date", value=st.session_state.travel_date)
            
            if st.button("Select Route", type="primary", use_container_width=True):
                st.session_state.selected_route = route
                st.session_state.travel_date = travel_date
                st.session_state.step = 2
                st.session_state.selected_schedule = None
                st.session_state.selected_seats = []
                st.rerun()

    # ---- STEP 2: Bus Selection (Stacked Cards) ----
    elif st.session_state.step == 2:
        st.markdown(f"**{st.session_state.selected_route}** | {st.session_state.travel_date}")
        
        schedules = database.get_schedules_by_route(st.session_state.selected_route)
        
        if not schedules:
            st.warning("No buses available for this route.")
        else:
            for sched in schedules:
                booked_count = database.get_booked_seat_count(sched['schedule_id'], str(st.session_state.travel_date))
                total = sched['total_seats']
                available = total - booked_count
                fare = sched.get('base_fare', 0)
                
                # Stacked card layout (mobile-friendly)
                with st.container():
                    st.markdown(f"""
                    <div class="bus-select-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <div style="font-weight: 700; font-size: 1rem;">{sched['bus_name']}</div>
                                <div style="font-size: 0.85rem; opacity: 0.7; margin-top: 2px;">
                                    Departure: {sched['departure_time']}
                                    {f' | BDT {fare:,.0f}' if fare > 0 else ''}
                                </div>
                            </div>
                            <div style="text-align: right;">
                                {'<span style="color: #ef4444; font-weight: 700;">FULL</span>' if available == 0 else f'<span style="color: {"#f97316" if available <= 10 else "#22c55e"}; font-weight: 700;">{available}/{total}</span>'}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(
                        f"Select {sched['bus_name']} - {sched['departure_time']}", 
                        key=f"sel_bus_{sched['schedule_id']}", 
                        disabled=(available == 0),
                        use_container_width=True
                    ):
                        st.session_state.selected_schedule = sched
                        st.session_state.step = 3
                        st.session_state.selected_seats = []
                        st.session_state.autofill_done = False
                        st.rerun()
        
        st.write("")
        if st.button("Back", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

    # ---- STEP 3: Seat Selection & Passenger Info ----
    elif st.session_state.step == 3:
        sched = st.session_state.selected_schedule
        booked_seats = database.get_booked_seats(sched['schedule_id'], str(st.session_state.travel_date))
        
        st.markdown(f"**{sched['bus_name']}** | {st.session_state.selected_route} | {sched['departure_time']}")
        
        # Build all seat info
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        all_seats = [f"{r}{c}" for r in rows for c in [1, 2, 3, 4]]
        available_seats = [s for s in all_seats if s not in booked_seats]
        
        # Seat selection via multiselect (works perfectly on mobile)
        selected = st.multiselect(
            "Tap to select seats",
            options=available_seats,
            default=[s for s in st.session_state.selected_seats if s in available_seats],
            key="seat_multiselect"
        )
        st.session_state.selected_seats = selected
        
        # --- Pure HTML Bus Visual ---
        seat_html_rows = ""
        for r in rows:
            cells = ""
            for j, col in enumerate([1, 2, 3, 4]):
                s = f"{r}{col}"
                if s in booked_seats:
                    cls = "seat booked"
                    label = f"X"
                elif s in st.session_state.selected_seats:
                    cls = "seat selected"
                    label = f"●"
                else:
                    cls = "seat available"
                    label = s
                
                cells += f'<div class="{cls}">{label}</div>'
                if j == 1:
                    cells += '<div class="aisle"></div>'
            
            seat_html_rows += f'<div class="seat-row">{cells}</div>'
        
        bus_html = f"""
        <div style="max-width: 280px; margin: 10px auto; border: 2px solid #555; border-radius: 20px 20px 10px 10px; padding: 10px 15px 15px 15px; background: rgba(128,128,128,0.05);">
            <div style="text-align: center; font-weight: 700; font-size: 0.85rem; padding: 6px 0; border-bottom: 2px dashed #888; margin-bottom: 8px;">🚌 DRIVER</div>
            <style>
                .seat-row {{ display: flex; justify-content: center; gap: 6px; margin-bottom: 5px; }}
                .seat {{ width: 42px; height: 36px; display: flex; align-items: center; justify-content: center;
                         border-radius: 6px; font-size: 0.75rem; font-weight: 600; border: 1.5px solid #666; }}
                .seat.available {{ background: rgba(128,128,128,0.1); color: var(--text-color, #ccc); }}
                .seat.booked {{ background: rgba(239,68,68,0.2); color: #ef4444; border-color: #ef4444; }}
                .seat.selected {{ background: rgba(37,99,235,0.8); color: #fff; border-color: #2563eb; }}
                .aisle {{ width: 20px; }}
            </style>
            {seat_html_rows}
            <div style="display: flex; justify-content: center; gap: 12px; margin-top: 10px; font-size: 0.7rem; opacity: 0.8;">
                <span>⬜ Available</span>
                <span style="color: #ef4444;">❌ Booked</span>
                <span style="color: #2563eb;">🔵 Selected</span>
            </div>
        </div>
        """
        st.markdown(bus_html, unsafe_allow_html=True)
        
        st.write("")
        if st.button("Back to Buses", use_container_width=True):
            st.session_state.step = 2
            st.rerun()

        if st.session_state.selected_seats:
            seats_str = ", ".join(st.session_state.selected_seats)
            st.success(f"Seats: {seats_str}")
            st.markdown("---")
            
            # --- Auto-fill returning customer ---
            phone_lookup = st.text_input(
                "Phone (auto-fill)",
                value=st.session_state.customer_phone,
                key="phone_lookup_input",
                placeholder="e.g. 01712345678",
                max_chars=11
            )
            
            if phone_lookup and phone_lookup != st.session_state.customer_phone:
                st.session_state.customer_phone = phone_lookup
                existing = database.get_customer(phone_lookup)
                if existing:
                    st.session_state.customer_name = existing['name']
                    st.session_state.customer_address = existing['address'] or ""
                    st.session_state.autofill_done = True
                    st.rerun()
            
            if st.session_state.autofill_done:
                st.success(f"Returning customer: {st.session_state.customer_name}")
                st.session_state.autofill_done = False
            
            # Booking form (single column for mobile)
            with st.form("booking_form", clear_on_submit=False):
                phone = st.text_input(
                    "Mobile Phone", 
                    value=st.session_state.customer_phone,
                    placeholder="Required for SMS",
                    max_chars=11
                )
                name = st.text_input(
                    "Passenger Name", 
                    value=st.session_state.customer_name
                )
                address = st.text_input(
                    "Address (Optional)", 
                    value=st.session_state.customer_address
                )
                
                # Fare and payment
                default_fare = int(sched.get('base_fare', 0)) if sched.get('base_fare', 0) > 0 else 1500
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    price = st.number_input("Fare (BDT)", min_value=0, step=50, value=default_fare)
                with f_col2:
                    payment_status = st.selectbox("Payment", ["Paid", "Unpaid", "Partial"])
                
                ticket_format = st.radio("Ticket Format", ["Standard", "Expanded (with seat map)"], horizontal=True)
                
                submitted = st.form_submit_button("Confirm Booking", type="primary", use_container_width=True)
                
                if submitted:
                    clean_phone = phone.strip()
                    if not clean_phone or not name.strip() or price <= 0:
                        st.error("Please fill Phone, Name, and Fare.")
                    elif len(clean_phone) != 11 or not clean_phone.isdigit():
                        st.error("Please enter a valid 11-digit phone number (e.g. 01712345678).")
                    else:
                        try:
                            database.save_customer(clean_phone, name, address)
                            
                            generated_pdfs = []
                            booked_ids = []
                            last_sms_text = ""
                            
                            for seat in st.session_state.selected_seats:
                                booking_id = database.save_booking(
                                    phone=clean_phone,
                                    schedule_id=sched['schedule_id'],
                                    seat_number=seat,
                                    travel_date=str(st.session_state.travel_date),
                                    price=price,
                                    payment_status=payment_status
                                )
                                booked_ids.append(f"TKT{booking_id}")
                                
                                pdf_path = pdf_generator.generate_ticket(
                                    booking_id=booking_id,
                                    name=name,
                                    phone=phone,
                                    address=address,
                                    bus_name=sched['bus_name'],
                                    route=sched['route'],
                                    departure_time=sched['departure_time'],
                                    seat_number=seat,
                                    travel_date=str(st.session_state.travel_date),
                                    price=price,
                                    payment_status=payment_status,
                                    ticket_type=ticket_format.split(" ")[0]
                                )
                                generated_pdfs.append(pdf_path)
                                
                                sms_res = sms_service.send_booking_sms(
                                    phone_number=clean_phone,
                                    customer_name=name,
                                    ticket_id=booking_id,
                                    bus_name=sched['bus_name'],
                                    seat_number=seat,
                                    travel_date=str(st.session_state.travel_date),
                                    departure_time=sched['departure_time'],
                                    price=price,
                                    api_token=sms_token if sms_token else None
                                )
                                
                                last_sms_text = f"Hello {name}, your ticket is Confirmed!\nTicket ID: TKT{booking_id}\nBus: {sched['bus_name']}\nSeat: {seat}\nDate: {st.session_state.travel_date} ({sched['departure_time']})\nFare: BDT {price}\nThank you for choosing us!"
                            
                            if not sms_token:
                                st.session_state.sms_logs.append({
                                    "phone": clean_phone,
                                    "message": last_sms_text
                                })
                            
                            ids_str = ", ".join(booked_ids)
                            st.success(f"Booked! Tickets: {ids_str}")
                            
                            if sms_res.get("mock"):
                                st.info(f"SMS simulated to {clean_phone}")
                            elif sms_res.get("success"):
                                st.success(f"SMS sent to {clean_phone}")
                            else:
                                st.warning(f"SMS failed: {sms_res.get('message')}")
                                
                            st.markdown("#### SMS Preview")
                            st.info(last_sms_text)
                                
                            st.session_state.latest_pdfs = generated_pdfs
                            st.session_state.selected_seats = []
                            st.session_state.customer_phone = ""
                            st.session_state.customer_name = ""
                            st.session_state.customer_address = ""
                            
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            # Download buttons and ticket preview
            if st.session_state.get('latest_pdfs'):
                st.markdown("---")
                st.markdown("#### Tickets")
                
                last_booking = None
                if all_bookings := database.get_all_bookings():
                    for b in all_bookings:
                        if b['phone_number'] == st.session_state.get('customer_phone', ''):
                            last_booking = b
                            break
                    if not last_booking:
                        last_booking = all_bookings[0]
                
                for idx, pdf_path in enumerate(st.session_state.latest_pdfs):
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                            
                        ticket_name = os.path.basename(pdf_path).split('_')[0]
                        
                        # Compact ticket card
                        st.markdown(f"""
                        <div style="background: var(--secondary-background-color); padding: 12px; border-radius: 10px; border-left: 4px solid var(--primary-color); margin-bottom: 8px; border: 1px solid rgba(128,128,128,0.15);">
                            <div style="font-weight: 700; margin-bottom: 4px;">{ticket_name}</div>
                            <div style="font-size: 0.85rem; opacity: 0.8;">
                                {last_booking['customer_name'] if last_booking else 'N/A'} |
                                Seat {last_booking['seat_number'] if last_booking else 'N/A'} |
                                {last_booking['route'] if last_booking else 'N/A'}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.download_button(
                            label=f"Download {ticket_name}",
                            data=pdf_bytes,
                            file_name=os.path.basename(pdf_path),
                            mime='application/pdf',
                            type="primary",
                            key=f"dl_btn_{idx}",
                            use_container_width=True
                        )
                        
                        import base64
                        b64 = base64.b64encode(pdf_bytes).decode('utf-8')
                        st.markdown(f"""
                        <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                            <a href="data:application/pdf;base64,{b64}" target="_blank" style="flex: 1; text-align: center; padding: 10px; background-color: var(--secondary-background-color); color: var(--text-color); border: 1px solid rgba(128,128,128,0.3); border-radius: 8px; text-decoration: none; font-weight: 600;">🖨️ Print / Open in Browser</a>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        try:
                            import fitz
                            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            st.markdown("##### PDF Preview")
                            for page_num in range(len(doc)):
                                page = doc.load_page(page_num)
                                pix = page.get_pixmap(dpi=120)
                                st.image(pix.tobytes("png"), use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not render PDF preview: {e}")

# ==========================================
#   TAB 2: BOOKING HISTORY
# ==========================================
with tab2:
    st.markdown("#### History & Finance")
    all_bookings = database.get_all_bookings()
    
    if all_bookings:
        df = pd.DataFrame(all_bookings)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Search (full width)
        search_query = st.text_input(
            "Search",
            placeholder="Ticket ID, Name, or Phone",
            key="search_bookings"
        )
        search_status = st.selectbox("Status Filter", ["All", "Booked", "Cancelled"], key="search_status")
        
        # Apply search filters
        filtered_df = df.copy()
        
        if search_query.strip():
            q = search_query.strip().lower()
            mask = (
                filtered_df['booking_id'].astype(str).str.contains(q.replace("tkt", ""), case=False) |
                filtered_df['customer_name'].str.contains(q, case=False, na=False) |
                filtered_df['phone_number'].str.contains(q, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        if search_status != "All":
            filtered_df = filtered_df[filtered_df['status'] == search_status]
        
        # Date range
        min_date = df['created_at'].min().date()
        max_date = df['created_at'].max().date()
        selected_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        
        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            mask = (filtered_df['created_at'].dt.date >= start_date) & (filtered_df['created_at'].dt.date <= end_date)
            filtered_df = filtered_df.loc[mask]
        
        # Revenue metrics (2x2 grid)
        total_revenue = filtered_df['price'].sum()
        booked_df = filtered_df[filtered_df['status'] != 'Cancelled'] if 'status' in filtered_df.columns else filtered_df
        cancelled_df = filtered_df[filtered_df['status'] == 'Cancelled'] if 'status' in filtered_df.columns else pd.DataFrame()
        total_refunds = cancelled_df['refund_amount'].sum() if not cancelled_df.empty and 'refund_amount' in cancelled_df.columns else 0
        net_revenue = total_revenue - total_refunds
        active_bookings = len(booked_df)
        
        m1, m2 = st.columns(2)
        m1.metric("Active", active_bookings)
        m2.metric("Net Revenue", f"BDT {net_revenue:,.0f}")
        
        m3, m4 = st.columns(2)
        m3.metric("Gross", f"BDT {total_revenue:,.0f}")
        m4.metric("Refunds", f"BDT {total_refunds:,.0f}")
        
        # Cancel ticket
        st.markdown("---")
        st.markdown("#### Cancel Ticket")
        cancel_id_raw = st.text_input("Ticket ID (e.g. TKT1026)", key="cancel_input")
        refund_amt = st.number_input("Refund Amount (BDT)", min_value=0.0, step=50.0, value=0.0)
        
        if st.button("Cancel Ticket", type="primary", use_container_width=True):
            if cancel_id_raw.upper().startswith("TKT"):
                try:
                    b_id = int(cancel_id_raw.upper().replace("TKT", ""))
                    result = database.cancel_booking(b_id, refund_amount=refund_amt)
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                except ValueError:
                    st.error("Invalid Ticket ID format.")
            else:
                st.error("Enter a valid Ticket ID starting with 'TKT'.")

        st.markdown("---")
        if st.button("Export Report (PDF)", use_container_width=True):
            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                s_date = selected_dates[0].strftime("%Y-%m-%d")
                e_date = selected_dates[1].strftime("%Y-%m-%d")
            else:
                s_date = min_date.strftime("%Y-%m-%d")
                e_date = max_date.strftime("%Y-%m-%d")
                
            report_path = pdf_generator.generate_history_report(filtered_df, s_date, e_date, total_revenue)
            
            with open(report_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Report",
                    data=pdf_file.read(),
                    file_name=os.path.basename(report_path),
                    mime='application/pdf',
                    use_container_width=True
                )
        
        st.markdown("---")
        st.dataframe(
            filtered_df[['booking_id', 'customer_name', 'phone_number', 'bus_name', 'route', 'seat_number', 'travel_date', 'price', 'payment_status', 'status', 'created_at']],
            column_config={
                "booking_id": "Ticket",
                "customer_name": "Customer",
                "phone_number": "Phone",
                "bus_name": "Bus",
                "route": "Route",
                "seat_number": "Seat",
                "travel_date": "Date",
                "price": st.column_config.NumberColumn("Fare", format="%.0f"),
                "payment_status": "Payment",
                "status": "Status",
                "created_at": st.column_config.DatetimeColumn("Booked", format="MMM DD HH:mm")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Refund History
        if not cancelled_df.empty and 'refund_amount' in cancelled_df.columns:
            st.markdown("---")
            st.markdown("#### Refund History")
            st.metric("Total Refunded", f"BDT {total_refunds:,.0f}")
            
            st.dataframe(
                cancelled_df[['booking_id', 'customer_name', 'phone_number', 'price', 'refund_amount', 'refund_date']],
                column_config={
                    "booking_id": "Ticket",
                    "customer_name": "Customer",
                    "phone_number": "Phone",
                    "price": st.column_config.NumberColumn("Fare", format="%.0f"),
                    "refund_amount": st.column_config.NumberColumn("Refund", format="%.0f"),
                    "refund_date": st.column_config.DatetimeColumn("Date", format="MMM DD HH:mm")
                },
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info("No bookings yet.")

# ==========================================
#   SIDEBAR (Overview only)
# ==========================================
with st.sidebar:
    st.markdown("**Overview**")
    total_b = len(database.get_all_bookings())
    st.metric("Total Bookings", total_b)
