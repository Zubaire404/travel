import os
from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        # Placeholder for Agency Logo/Name
        self.set_font("helvetica", "B", 20)
        self.set_text_color(33, 150, 243) # Blue
        self.cell(0, 10, "XYZ Travels & Tours", border=0, align="C", ln=1)
        self.set_font("helvetica", "I", 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, "Your Trusted Travel Partner", border=0, align="C", ln=1)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        # Handle fpdf2 or old fpdf page_no
        page_num = getattr(self, 'page_no', lambda: 1)()
        self.cell(0, 10, f"Page {page_num}", align="C")

def generate_ticket(booking_id, name, phone, address, bus_name, route, departure_time, seat_number, travel_date, price, payment_status, ticket_type="Standard"):
    # Ensure Tickets directory exists
    if not os.path.exists("Tickets"):
        os.makedirs("Tickets")

    pdf = PDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "BOOKING CONFIRMATION / TICKET", align="C", ln=1)
    pdf.ln(5)
    
    # Ticket & Date Info
    pdf.set_font("helvetica", "B", 12)
    ticket_str = f"TKT{booking_id}"
    pdf.cell(100, 8, f"Ticket ID: {ticket_str}")
    pdf.set_font("helvetica", "", 12)
    pdf.cell(90, 8, f"Issue Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="R", ln=1)
    pdf.ln(5)

    # Customer Details Box
    pdf.set_font("helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, " Passenger Details", border=1, fill=True, ln=1)
    
    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Name:", border="L")
    pdf.cell(150, 8, name, border="R", ln=1)
    
    pdf.cell(40, 8, "Phone Number:", border="L")
    pdf.cell(150, 8, phone, border="R", ln=1)
    
    pdf.cell(40, 8, "Address:", border="L, B")
    pdf.cell(150, 8, address if address else "N/A", border="R, B", ln=1)
    pdf.ln(5)

    # Travel Details Box
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, " Travel Details", border=1, fill=True, ln=1)
    
    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Bus Operator:", border="L")
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(150, 8, bus_name, border="R", ln=1)

    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Route:", border="L")
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(150, 8, route, border="R", ln=1)

    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Seat Number:", border="L")
    pdf.set_font("helvetica", "B", 11)
    pdf.set_text_color(220, 0, 0) # Highlight seat
    pdf.cell(150, 8, seat_number, border="R", ln=1)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Dep. Time:", border="L")
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(150, 8, f"{travel_date} | {departure_time}", border="R", ln=1)

    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "", border="L, B") # Empty bottom border line
    pdf.cell(150, 8, "", border="R, B", ln=1)
    pdf.ln(5)

    # Payment Details Box
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, " Payment Details", border=1, fill=True, ln=1)
    
    pdf.set_font("helvetica", "", 11)
    pdf.cell(40, 8, "Total Price:", border="L")
    pdf.cell(150, 8, f"BDT {price}", border="R", ln=1)
    
    pdf.cell(40, 8, "Payment Status:", border="L, B")
    
    # Color code status
    if payment_status.lower() == "paid":
        pdf.set_text_color(0, 150, 0)
    elif payment_status.lower() == "unpaid":
        pdf.set_text_color(255, 0, 0)
    else:
        pdf.set_text_color(200, 100, 0)
        
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(150, 8, payment_status.upper(), border="R, B", ln=1)
    pdf.set_text_color(0, 0, 0) # reset
    
    if ticket_type.lower() == "expanded":
        pdf.add_page()
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "Seat Map", align="C", ln=1)
        pdf.ln(5)
        
        # Bus Map parameters
        start_x = 60
        start_y = pdf.get_y()
        seat_w = 15
        seat_h = 15
        gap = 5
        aisle = 20
        
        pdf.set_font("helvetica", "", 10)
        
        # Draw front of bus
        pdf.set_xy(start_x, start_y)
        pdf.cell(seat_w*2 + aisle + seat_w*2 + gap*3, 10, "DRIVER", border=1, align="C")
        
        start_y += 15
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        for i, r in enumerate(rows):
            for j, col in enumerate([1, 2, 3, 4]):
                s_num = f"{r}{col}"
                # Calculate X position
                if j < 2:
                    curr_x = start_x + j * (seat_w + gap)
                else:
                    curr_x = start_x + 2 * (seat_w + gap) - gap + aisle + (j - 2) * (seat_w + gap)
                
                curr_y = start_y + i * (seat_h + gap)
                
                pdf.set_xy(curr_x, curr_y)
                if s_num == seat_number:
                    pdf.set_fill_color(33, 150, 243) # Blue selected
                    pdf.set_text_color(255, 255, 255)
                    pdf.cell(seat_w, seat_h, s_num, border=1, fill=True, align="C")
                    pdf.set_text_color(0, 0, 0)
                else:
                    pdf.cell(seat_w, seat_h, s_num, border=1, align="C")
        
        pdf.ln((len(rows) * (seat_h + gap)) + 10)
    
    pdf.ln(10)
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 10, "Thank you for booking with us! Have a safe journey.", align="C", ln=1)
    
    # Save PDF
    safe_name = name.replace(" ", "_")
    filename = f"Tickets/{ticket_str}_{safe_name}.pdf"
    pdf.output(filename)
    return filename

def generate_history_report(dataframe, start_date, end_date, total_revenue):
    if not os.path.exists("Reports"):
        os.makedirs("Reports")
        
    pdf = PDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, "BOOKING HISTORY REPORT", align="C", ln=1)
    pdf.ln(2)
    
    # Report Meta Info
    pdf.set_font("helvetica", "", 11)
    pdf.cell(0, 6, f"Generated On: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", ln=1)
    pdf.cell(0, 6, f"Period: {start_date} to {end_date}", align="C", ln=1)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 150, 0)
    pdf.cell(0, 8, f"Total Revenue: BDT {total_revenue:,.2f}", align="C", ln=1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    # Table Header
    # Columns: Ticket, Date, Bus, Seat, Name, Phone, Price, Status
    # Widths: 15, 20, 25, 10, 30, 25, 15, 15 => Total 155? Let's use 190 total (full width)
    # 20(TKT), 22(Date), 30(Bus), 15(Seat), 40(Name), 30(Phone), 18(Price), 15(Status) = 190
    col_widths = [20, 22, 28, 12, 38, 28, 22, 20]
    headers = ["Ticket", "Travel Date", "Bus", "Seat", "Passenger", "Phone", "Price", "Status"]
    
    pdf.set_font("helvetica", "B", 9)
    pdf.set_fill_color(220, 220, 220)
    for i in range(len(headers)):
        pdf.cell(col_widths[i], 8, headers[i], border=1, fill=True, align="C")
    pdf.ln(8)
    
    # Table Rows
    pdf.set_font("helvetica", "", 8)
    
    for index, row in dataframe.iterrows():
        # Clean text
        tkt = f"TKT{row['booking_id']}"
        date = str(row['travel_date'])
        bus = str(row['bus_name'])[:15] # truncate if too long
        seat = str(row['seat_number'])
        name = str(row['customer_name'])[:20]
        phone = str(row['phone_number'])
        price = str(row['price'])
        status = str(row['payment_status'])
        
        pdf.cell(col_widths[0], 6, tkt, border=1, align="C")
        pdf.cell(col_widths[1], 6, date, border=1, align="C")
        pdf.cell(col_widths[2], 6, bus, border=1, align="C")
        pdf.cell(col_widths[3], 6, seat, border=1, align="C")
        pdf.cell(col_widths[4], 6, name, border=1, align="L")
        pdf.cell(col_widths[5], 6, phone, border=1, align="C")
        pdf.cell(col_widths[6], 6, price, border=1, align="R")
        
        if status.lower() == "paid":
            pdf.set_text_color(0, 150, 0)
        elif status.lower() == "unpaid":
            pdf.set_text_color(255, 0, 0)
            
        pdf.cell(col_widths[7], 6, status, border=1, align="C")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(6)
        
    report_name = f"Reports/Booking_Report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(report_name)
    return report_name

