#!/usr/local/bin/python3

import os.path, base64, pickle, praw, time, os
from prawcore import ResponseException, RequestException
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import datetime

# function for Gmail API login
def api_login():
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/gmail.compose']
    creds = None
    
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

# function to create email message
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

# function to send email message
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
        return message

    except HttpError as error:
        print(f"An error occurred with the Gmail API: {error}")

# function for Reddit bot
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

    # parse new submissions
    for submission in subreddit.new(limit=10):
        # check already done posts 
        if submission.id not in already_done:
            # add post to already done
            already_done.append(submission.id)
            # pull values from dict
            title = submission.title
            url = submission.url
            permalink = submission.permalink
            # add new post to list of new posts
            new_posts.append({"title": title,"url": url,"permalink": permalink})

    # Write our updated list back to the file
    with open("already_done.txt", "w") as f:
        for post_id in already_done:
            f.write(post_id + "\n")

    return new_posts

# main function
def main():
    # login to gmail API
    service = api_login()
    # set sender and recepient
    sender = 'jt58alerts@gmail.com'
    to = 'jt58alerts@gmail.com'
    starttime = datetime.datetime.now()
    starttime = starttime.split(".")[0]
    print(f"\nStarting sub_watcher...\n{starttime}\n" + "~"*50)
    
    try:
        while True:
            # attempt to make Reddit connection
            try:
                new_posts = reddit_bot()
            # deal with HTTP error exceptions
            except (
                praw.exceptions.APIException,
                praw.exceptions.ClientException,
                ResponseException,
                RequestException
                ) as error:
                    new_posts = []
                    print(f"\n**** {error} ****\n\n" + "~"*50)
            # iterate over new posts
            for post in new_posts:
                # format subject and message text
                subject = f"[GD] {post['title']}"
                message_text = f"{post['url']}\n\nhttps://www.reddit.com{post['permalink']}\n"
                # print subject
                print(f"\n{subject}\n\n" + "~"*50)
                # create message from subject and message text
                message = create_message(sender, to, subject, message_text)
                # send email message
                try:
                  send_message(service, sender, message)
                except BrokenPipeError as error:
                  print(f"\n**** PRAW error: {error} ****\n\n" + "~"*50)
                # pause
                time.sleep(3)
    except KeyboardInterrupt:
        quittime = datetime.datetime.now()
        quittime = quittime.split(".")[0]
        timerunning = quittime - starttime
        print(f"\nQuitting sub_watcher...\nRunning time = {timerunning}\n" + "~"*50)
        

if __name__ == '__main__':
    main()

'''
Traceback (most recent call last):
  File "sub_watcher.py", line 164, in <module>
    main()
  File "sub_watcher.py", line 143, in main
    prawcore.exceptions.ResponseException
NameError: name 'prawcore' is not defined
'''

'''
Traceback (most recent call last):
  File "sub_watcher.py", line 165, in <module>
    main()
  File "sub_watcher.py", line 158, in main
    send_message(service, sender, message)
  File "sub_watcher.py", line 78, in send_message
    message = (service.users().messages().send(userId=user_id, body=message)
  File "/home/jt/.local/lib/python3.6/site-packages/googleapiclient/_helpers.py", line 130, in positional_wrapper
    return wrapped(*args, **kwargs)
  File "/home/jt/.local/lib/python3.6/site-packages/googleapiclient/http.py", line 851, in execute
    method=str(self.method), body=self.body, headers=self.headers)
  File "/home/jt/.local/lib/python3.6/site-packages/googleapiclient/http.py", line 184, in _retry_request
    raise exception
  File "/home/jt/.local/lib/python3.6/site-packages/googleapiclient/http.py", line 165, in _retry_request
    resp, content = http.request(uri, method, *args, **kwargs)
  File "/home/jt/.local/lib/python3.6/site-packages/google_auth_httplib2.py", line 187, in request
    self._request, method, uri, request_headers)
  File "/home/jt/.local/lib/python3.6/site-packages/google/auth/credentials.py", line 124, in before_request
    self.refresh(request)
  File "/home/jt/.local/lib/python3.6/site-packages/google/oauth2/credentials.py", line 182, in refresh
    self._scopes,
  File "/home/jt/.local/lib/python3.6/site-packages/google/oauth2/_client.py", line 248, in refresh_grant
    response_data = _token_endpoint_request(request, token_uri, body)
  File "/home/jt/.local/lib/python3.6/site-packages/google/oauth2/_client.py", line 105, in _token_endpoint_request
    response = request(method="POST", url=token_uri, headers=headers, body=body)
  File "/home/jt/.local/lib/python3.6/site-packages/google_auth_httplib2.py", line 116, in __call__
    url, method=method, body=body, headers=headers, **kwargs)
  File "/home/jt/.local/lib/python3.6/site-packages/httplib2/__init__.py", line 1976, in request
    cachekey,
  File "/home/jt/.local/lib/python3.6/site-packages/httplib2/__init__.py", line 1640, in _request
    conn, request_uri, method, body, headers
  File "/home/jt/.local/lib/python3.6/site-packages/httplib2/__init__.py", line 1547, in _conn_request
    conn.request(method, request_uri, body, headers)
  File "/usr/lib/python3.6/http/client.py", line 1254, in request
    self._send_request(method, url, body, headers, encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1300, in _send_request
    self.endheaders(body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1249, in endheaders
    self._send_output(message_body, encode_chunked=encode_chunked)
  File "/usr/lib/python3.6/http/client.py", line 1036, in _send_output
    self.send(msg)
  File "/usr/lib/python3.6/http/client.py", line 996, in send
    self.sock.sendall(data)
  File "/usr/lib/python3.6/ssl.py", line 975, in sendall
    v = self.send(byte_view[count:])
  File "/usr/lib/python3.6/ssl.py", line 944, in send
    return self._sslobj.write(data)
  File "/usr/lib/python3.6/ssl.py", line 642, in write
    return self._sslobj.write(data)
BrokenPipeError: [Errno 32] Broken pipe

'''
