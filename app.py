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
        email_password = "icjd xvpn jebj nmuf"  
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = email_recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  
            server.login(email_sender, email_password)
            text = msg.as_string()
            server.sendmail(email_sender, email_recipient, text)
        
        print("Notification sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname1 = request.form['uname1']
        email = request.form['email']
        upswd1 = request.form['upswd1']
        upswd2 = request.form['upswd2']

        conn = get_db_connection()
        cursor = conn.cursor()
       
        cursor.execute("INSERT INTO register (uname1, email, upswd1, upswd2) VALUES (%s, %s, %s, %s)",
                       (uname1, email, upswd1, upswd2))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Registration successful!", 'success')
        return redirect(url_for('login'))

    return render_template('register.html')  

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname1 = request.form['uname1']
        upswd1 = request.form['upswd1']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT upswd1 FROM register WHERE uname1 = %s LIMIT 1", (uname1,))
        stored_password = cursor.fetchone()

        if stored_password:
            if upswd1 == stored_password[0]:  
                session['logged_in'] = True
                session['username'] = uname1
                flash("Login successful!", 'success')
                cursor.close()
                conn.close()
                return redirect(url_for('dashboard')) 
            else:
                flash("Incorrect username or password.", 'error')
        else:
            flash("Incorrect username or password.", 'error')

        cursor.close()
        conn.close()

    return render_template('login.html') 

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        flash("You must be logged in to access the dashboard.", 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT cardNumber, cardName, amount FROM card")  
    account_data = cursor.fetchall() 

    cursor.execute("SELECT id, cardNumber, goal, transactionType, amount, transactionDate FROM transaction")
    transactions = cursor.fetchall() 

    cursor.execute("SELECT id, bill_name, item_description, due_date, amount FROM bills")
    bills = cursor.fetchall()  

    today = datetime.today().date()
    upcoming_bills_count = sum(
        1 for bill in bills if today <= bill[3] <= today + timedelta(days=3)
    )
    today = datetime.today().date() 
    for bill in bills:
        due_date = bill[3]
        bill_name = bill[1]
        amount = bill[4]

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


    graph_url = generate_expenses_graph()

    username = session['username']
    cursor.execute("SELECT id FROM register WHERE uname1 = %s", (username,))
    user_id = cursor.fetchone()[0]

    cursor.execute("SELECT goal_name, target_amount, current_amount, achieved FROM goals WHERE user_id = %s", (user_id,))
    active_goal = cursor.fetchone()

    username = session.get('username') 


    cursor.close()
    conn.close()

    return render_template('dashboard.html', accounts=account_data,transactions=transactions,bills=bills,graph_url=graph_url,upcoming_bills_count=upcoming_bills_count,active_goal=active_goal,username=username)

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
    return redirect('/dashboard') 

@app.route('/delete_account/<card_number>', methods=['POST'])
def delete_account(card_number):
    if not session.get('logged_in'):
        flash("You must be logged in to perform this action.", 'error')
        return redirect(url_for('login'))

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

    card_number = request.form['cardNumber']
    transaction_type = request.form['transactionType']  
    amount = Decimal(request.form['amount'])  
    transaction_date = request.form['transactionDate']
    goal = request.form['goal']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM card WHERE cardNumber = %s", (card_number,))
    card = cursor.fetchone()

    if not card:
        flash("Card number not found!", 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard'))

    current_balance = Decimal(card[0])

    if transaction_type == 'credit':
        new_balance = current_balance + amount  
    elif transaction_type == 'debit':
        if current_balance >= amount:
            new_balance = current_balance - amount  
        else:
            flash("Insufficient funds!", 'error')
            cursor.close()
            conn.close()
            return redirect(url_for('dashboard'))

    cursor.execute("""
        INSERT INTO transaction (cardNumber, goal, transactionType, amount, transactionDate) 
        VALUES (%s, %s, %s, %s, %s)
    """, (card_number, goal, transaction_type, amount, transaction_date))
    conn.commit()

    cursor.execute("UPDATE card SET amount = %s WHERE cardNumber = %s", (new_balance, card_number))
    conn.commit()

    if transaction_type == 'credit' and goal:
        cursor.execute("""
            UPDATE goals
            SET current_amount = current_amount + %s,
               achieved = CASE WHEN current_amount + %s >= target_amount THEN 1 ELSE 0 END
            WHERE goal_name = %s AND achieved = 0
        """, (amount, amount, goal))
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

    transaction_id = request.form.get('transaction_id')

    if not transaction_id:
        flash("No transaction selected for deletion.", 'error')
        return redirect(url_for('dashboard'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transaction WHERE id = %s", (transaction_id,))
        conn.commit()
        flash("Transaction deleted successfully!", 'success')
    except Exception as e:
        conn.rollback()
        flash(f"Error deleting transaction: {e}", 'error')
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('dashboard'))

@app.route('/add_bill', methods=['POST'])
def add_bill():
    if not session.get('logged_in'):
        flash("You must be logged in to perform this action.", 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    bill_name = request.form['bill_name']
    item_description = request.form['item_description']
    due_date = request.form['due_date']
    amount = request.form['amount']
    
    cursor.execute("INSERT INTO bills (bill_name, item_description, due_date, amount) VALUES (%s, %s, %s, %s)",
                (bill_name, item_description, due_date, amount))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('dashboard'))

@app.route('/delete_selected_bills', methods=['POST'])
def delete_selected_bills():
    selected_bill_ids = request.form.getlist('bill_ids')
    
    if selected_bill_ids:
        cur = mysql.connection.cursor()
        ids_to_delete = ','.join(selected_bill_ids)
        query = f"DELETE FROM bills WHERE id IN ({ids_to_delete})"
        cur.execute(query)
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('dashboard'))

def generate_expenses_graph():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT goal, SUM(amount) 
        FROM transaction 
        WHERE transactionType = 'debit' 
        GROUP BY goal
    """)
    data = cursor.fetchall()

    if not data:
        return None

    df = pd.DataFrame(data, columns=["Expense Category", "Total Amount"])

    fig, ax = plt.subplots()
    ax.pie(df["Total Amount"], labels=df["Expense Category"], autopct='%1.1f%%', startangle=90)
    ax.axis('equal') 
    ax.set_title('Expense Breakdown by Category')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)

    graph_url = base64.b64encode(img.getvalue()).decode('utf-8')

    cursor.close()
    conn.close()

    return graph_url

@app.route('/get_upcoming_bills', methods=['GET'])
def get_upcoming_bills():
    conn = get_db_connection()
    cursor = conn.cursor()

    today = datetime.today()
    cursor.execute("""
        SELECT bill_name, due_date, amount 
        FROM bills 
        WHERE due_date BETWEEN %s AND %s
    """, (today, today + timedelta(days=3)))
    bills = cursor.fetchall()

    formatted_bills = [
        {"bill_name": bill[0], "due_date": bill[1].strftime('%Y-%m-%d'), "amount": float(bill[2])}
        for bill in bills
    ]

    cursor.close()
    conn.close()

    return {"bills": formatted_bills}

@app.route('/set_goal', methods=['POST'])
def set_goal():
    if not session.get('logged_in'):
        flash("You must be logged in to set a goal.", 'error')
        return redirect(url_for('login'))

    goal_name = request.form['goal_name']
    target_amount = request.form['target_amount']
    
    username = session['username']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM register WHERE uname1 = %s", (username,))
    user_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO goals (user_id, goal_name, target_amount) 
        VALUES (%s, %s, %s)
    """, (user_id, goal_name, target_amount))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Goal set successfully!", 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear() 
    flash("Logged out successfully.", 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)