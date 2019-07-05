from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import csv

# TODO: Make it as a Classs
# TODO: Fix issue when there is no nextPageToken (last page) and it fails
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate():
    """
    Performs authentication based on the stored credentials.json file
    :return: credentials
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
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def get_message_data(service, message_id):
    email = service.users().messages().get(userId='me', id=message_id).execute()
    field_from, field_return, field_subject, field_date, field_internal_date = ('', '', '', '', '')
    for header in email['payload']['headers']:
        if header['name'] == 'From':
            field_from = header['value']
        elif header['name'] == 'Return-Path':
            field_return = header['value']
        elif header['name'] == 'Subject':
            field_subject = header['value']
        elif header['name'] == 'Date':
            field_date = header['value']
    field_internal_date = email.get('internalDate')
    field_labels = email.get('labelIds')
    if field_labels:
        field_labels = ''.join((separated+',' for separated in field_labels))[:-1]
    is_attachment = False
    if email['payload'].get('parts'):
        attachments = list(filter(lambda x: x.get('filename'), email['payload']['parts']))
        attachments = list(field['filename'] for field in attachments)
        if attachments:
            is_attachment = True
    return [field_date, field_internal_date, field_labels, field_from, field_return, field_subject, email.get('sizeEstimate'), is_attachment]


def messages(service):
    message_count = 500
    try:
        with open('.gexport', mode='r') as state_file:
            next_page = state_file.read()
            file_mode = 'a'
    except FileNotFoundError:
        next_page = ''
        file_mode = 'w'
    email_count = 0
    with open('emails.csv', mode=file_mode, newline='', encoding="utf-8") as export_file:
        export_writer = csv.writer(export_file, delimiter=';', quotechar="'", quoting=csv.QUOTE_MINIMAL)
        while message_count == 500:
            results = service.users().messages().list(userId='me', maxResults=500, pageToken=next_page).execute()
            message_count = len(results['messages'])
            email_count += message_count
            next_page = results.get('nextPageToken')
            for message in results['messages']:
                export_writer.writerow(get_message_data(service, message['id']))
            with open('.gexport', mode='w') as state_file:
                state_file.write(next_page)
                state_file.close()
            print(email_count)
        os.remove('.gexport')
    return email_count

def main():
    credentials = authenticate()
    service = build('gmail', 'v1', credentials=credentials)
    messages(service)


if __name__ == '__main__':
    main()
