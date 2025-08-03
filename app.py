from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from fpdf import FPDF
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))  # For demo, store hashed passwords in real apps

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client = db.Column(db.String(150))
    service = db.Column(db.String(150))
    price = db.Column(db.String(150))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add validation & password hashing in production
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            # Return login page with error message if login fails
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    quotes = Quote.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', quotes=quotes)

# Quote generation route (protected)
@app.route('/add_quote', methods=['GET', 'POST'])
@login_required
def add_quote():
    if request.method == 'POST':
        client = request.form['client']
        service = request.form['service']
        price = float(request.form['price'])

        # Save to database
        new_quote = Quote(client=client, service=service, price=price, user_id=current_user.id)
        db.session.add(new_quote)
        db.session.commit()
        # PDF generation code can come here (or separate route)
        return redirect(url_for('dashboard'))
    return render_template('generate.html')

@app.route('/generate_pdf/<int:quote_id>')
@login_required
def generate_pdf(quote_id):
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
    return send_file(pdf_path, as_attachment=True)'''

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

    return send_file(pdf_path, as_attachment=True)


@app.route('/delete_quote/<int:quote_id>', methods=['POST'])
@login_required
def delete_quote(quote_id):
    quote = Quote.query.filter_by(id=quote_id, user_id=current_user.id).first_or_404()
    db.session.delete(quote)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)