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

st.set_page_config(page_title="Travel Agency Booking System", layout="wide")

# Custom Modern CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .header-container {
        background-color: var(--secondary-background-color);
        padding: 2rem;
        border-radius: 8px;
        color: var(--text-color);
        margin-bottom: 2rem;
        border: 1px solid var(--primary-color);
        border-left: 6px solid var(--primary-color);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--text-color) !important;
    }
    
    .header-container p {
        margin: 0.5rem 0 0 0;
        opacity: 0.8;
        font-size: 0.95rem;
    }
    
    .stepper {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid var(--secondary-background-color);
        padding-bottom: 1rem;
    }
    .step {
        font-size: 0.9rem;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        transition: all 0.2s ease;
    }
    .step.active {
        background-color: var(--primary-color);
        color: #ffffff;
    }
    .step.inactive {
        color: var(--text-color);
        opacity: 0.6;
        background-color: transparent;
    }

    @media (max-width: 768px) {
        [data-testid="stHorizontalBlock"] {
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            gap: 4px !important;
        }
        .stButton button {
            padding: 0.4rem 0.2rem !important;
            font-size: 0.75rem !important;
            min-height: 44px !important;
            min-width: 0 !important;
        }
        .header-container {
            padding: 1.25rem;
        }
        .header-container h1 {
            font-size: 1.4rem;
        }
        .stepper {
            flex-direction: column;
            gap: 0.5rem;
        }
    }
    
    .stDataFrame {
        overflow-x: auto;
    }
    
    div.stButton > button {
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    [data-testid="stForm"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    /* Bus card styling */
    .bus-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar with Theme Toggle
t_col1, t_col2 = st.columns([9, 1])
with t_col2:
    if st.session_state.is_dark_theme:
        if st.button(":material/light_mode:", help="Switch to Light Theme"):
            st.session_state.is_dark_theme = False
            set_theme(False)
            st.rerun()
    else:
        if st.button(":material/dark_mode:", help="Switch to Dark Theme"):
            st.session_state.is_dark_theme = True
            set_theme(True)
            st.rerun()

# Application Header
with t_col1:
    st.markdown("""
    <div class="header-container">
        <h1>Travel Agency Management System</h1>
        <p>Professional Ticketing, Automated PDF Generation, and SMS Dispatching</p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("System Settings")
    st.subheader("SMS Configuration")
    sms_token = st.text_input(
        "API Gateway Token",
        type="password",
        help="Leave blank to use Simulated Mode (Logs to console)."
    )
    if sms_token:
        st.success("Real SMS Enabled")
    else:
        st.info("Simulated SMS Mode")
        
    st.divider()
    st.markdown("**Overview**")
    total_b = len(database.get_all_bookings())
    st.metric("Total Bookings", total_b)

tab1, tab2 = st.tabs(["New Booking", "Booking History"])

# ==========================================
#   TAB 1: NEW BOOKING
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

    # Visual Step Tracker
    s1_cls = "step active" if st.session_state.step == 1 else "step inactive"
    s2_cls = "step active" if st.session_state.step == 2 else "step inactive"
    s3_cls = "step active" if st.session_state.step == 3 else "step inactive"
    
    st.markdown(f"""
    <div class="stepper">
        <div class="{s1_cls}">Step 1: Route Configuration</div>
        <div class="{s2_cls}">Step 2: Fleet Selection</div>
        <div class="{s3_cls}">Step 3: Seat & Passenger Allocation</div>
    </div>
    """, unsafe_allow_html=True)

    # ---- STEP 1: Select Route and Date ----
    if st.session_state.step == 1:
        st.subheader("Route Configuration")
        routes = database.get_routes()
        
        if not routes:
            st.warning("No bus schedules found in database. Initializing default schedules...")
            import setup_schedules
            setup_schedules.setup()
            routes = database.get_routes()

        col1, col2 = st.columns(2)
        with col1:
            route = st.selectbox(
                "Select Route", 
                routes, 
                index=routes.index(st.session_state.selected_route) if st.session_state.selected_route in routes else 0
            )
        with col2:
            travel_date = st.date_input("Travel Date", value=st.session_state.travel_date)
            
        st.write("")
        if st.button("Proceed to Fleet Selection", type="primary"):
            st.session_state.selected_route = route
            st.session_state.travel_date = travel_date
            st.session_state.step = 2
            st.session_state.selected_schedule = None
            st.session_state.selected_seats = []
            st.rerun()

    # ---- STEP 2: Select Bus (with seat availability count) ----
    elif st.session_state.step == 2:
        st.subheader("Fleet Selection")
        st.markdown(f"**Route:** {st.session_state.selected_route} | **Date:** {st.session_state.travel_date}")
        
        schedules = database.get_schedules_by_route(st.session_state.selected_route)
        
        if not schedules:
            st.warning("No fleets available for this route.")
        else:
            for sched in schedules:
                booked_count = database.get_booked_seat_count(sched['schedule_id'], str(st.session_state.travel_date))
                total = sched['total_seats']
                available = total - booked_count
                fare = sched.get('base_fare', 0)
                
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
                    c1.markdown(f"**{sched['bus_name']}**")
                    c2.markdown(f"Departure: **{sched['departure_time']}**")
                    
                    # Color-code availability
                    if available == 0:
                        c3.markdown(f":red[**FULL** (0/{total})]")
                    elif available <= 10:
                        c3.markdown(f":orange[**{available}/{total}** Available]")
                    else:
                        c3.markdown(f":green[**{available}/{total}** Available]")
                    
                    if fare > 0:
                        c4.markdown(f"Fare: **BDT {fare:,.0f}**")
                    
                    if c5.button("Select", key=f"sel_bus_{sched['schedule_id']}", disabled=(available == 0)):
                        st.session_state.selected_schedule = sched
                        st.session_state.step = 3
                        st.session_state.selected_seats = []
                        st.session_state.autofill_done = False
                        st.rerun()
                        
        st.write("")
        if st.button("Back to Route Configuration"):
            st.session_state.step = 1
            st.rerun()

    # ---- STEP 3: Seat Selection & Passenger Info ----
    elif st.session_state.step == 3:
        st.subheader("Seat Allocation")
        
        sched = st.session_state.selected_schedule
        booked_seats = database.get_booked_seats(sched['schedule_id'], str(st.session_state.travel_date))
        
        st.info(f"Route: {st.session_state.selected_route} | Fleet: {sched['bus_name']} | Departure: {sched['departure_time']}")
        
        # Legend
        l1, l2, l3, l4 = st.columns(4)
        l1.markdown("`[   ]` Available")
        l2.markdown("`[ X ]` Booked")
        l3.markdown("`[ O ]` Selected")
        st.write("")
        
        # Seat Grid layout (2x2 with aisle)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for r in rows:
            cols = st.columns([1, 1, 0.4, 1, 1])
            seats_in_row = [f"{r}1", f"{r}2", f"{r}3", f"{r}4"]
            col_indices = [0, 1, 3, 4]
            
            for seat, col_idx in zip(seats_in_row, col_indices):
                is_booked = seat in booked_seats
                is_selected = (seat in st.session_state.selected_seats)
                
                label = f"{seat}"
                if is_booked:
                    label = f"X {seat}"
                elif is_selected:
                    label = f"O {seat}"
                    
                btn_type = "primary" if is_selected else "secondary"
                
                if cols[col_idx].button(
                    label, 
                    key=f"seat_{seat}", 
                    disabled=is_booked, 
                    type=btn_type,
                    use_container_width=True
                ):
                    if seat in st.session_state.selected_seats:
                        st.session_state.selected_seats.remove(seat)
                    else:
                        st.session_state.selected_seats.append(seat)
                    st.rerun()
        
        st.write("")
        if st.button("Back to Fleet Selection"):
            st.session_state.step = 2
            st.rerun()

        if st.session_state.selected_seats:
            seats_str = ", ".join(st.session_state.selected_seats)
            st.success(f"Seats Allocated: {seats_str}")
            st.markdown("---")
            st.subheader("Passenger Information")
            
            # --- FEATURE #1: Auto-fill returning customer ---
            phone_lookup = st.text_input(
                "Phone Number (type and press Enter to auto-fill)",
                value=st.session_state.customer_phone,
                key="phone_lookup_input",
                placeholder="e.g. 01712345678"
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
                st.success(f"Returning customer found: {st.session_state.customer_name}")
                st.session_state.autofill_done = False
            
            # Booking form
            with st.form("booking_form", clear_on_submit=False):
                p_col1, p_col2 = st.columns(2)
                
                with p_col1:
                    phone = st.text_input(
                        "Mobile Phone Number", 
                        value=st.session_state.customer_phone,
                        placeholder="Required for SMS"
                    )
                    name = st.text_input(
                        "Passenger Full Name", 
                        value=st.session_state.customer_name
                    )
                    
                with p_col2:
                    address = st.text_area(
                        "Address / Destination", 
                        value=st.session_state.customer_address, 
                        height=100
                    )
                
                f_col1, f_col2 = st.columns(2)
                with f_col1:
                    # --- FEATURE #5: Route-based fare auto-fill ---
                    default_fare = int(sched.get('base_fare', 0)) if sched.get('base_fare', 0) > 0 else 1500
                    price = st.number_input("Ticket Fare (BDT)", min_value=0, step=50, value=default_fare)
                with f_col2:
                    payment_status = st.selectbox("Payment Status", ["Paid", "Unpaid", "Partial"])
                
                submitted = st.form_submit_button("Confirm Booking & Generate Tickets", type="primary", use_container_width=True)
                
                if submitted:
                    if not phone.strip() or not name.strip() or price <= 0:
                        st.error("Error: Please complete all required fields (Phone, Name, and Fare must be greater than 0).")
                    else:
                        try:
                            database.save_customer(phone, name, address)
                            
                            generated_pdfs = []
                            booked_ids = []
                            
                            for seat in st.session_state.selected_seats:
                                booking_id = database.save_booking(
                                    phone=phone,
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
                                    payment_status=payment_status
                                )
                                generated_pdfs.append(pdf_path)
                                
                                sms_res = sms_service.send_booking_sms(
                                    phone_number=phone,
                                    customer_name=name,
                                    ticket_id=booking_id,
                                    bus_name=sched['bus_name'],
                                    seat_number=seat,
                                    travel_date=str(st.session_state.travel_date),
                                    departure_time=sched['departure_time'],
                                    price=price,
                                    api_token=sms_token if sms_token else None
                                )
                            
                            ids_str = ", ".join(booked_ids)
                            st.success(f"Transaction Successful. Ticket Identifiers: {ids_str}")
                            
                            if sms_res.get("mock"):
                                st.info(f"SMS Notification (Simulated): Dispatched to {phone}")
                            elif sms_res.get("success"):
                                st.success(f"SMS Notification Sent: Real SMS delivered to {phone}")
                            else:
                                st.warning(f"SMS Delivery Exception: {sms_res.get('message')}")
                                
                            st.session_state.latest_pdfs = generated_pdfs
                            st.session_state.selected_seats = []
                            st.session_state.customer_phone = ""
                            st.session_state.customer_name = ""
                            st.session_state.customer_address = ""
                            
                        except Exception as e:
                            st.error(f"Transaction failed due to system error: {e}")
            
            # Download buttons outside the form
            if st.session_state.get('latest_pdfs'):
                st.markdown("### Download Tickets")
                dl_cols = st.columns(min(len(st.session_state.latest_pdfs), 4))
                for idx, pdf_path in enumerate(st.session_state.latest_pdfs):
                    col = dl_cols[idx % len(dl_cols)]
                    if os.path.exists(pdf_path):
                        with open(pdf_path, "rb") as pdf_file:
                            col.download_button(
                                label=f"Download {os.path.basename(pdf_path).split('_')[0]}",
                                data=pdf_file.read(),
                                file_name=os.path.basename(pdf_path),
                                mime='application/pdf',
                                type="primary",
                                key=f"dl_btn_{idx}"
                            )

# ==========================================
#   TAB 2: BOOKING HISTORY
# ==========================================
with tab2:
    st.header("Financial Overview & History")
    all_bookings = database.get_all_bookings()
    
    if all_bookings:
        df = pd.DataFrame(all_bookings)
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # --- FEATURE #3: Booking Search / Ticket Lookup ---
        st.subheader("Search Bookings")
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input(
                "Search by Ticket ID, Customer Name, or Phone Number",
                placeholder="e.g. TKT1026, Karim, 01712345678",
                key="search_bookings"
            )
        with search_col2:
            search_status = st.selectbox("Filter by Status", ["All", "Booked", "Cancelled"], key="search_status")
        
        st.write("---")
        
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
        
        # Date range filter
        st.subheader("Report Filters")
        min_date = df['created_at'].min().date()
        max_date = df['created_at'].max().date()
        
        selected_dates = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        
        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = selected_dates
            mask = (filtered_df['created_at'].dt.date >= start_date) & (filtered_df['created_at'].dt.date <= end_date)
            filtered_df = filtered_df.loc[mask]
        
        # --- FEATURE #7: Net Revenue (Gross - Refunds) ---
        total_revenue = filtered_df['price'].sum()
        total_bookings = len(filtered_df)
        booked_df = filtered_df[filtered_df['status'] != 'Cancelled'] if 'status' in filtered_df.columns else filtered_df
        cancelled_df = filtered_df[filtered_df['status'] == 'Cancelled'] if 'status' in filtered_df.columns else pd.DataFrame()
        total_refunds = cancelled_df['refund_amount'].sum() if not cancelled_df.empty and 'refund_amount' in cancelled_df.columns else 0
        net_revenue = total_revenue - total_refunds
        active_bookings = len(booked_df)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Active Bookings", active_bookings)
        m2.metric("Gross Revenue", f"BDT {total_revenue:,.2f}")
        m3.metric("Total Refunds", f"BDT {total_refunds:,.2f}")
        m4.metric("Net Revenue", f"BDT {net_revenue:,.2f}")
        
        # --- FEATURE #8: Cancellation with Double-Cancel Guard ---
        st.subheader("Manage Bookings")
        col_c1, col_c2, col_c3 = st.columns([2, 2, 1])
        with col_c1:
            cancel_id_raw = st.text_input("Enter Ticket ID to Cancel (e.g., TKT1026)", key="cancel_input")
        with col_c2:
            refund_amt = st.number_input("Refund Amount (BDT)", min_value=0.0, step=50.0, value=0.0)
        with col_c3:
            st.write("")
            st.write("")
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
                        st.error("Invalid Ticket ID format. Use TKT followed by numbers.")
                else:
                    st.error("Please enter a valid Ticket ID starting with 'TKT'.")

        st.write("---")
        if st.button("Export Financial Report (PDF)", type="secondary"):
            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
                s_date = selected_dates[0].strftime("%Y-%m-%d")
                e_date = selected_dates[1].strftime("%Y-%m-%d")
            else:
                s_date = min_date.strftime("%Y-%m-%d")
                e_date = max_date.strftime("%Y-%m-%d")
                
            report_path = pdf_generator.generate_history_report(filtered_df, s_date, e_date, total_revenue)
            
            with open(report_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Report PDF",
                    data=pdf_file.read(),
                    file_name=os.path.basename(report_path),
                    mime='application/pdf'
                )
        st.write("---")
        
        st.dataframe(
            filtered_df[['booking_id', 'customer_name', 'phone_number', 'bus_name', 'route', 'departure_time', 'seat_number', 'travel_date', 'price', 'payment_status', 'status', 'created_at']],
            column_config={
                "booking_id": "Ticket ID",
                "customer_name": "Customer",
                "phone_number": "Phone Number",
                "bus_name": "Fleet",
                "route": "Route",
                "departure_time": "Time",
                "seat_number": "Seat",
                "travel_date": "Travel Date",
                "price": st.column_config.NumberColumn("Fare (BDT)", format="%.2f"),
                "payment_status": "Payment",
                "status": "Status",
                "created_at": st.column_config.DatetimeColumn("Transaction Date", format="YYYY-MM-DD HH:mm")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # --- REFUND HISTORY SECTION ---
        st.write("---")
        st.subheader("Refund History")
        if not cancelled_df.empty and 'refund_amount' in cancelled_df.columns:
            st.metric("Total Issued Refunds", f"BDT {total_refunds:,.2f}")
            
            st.dataframe(
                cancelled_df[['booking_id', 'customer_name', 'phone_number', 'price', 'refund_amount', 'refund_date']],
                column_config={
                    "booking_id": "Ticket ID",
                    "customer_name": "Customer",
                    "phone_number": "Phone Number",
                    "price": st.column_config.NumberColumn("Original Fare", format="%.2f"),
                    "refund_amount": st.column_config.NumberColumn("Refunded Amount", format="%.2f"),
                    "refund_date": st.column_config.DatetimeColumn("Refund Date", format="YYYY-MM-DD HH:mm")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No refunds issued in this date range.")
    else:
        st.info("No transaction records found.")
