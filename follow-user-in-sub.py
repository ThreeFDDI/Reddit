#!/usr/local/bin/python3

# Bot to find posts by user in a subreddit

import praw

# set bot from praw.ini
reddit = praw.Reddit('bot1')

# set user to seach for
that_guy = "user"

# set subreddit to search
subreddit = reddit.subreddit("all")

# do your thing!
for submission in subreddit.new(limit=1000):
    for comment in submission.comments:
        if comment.author == that_guy:
            print(f"-"*80)
            print(comment.body)
            print(comment.author)
            if len(comment.replies) > 0:
                for reply in comment.replies:
                    if reply.author == that_guy:
                        print(f"-"*80)
                        print(comment.body)
                        print(comment.author)
