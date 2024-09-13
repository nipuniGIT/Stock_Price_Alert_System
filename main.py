from email.mime.multipart import MIMEMultipart
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
from email.mime.text import MIMEText


def scraper(url, data, headers):
    float_price = None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f'Request status: {response.status_code}')
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        with open('temp.html', 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        
        scraped_price = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'}).text
        matched = re.search(r'\d+.\d+', scraped_price).group()
        float_price = float(matched.strip())
        print(f'Float Price Value: {float_price}')
    except Exception as e:
        print(e)
    
    return float_price


def dataReconciliation(scraped_price, file_path):
    try:
        df = pd.read_csv(file_path)
        aapl_df = df[df['Company'] == 'AAPL']
        
        # Fix FutureWarning
        appl_price = float(aapl_df['Price'].iloc[0])
        print(f'Appl Price: {appl_price}')
        
        if scraped_price > appl_price:
            print(f'Minimum price: {appl_price} for appl_price')
            percentage = ((scraped_price - appl_price) / appl_price) * 100
            print(f'Increased Percentage: {percentage} %')
        else:
            print(f'Minimum price: {scraped_price} for scraped_price')
            
        emailAlert(scraped_price, appl_price)

    except Exception as e:
        print(f'Error: {e}')


def emailAlert(scraped_price, appl_price):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'nscapture99@gmail.com'
    smtp_password = 'pwd'  

    sender_email = 'nscapture99@gmail.com'
    recipient_email = 'ulnipunishanika18tec@gmail.com'
    subject = 'Stock Price Alert'

    current_price = scraped_price
    previous_price = appl_price
    price_difference = current_price - previous_price
    threshold = 0.00  # Adjust threshold as needed

    if abs(price_difference) > threshold:
        body = (f"Stock Price Notification:\n\n"
                f"Current Price: ${current_price:.2f}\n"
                f"Previous Price: ${previous_price:.2f}\n"
                f"Price Difference: ${price_difference:.2f}\n\n"
                f"Threshold: ${threshold:.2f}\n\n"
                f"Action Required: The price difference exceeds the threshold.")

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f'Email sent successfully to {recipient_email}.')
        except Exception as e:
            print(f'Error sending email: {e}')
    else:
        print('Price difference does not exceed the threshold. No email sent.')


if __name__ == "__main__":
    url = 'https://finance.yahoo.com/quote/AAPL?p=AAPL'
    data = {
        'p': 'AAPL'
    }
    headers = {
        'authority': 'finance.yahoo.com',
        'path': '/quote/AAPL?p=AAPL',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }

    # Correct variable name
    scraped_price = scraper(url, data, headers)

    file_path = 'input/stock_data.csv'
    dataReconciliation(scraped_price, file_path)
