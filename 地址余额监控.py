
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import time

# Configuration info
api_url = "https://api-era.zksync.network/api"  # Replace with the actual API endpoint if different
api_key = "api key"  # Replace with your actual API Key https://era.zksync.network这个网站申请api
contract_address = "0xBBeB516fb02a01611cBBE0453Fe3c580D7281011" # 监控的代币的合约地址
monitored_address = "0xc812Dda5c01f3B3E2eF6281e4CE6801C1B84226B" # 要监控的地址
max_balance = "100000"  # Maximum balance threshold as a raw string wei单位

# Email alert configuration
mail_host = "SMTP server domain"  # SMTP server domain
mail_port = 587  # SMTP server port, usually 587 or 465
mail_user = "发送邮箱"  # Sender email
mail_pass = "密码"  # Sender email password
mail_to = "接收提醒邮箱"  # Recipient email

def get_address_token_balance(api_url, contract_address, address, api_key):
    params = {
        "module": "account",
        "action": "tokenbalance",
        "contractaddress": contract_address,
        "address": address,
        "tag": "latest",
        "apikey": api_key
    }
    
    response = requests.get(api_url, params=params)
    response_json = response.json()
    print(response_json)  # Print API response for debugging
    
    if response.status_code == 200 and 'result' in response_json:
        balance_raw = response_json["result"]
        return balance_raw
    else:
        raise Exception(f"Error fetching balance: {response.status_code}, {response_json}")

def send_alert_email(mail_host, mail_port, mail_user, mail_pass, to, subject, content):
    message = MIMEMultipart('alternative')
    message['From'] = Header(mail_user, 'utf-8')
    message['To'] = Header(to, 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    
    part1 = MIMEText(content, 'plain', 'utf-8')
    message.attach(part1)
    
    try:
        with smtplib.SMTP(mail_host, mail_port) as smtpObj:
            smtpObj.starttls()
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(mail_user, [to], message.as_string())
            print("ok")
    except Exception as e:
        print(f"no: {str(e)}")
        
while True:
    try:
        balance_raw = get_address_token_balance(api_url, contract_address, monitored_address, api_key)
        print(f"Address {monitored_address} raw balance: {balance_raw}")

        if int(balance_raw) > int(max_balance):
            subject = f"Balance Alert for Address {monitored_address}"
            content = f"The balance {balance_raw} exceeds the limit of {max_balance}. Address: {monitored_address}"
            send_alert_email(mail_host, mail_port, mail_user, mail_pass, mail_to, subject, content)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
    time.sleep(60)  # Check every 60 seconds 几秒刷新一次
