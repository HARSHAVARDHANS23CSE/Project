from flask import Flask, render_template, request, redirect, url_for, flash, session
import re  
import mysql.connector
import secrets
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
from decimal import Decimal
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)  

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="intern"
    )

def send_email(subject, body, email_recipient):
    """Send an email notification."""
    try:
        email_sender = "amirthaamirtha788@gmail.com" 
        email_password = "icjd xvpn jebj nmuf"  # Your email password (use App Passwords if using Gmail)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(email_sender, email_password)
            text = msg.as_string()
            server.sendmail(email_sender, email_recipient, text)
        
        print("Notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname1 = request.form['uname1']
        email = request.form['email']
        upswd1 = request.form['upswd1']
        upswd2 = request.form['upswd2']

        # Input validation
        if not uname1 or not email or not upswd1 or not upswd2:
            flash("All fields are required!", 'error')
            return render_template('register.html')

        if upswd1 != upswd2:
            flash("Passwords do not match!", 'error')
            return render_template('register.html')

        # Validate email format
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            flash("Invalid email format!", 'error')
            return render_template('register.html')

        # Connect to DB and check if email exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM register WHERE email = %s LIMIT 1", (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            flash("This email is already registered!", 'error')
            cursor.close()
            conn.close()
            return render_template('register.html')

        # Insert into the database
        cursor.execute("INSERT INTO register (uname1, email, upswd1, upswd2) VALUES (%s, %s, %s, %s)",
                       (uname1, email, upswd1, upswd2))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful!", 'success')
        return redirect(url_for('login'))

    return render_template('register.html')  # Render the registration page


# Route for user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname1 = request.form['uname1']
        upswd1 = request.form['upswd1']

        # Input validation
        if not uname1 or not upswd1:
            flash("Username and Password are required.", 'error')
            return render_template('login.html')

        # Check credentials in DB
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT upswd1 FROM register WHERE uname1 = %s LIMIT 1", (uname1,))
        stored_password = cursor.fetchone()

        if stored_password:
            # Check if entered password matches stored one (Use hashing for better security)
            if upswd1 == stored_password[0]:  # Assuming plain-text for simplicity
                session['logged_in'] = True
                session['username'] = uname1
                flash("Login successful!", 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('dashboard'))  # Redirect to dashboard page
            else:
                flash("Incorrect username or password.", 'error')
        else:
            flash("Incorrect username or password.", 'error')

        cursor.close()
        conn.close()

    return render_template('login.html')  # Render the login page


# Route for dashboard (After successful login)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        flash("You must be logged in to access the dashboard.", 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all account data from the database
    cursor.execute("SELECT cardNumber, cardName, amount FROM card")  # Fetch all accounts
    account_data = cursor.fetchall()  # Fetch all rows as a list of tuples

    # Get all transaction data
    cursor.execute("SELECT id, cardNumber, goal, transactionType, amount, transactionDate FROM transaction")
    transactions = cursor.fetchall()  # Fetch all rows

    cursor.execute("SELECT id, bill_name, item_description, due_date, amount FROM bills")
    bills = cursor.fetchall()  # Fetch all rows

     # Check for upcoming bills (due within the next 3 days)
    today = datetime.today().date()
    upcoming_bills_count = sum(
        1 for bill in bills if today <= bill[3] <= today + timedelta(days=3)
    )
     # Check for upcoming bills and send notifications
    today = datetime.today().date()  # Convert to datetime.date
    for bill in bills:
        due_date = bill[3]
        bill_name = bill[1]
        amount = bill[4]

        # Fetch user's email (assuming bills are linked to users via session)
        cursor.execute("SELECT email FROM register WHERE uname1 = %s", (session['username'],))
        user_email = cursor.fetchone()[0]

        if due_date <= today + timedelta(days=3) and due_date >= today:
            subject = f"Upcoming Bill Due: {bill_name}"
            body = f"""
            Dear {session['username']},

            Your bill '{bill_name}' for ${amount:.2f} is due on {due_date.strftime('%Y-%m-%d')}.
            Please ensure payment is completed to avoid any penalties.

            Best regards,
            Your Finance App Team
            """
            send_email(subject, body, user_email)


    # Generate the graph for expenses
    graph_url = generate_expenses_graph()

    cursor.close()
    conn.close()

    user_id = session.get('user_id')
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the current active goal
    cursor.execute("""
        SELECT goal_name, target_amount, current_amount, achieved 
        FROM goals 
        WHERE user_id = %s AND achieved = 0
    """, (user_id,))
    active_goal = cursor.fetchone()

    # Fetch other necessary data for the dashboard
    # ...

    cursor.close()
    conn.close()

    # Render dashboard template with the fetched account details
    return render_template('dashboard.html', accounts=account_data,transactions=transactions,bills=bills,graph_url=graph_url,upcoming_bills_count=upcoming_bills_count,active_goal=active_goal)


# Add Account Route (existing form functionality)
@app.route('/add_account', methods=['POST'])
def add_account():
    if not session.get('logged_in'):
        flash("You must be logged in to add an account.", 'error')
        return redirect(url_for('login'))

    card_number = request.form['cardNumber']
    card_name = request.form['cardName']
    expiry_date = request.form['expiryDate']
    cvv = request.form['cvv']
    amount = request.form['amount']

    # Insert into the database (add account info)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO card (cardNumber, cardName, expiryDate, cvv, amount) 
        VALUES (%s, %s, %s, %s, %s)
    """, (card_number, card_name, expiry_date, cvv, amount))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Account added successfully!", 'success')
    return redirect('/dashboard')  # Redirect back to the dashboard after adding the account

@app.route('/delete_account/<card_number>', methods=['POST'])
def delete_account(card_number):
    if not session.get('logged_in'):
        flash("You must be logged in to perform this action.", 'error')
        return redirect(url_for('login'))

    # Delete the account from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM card WHERE cardNumber = %s", (card_number,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Account deleted successfully!", 'success')
    return redirect(url_for('dashboard'))


@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    if not session.get('logged_in'):
        flash("You must be logged in to perform this action.", 'error')
        return redirect(url_for('login'))

    # Get the transaction details from the form
    card_number = request.form['cardNumber']
    transaction_type = request.form['transactionType']  # 'credit' or 'debit'
    amount = Decimal(request.form['amount'])  # Convert to Decimal for accuracy
    transaction_date = request.form['transactionDate']
    goal = request.form['goal']

    # Check if card exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM card WHERE cardNumber = %s", (card_number,))
    card = cursor.fetchone()

    if not card:
        flash("Card number not found!", 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard'))

    # Convert the database balance to Decimal
    current_balance = Decimal(card[0])

    # Update the balance based on the transaction type
    if transaction_type == 'credit':
        new_balance = current_balance + amount  # Adding to balance for credit
    elif transaction_type == 'debit':
        if current_balance >= amount:
            new_balance = current_balance - amount  # Subtracting from balance for debit
        else:
            flash("Insufficient funds!", 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))

    # Insert the transaction into the transaction table
    cursor.execute("""
        INSERT INTO transaction (cardNumber, goal, transactionType, amount, transactionDate) 
        VALUES (%s, %s, %s, %s, %s)
    """, (card_number, goal, transaction_type, amount, transaction_date))
    conn.commit()

    # Update the balance in the card table
    cursor.execute("UPDATE card SET amount = %s WHERE cardNumber = %s", (new_balance, card_number))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Transaction added successfully!", 'success')
    return redirect(url_for('dashboard'))

@app.route('/delete_selected_transactions', methods=['POST'])
def delete_selected_transactions():
    if not session.get('logged_in'):
        flash("You must be logged in to perform this action.", 'error')
        return redirect(url_for('login'))

    # Get selected transaction IDs from the form
    selected_ids = request.form.getlist('transaction_ids')  # List of selected transaction IDs

    if selected_ids:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Delete selected transactions
        cursor.execute("DELETE FROM transaction WHERE id IN (%s)" % ','.join(['%s'] * len(selected_ids)), selected_ids)
        conn.commit()

         # Reset the auto-increment value for 'id' after deletion
        cursor.execute("ALTER TABLE transaction AUTO_INCREMENT = 1")
        conn.commit()
        
        cursor.close()
        conn.close()

        flash("Selected transactions deleted successfully!", 'success')
    else:
        flash("No transactions selected for deletion.", 'error')

    return redirect(url_for('dashboard'))

@app.route('/add_bill', methods=['POST'])
def add_bill():
    if not session.get('logged_in'):
        flash("You must be logged in to perform this action.", 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Get form data
    bill_name = request.form['bill_name']
    item_description = request.form['item_description']
    due_date = request.form['due_date']
    amount = request.form['amount']
    
    # Insert the new bill into the database
    cursor.execute("INSERT INTO bills (bill_name, item_description, due_date, amount) VALUES (%s, %s, %s, %s)",
                (bill_name, item_description, due_date, amount))
    conn.commit()

    cursor.close()
    conn.close()

    # Redirect back to the main page after adding
    return redirect(url_for('dashboard'))

@app.route('/delete_selected_bills', methods=['POST'])
def delete_selected_bills():
    # Get the list of selected bill IDs
    selected_bill_ids = request.form.getlist('bill_ids')
    
    # If there are selected bills, delete them from the database
    if selected_bill_ids:
        cur = mysql.connection.cursor()
        ids_to_delete = ','.join(selected_bill_ids)
        query = f"DELETE FROM bills WHERE id IN ({ids_to_delete})"
        cur.execute(query)
        mysql.connection.commit()
        cur.close()

    # Redirect back to the main page after deletion
    return redirect(url_for('dashboard'))

# Function to generate a graph of expenses based on categories
def generate_expenses_graph():
    # Fetch transaction data from the database (grouped by goal for expense types)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT goal, SUM(amount) 
        FROM transaction 
        WHERE transactionType = 'debit' 
        GROUP BY goal
    """)
    data = cursor.fetchall()

    # If no data, return a default graph
    if not data:
        return None

    # Convert data into a DataFrame for easier manipulation
    df = pd.DataFrame(data, columns=["Expense Category", "Total Amount"])

    # Create a pie chart to represent the expenses by category
    fig, ax = plt.subplots()
    ax.pie(df["Total Amount"], labels=df["Expense Category"], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title('Expense Breakdown by Category')

    # Save the plot to a bytes buffer and convert to base64 for embedding in HTML
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    # Encode the image in base64 to embed in the HTML
    graph_url = base64.b64encode(img.getvalue()).decode('utf-8')

    cursor.close()
    conn.close()

    return graph_url

@app.route('/get_upcoming_bills', methods=['GET'])
def get_upcoming_bills():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get upcoming bills within the next 3 days
    today = datetime.today()
    cursor.execute("""
        SELECT bill_name, due_date, amount 
        FROM bills 
        WHERE due_date BETWEEN %s AND %s
    """, (today, today + timedelta(days=3)))
    bills = cursor.fetchall()

    # Format the bills as a list of dictionaries
    formatted_bills = [
        {"bill_name": bill[0], "due_date": bill[1].strftime('%Y-%m-%d'), "amount": float(bill[2])}
        for bill in bills
    ]

    cursor.close()
    conn.close()

    return {"bills": formatted_bills}

@app.route('/add_goal', methods=['POST'])
def add_goal():
    if not session.get('logged_in'):
        flash("You must be logged in to set a goal.", 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')  # Ensure this is set during login
    if not user_id:
        flash("User ID not found in session. Please log in again.", 'error')
        return redirect(url_for('login'))

    goal_name = request.form['goal_name']
    target_amount = Decimal(request.form['target_amount'])

    # Check if there's an active goal
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM goals WHERE user_id = %s AND achieved = 0", (user_id,))
    active_goal = cursor.fetchone()

    if active_goal:
        flash("You already have an active goal. Complete it before creating a new one.", 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard'))

    # Insert new goal into the database
    cursor.execute("""
        INSERT INTO goals (user_id, goal_name, target_amount, current_amount, achieved)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, goal_name, target_amount, 0, 0))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Goal added successfully!", 'success')
    return redirect(url_for('dashboard'))


@app.route('/update_goal_progress', methods=['POST'])
def update_goal_progress():
    if not session.get('logged_in'):
        flash("You must be logged in to perform this action.", 'error')
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    transaction_amount = Decimal(request.form['amount'])
    goal_name = request.form['goal']  # Name of the goal associated with the transaction

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch active goal matching the name
    cursor.execute("""
        SELECT id, current_amount, target_amount 
        FROM goals 
        WHERE user_id = %s AND goal_name = %s AND achieved = 0
    """, (user_id, goal_name))
    goal = cursor.fetchone()

    if not goal:
        flash("No active goal matches the transaction.", 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard'))

    # Update the goal's progress
    goal_id, current_amount, target_amount = goal
    new_current_amount = current_amount + transaction_amount

    cursor.execute("""
        UPDATE goals 
        SET current_amount = %s, achieved = %s 
        WHERE id = %s
    """, (new_current_amount, int(new_current_amount >= target_amount), goal_id))
    conn.commit()

    flash("Goal progress updated successfully!", 'success')
    cursor.close()
    conn.close()
    return redirect(url_for('dashboard'))


# Route for logging out
@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash("Logged out successfully.", 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
