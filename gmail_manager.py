import imaplib, re
import email
import datetime

SEARCH_MAILBOX = 'YOUR_BASECAMP_FOLDER' # foler name, e.g. 'Basecamp'
SEARCH_KEYWORD = 'YOUR_SEARCH_KEYWORD' 
IGNORE_KEYWORD = 'YOUR_IGNORE_KEYWORD'
EMAIL_ADDRESS = 'YOUR_EMAIL_ADDRESS'

# normal password is not accept, create application password for it
GMAIL_APPLICATION_PASSWORD = 'YOUR_APPLICATION_PASSWORD'


def connect(email):
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(email, GMAIL_APPLICATION_PASSWORD)
    return imap


def disconnect(imap):
    imap.logout()


def get_content(payload):
    content = ''
    if 'multipart' in payload.get_content_type():
        for sub_payload in payload.get_payload():
            content += get_content(sub_payload)
    if 'text' in payload.get_content_type():
        content = payload.get_payload()
    return content

if __name__ == '__main__':

    today_date = datetime.datetime.now().strftime("%d-%b-%Y")
    search_for = '(ON "%s")' % today_date

    print('**** Connent to %s' % EMAIL_ADDRESS)

    imap = connect(EMAIL_ADDRESS)
    imap.select(mailbox=SEARCH_MAILBOX, readonly=False)
    resp, items = imap.search(None, search_for, '(UNSEEN)')
    email_ids  = items[0].split()

    print('**** Got Basecamp %d emails today unread' % len(email_ids))

    related_email_no = 0
    action_count = 0
    for email_id in email_ids:
        resp, data = imap.fetch(email_id, "(RFC822)")
        selected_email = email.message_from_string(data[0][1])
        email_body = get_content(selected_email)

        # remove the email address and keyword
        email_body = email_body.lower().replace(EMAIL_ADDRESS, '')
        email_body = email_body.lower().replace(IGNORE_KEYWORD, '')

        if SEARCH_KEYWORD in email_body:
            related_email_no += 1

            # copy to inbox folder
            imap.copy(email_id, 'INBOX')

            # mark as unseen
            imap.store(email_id, '-FLAGS', '(\Seen)')
            status, msg = imap.expunge()
            if status == 'OK':
                action_count += 1

    print('**** total %d related to \'%s\'' % (related_email_no, SEARCH_KEYWORD))
    print('**** moved %d emails to INBOX' % action_count)
    print('**** Done!')

    disconnect(imap)
