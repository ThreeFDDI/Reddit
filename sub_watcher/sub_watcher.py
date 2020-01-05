#!/usr/local/bin/python3

import praw, time, os

# Reddit bot
def reddit_bot():
    reddit = praw.Reddit('bot1')
    subreddit = reddit.subreddit("funny")

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

            print("Title: {}".format(submission.title))
            print("Link: {}".format(submission.url))
            print("Permalink: https://www.reddit.com{}".format(submission.permalink))
            print("-"*80+"\n")

    # Write our updated list back to the file
    with open("already_done.txt", "w") as f:
        for post_id in already_done:
            f.write(post_id + "\n")

while True:
    reddit_bot()