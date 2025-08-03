from extensions import db
from models import Quote
from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, redirect, url_for, send_file
from fpdf import FPDF
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    quotes = Quote.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', quotes=quotes)

@main_bp.route('/add_quote', methods=['GET', 'POST'])
@login_required
def add_quote():
    if request.method == 'POST':
        client = request.form['client']
        service = request.form['service']
        price = float(request.form['price'])
        new_quote = Quote(client=client, service=service, price=price, user_id=current_user.id)
        db.session.add(new_quote)
        db.session.commit()
        return redirect(url_for('main.dashboard'))  # Runs if POST
    return render_template('generate.html')  # Runs if GET

@main_bp.route('/delete_quote', methods=['POST'])
@login_required
def delete_quote(quote_id):
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()
    db.session.delete(quote)
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main_bp.route('/generate_pdf/<int:quote_id>')
@login_required
def generate_pdf(quote_id):
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()

    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Color palette
    soft_slate = (75, 85, 99)
    misty_blue = (115, 151, 176)
    warm_light = (255, 251, 243)
    dark_text = (17, 24, 39)
    muted_gray = (99, 102, 106)

    pdf.set_fill_color(*warm_light)
    pdf.rect(0, 0, 210, 297, style='F')

    margin_left = 25
    margin_right = 25
    container_width = 210 - margin_left - margin_right

    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(*muted_gray)
    pdf.set_xy(210 - margin_right - 40, 15)
    pdf.cell(40, 10, datetime.today().strftime('%B %d, %Y'), align='R')

    pdf.set_xy(margin_left, 30)
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(*soft_slate)
    pdf.cell(container_width, 12, "Quote", ln=True, align='C')

    pdf.set_draw_color(*misty_blue)
    pdf.set_line_width(0.5)
    pdf.line(margin_left, 45, 210 - margin_right, 45)
    pdf.ln(15)

    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*soft_slate)
    pdf.cell(35, 10, "Client:")
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(*dark_text)
    pdf.cell(0, 10, quote.client, ln=1)

    pdf.ln(6)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*soft_slate)
    pdf.cell(35, 10, "Service:")
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(*dark_text)
    pdf.cell(0, 10, quote.service, ln=1)

    pdf.ln(6)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*soft_slate)
    pdf.cell(35, 10, "Price:")
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(*dark_text)
    pdf.cell(0, 10, f"${float(quote.price):,.2f}", ln=1)

    pdf.ln(20)
    pdf.set_font("Arial", 'I', 11)
    pdf.set_text_color(*muted_gray)
    pdf.multi_cell(0, 8, "Thank you for choosing our services.", align='C')

    pdf_path = f"quote_{quote.client.replace(' ', '_')}.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

'''quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id,).first_or_404()

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Quote", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Client: {quote.client}", ln=True)
    pdf.cell(200, 10, txt=f"Service: {quote.service}", ln=True)
    pdf.cell(200, 10, txt=f"Price: ${float(quote.price):.2f}", ln=True)
    # Save PDF to a temp file (or use BytesIO for in-memory)
    pdf_path = f"quote_{quote.client.replace(' ', '_')}.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()

    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=25)

    # Define color palette
    soft_slate = (75, 85, 99)  # #4B5563
    misty_blue = (115, 151, 176)  # #7397B0
    warm_light = (255, 251, 243)  # #FFFBF3
    dark_text = (17, 24, 39)  # #111827
    muted_gray = (99, 102, 106)  # #63666A

    # Background
    pdf.set_fill_color(*warm_light)
    pdf.rect(0, 0, 210, 297, style='F')

    # Margins
    margin_left = 25
    margin_right = 25
    container_width = 210 - margin_left - margin_right

    # Date (top right)
    from datetime import datetime
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(*muted_gray)
    pdf.set_xy(210 - margin_right - 40, 15)
    pdf.cell(40, 10, datetime.today().strftime('%B %d, %Y'), align='R')

    # Title
    pdf.set_xy(margin_left, 30)
    pdf.set_font("Arial", 'B', 24)
    pdf.set_text_color(*soft_slate)
    pdf.cell(container_width, 12, "Quote", ln=True, align='C')

    # Divider
    pdf.set_draw_color(*misty_blue)
    pdf.set_line_width(0.5)
    pdf.line(margin_left, 45, 210 - margin_right, 45)

    pdf.ln(15)

    # Client
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*soft_slate)
    pdf.cell(35, 10, "Client:")
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(*dark_text)
    pdf.cell(0, 10, quote.client, ln=1)

    pdf.ln(6)

    # Service
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*soft_slate)
    pdf.cell(35, 10, "Service:")
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(*dark_text)
    pdf.cell(0, 10, quote.service, ln=1)

    pdf.ln(6)

    # Price (right-aligned)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(*soft_slate)
    pdf.cell(35, 10, "Price:")
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(*dark_text)
    pdf.cell(0, 10, f"${float(quote.price):,.2f}", ln=1)

    pdf.ln(20)

    # Footer message
    pdf.set_font("Arial", 'I', 11)
    pdf.set_text_color(*muted_gray)
    pdf.multi_cell(0, 8,
                   "Thank you for choosing our services.", align='C')

    # Output file
    pdf_path = f"quote_{quote.client.replace(' ', '_')}.pdf"
    pdf.output(pdf_path)

    return send_file(pdf_path, as_attachment=True)'''