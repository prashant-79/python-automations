import boto3
import json
import datetime
import requests
from dateutil import parser

def send_slack_notification(message, webhook_url):
    payload = {"text": message}
    requests.post(webhook_url, json=payload)

def check_aws_key(reminder_days, webhook_url):
    iam = boto3.client('iam')
    today = datetime.datetime.now()

    users = iam.list_users()['Users']

    for user in users:
        username = user['UserName']
        access_keys = iam.list_access_keys(UserName=username)['AccessKeyMetadata']

        for key in access_keys:
            key_id = key['AccessKeyId']
            create_date = key['CreateDate']
            age_days = (today - create_date.replace(tzinfo=None)).days
            expiry_days = 90 - age_days

            if expiry_days <= reminder_days:
                msg = f"🔐 AWS Key for *{username}* will expire in {expiry_days} days. ({key_id})"
                send_slack_notification(msg, webhook_url)

def main():
    with open('config.json') as f:
        config = json.load(f)

    check_aws_key(
        reminder_days=config['reminder_days'],
        webhook_url=config['slack_webhook']
    )

if __name__ == "__main__":
    main()