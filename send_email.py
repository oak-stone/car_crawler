#!/usr/bin/python3
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import datetime
import app
import json

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

with open('email_recipients.json') as email_recipients_config:
  email_recipients_from_config = json.load(email_recipients_config)

sender = ''
#to = email_recipients.email_recipients
to = ''
bcc = email_recipients_from_config['email_recipients']
date = ((datetime.datetime.now()).strftime("%x"))
subject = ('Daily Motorbikes: ' + date)
transmission = ('automatic' if app.crawl_config['gearBox'] == '2' else 'manual')
#message_text = ('Today\'s check was run on cars from year ' + app.crawl_config['year'] + ' with ' + transmission + ' transmission, max price of ' + app.crawl_config['maxPrice'] + ('€ and look back window of ') + app.crawl_config['lookBackPeriod'] + ' day(s)\n\n' + str("\n".join("{}\t{}".format(k, v) for k, v in app.main().items())))
message_text = ('Today\'s check was run on motorbikes with min. power of ' + app.crawl_config['minPower'] + ' cm3, max price of ' + app.crawl_config['maxPriceMotorbike'] + ('€ and look back window of ') + app.crawl_config['lookBackPeriod'] + ' day(s)\n\n' + str("\n".join("{}\t{}".format(k, v) for k, v in app.main().items())))

def get_credentials():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    #service = build('gmail', 'v1', credentials=creds)
    return creds


def create_message(sender, to, bcc, subject, message_text):
  message = MIMEText(message_text)
  message['to'] = to
  message['Bcc'] = bcc
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
  #return {'raw': base64.urlsafe_b64encode(message.as_bytes())}
      

def send_message(service, message):
  try:
    message = (service.users().messages().send(userId='me', body=message).execute())
    print ('Message Id: %s' % message['id'])
    return message
  except any as error:
    print ('An error occurred: %s' % error)

if __name__ == '__main__':
  creds = get_credentials()
  service = build('gmail', 'v1', credentials=creds)
  message = create_message(sender, to, bcc, subject, message_text)
  send_message(service, message)
