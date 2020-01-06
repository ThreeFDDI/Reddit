#!/usr/local/bin/python3

import praw, time, os
import pickle
import os.path
import base64 
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def api_login():
    """
    Shows basic usage of the Gmail API.
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

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    """
    Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    message = message.as_string()

    message = base64.urlsafe_b64encode(message.encode('UTF-8')).decode('ascii')

    return {'raw': message}

def send_message(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                .execute())
        print(f"Message Id: {message['id']}")
        return message

    except HttpError as error:
        print(f"An error occurred: {error}")

# Reddit bot
def reddit_bot():
    # initialize reddit bot
    reddit = praw.Reddit('bot1')
    # set subreddit to monitor
    subreddit = reddit.subreddit("gundeals")
    # initialize list of new posts
    new_posts = []

    # Have we run this code before? If not, create an empty list
    if not os.path.isfile("already_done.txt"):
        already_done = []

    # If we have run the code before, load the list of posts we have replied to
    else:
        # Read the file into a list and remove any empty values
        with open("already_done.txt", "r") as f:
            already_done = f.read()
            already_done = already_done.split("\n")
            already_done = list(filter(None, already_done))

    for submission in subreddit.new(limit=10):
        if submission.id not in already_done:
            already_done.append(submission.id)
            title = submission.title
            url = submission.url
            permalink = submission.permalink

            new_posts.append({"title": title,"url": url,"permalink": permalink})

    # Write our updated list back to the file
    with open("already_done.txt", "w") as f:
        for post_id in already_done:
            f.write(post_id + "\n")

    return new_posts

def main():

    service = api_login()

    sender = 'jt58alerts@gmail.com'
    to = 'jt58alerts@gmail.com'

    while True:
        new_posts = reddit_bot()

        for post in new_posts:
            subject = f"[GD] {post['title']}"
            message_text = f"{post['url']}\n\nhttps://www.reddit.com{post['permalink']}"

            print("~"*30 + "\nCreating Email\n" + "~"*30)

            print(subject)

            message = create_message(sender, to, subject, message_text)
            
            print("~"*30 + "\nSending Email")

            send_message(service, 'jt58alerts@gmail.com', message)

            time.sleep(2)

if __name__ == '__main__':
    main()