import tweepy
import logging
import time
from config import create_api, download_media
import os
import glob

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    # fetch items (tweets) from mentions. Use cursor for pagination (aka can do more than request 1 page)
    for tweet in tweepy.Cursor(api.mentions_timeline, since_id=since_id, tweet_mode="extended").items():
        # set new since_id to the highest tweet id (most recent).
        new_since_id = max(tweet.id, new_since_id)

        '''
        Im still trying to figure out what the below code does exactly...
        
        if tweet.in_reply_to_status_id is not None:
            logger.info("in_reply_to_status_id is not none... restart loop")
            logger.info(tweet.in_reply_to_status_id)
            continue
        logger.info("Detected mention...")
        '''

        # if not following the person who mentioned you, follow them
        if not tweet.user.following:
            tweet.user.follow()

        # download media
        if 'media' in api.get_status(tweet.in_reply_to_status_id).entities:
            logger.info("I found media!")
            media_ids = download_media(api, api.get_status(tweet.in_reply_to_status_id))

            # tweets the status argument as a reply, to the specified tweet id
            logger.info(f"Answering to {tweet.user.name} and posting pic...")
            api.update_status(status=f"Hey {tweet.user.name}. "
                                     f"I tried to find some faces in the tweet you showed me.",
                              in_reply_to_status_id=tweet.id,
                              auto_populate_reply_metadata=True,
                              media_ids=media_ids
                              )

            # delete downloaded media
            if os.path.exists('C:\\PythonLearning\\TwitterBot\\media'):
                files = glob.glob('.\\media\\*.jpg')
                for f in files:
                    os.remove(f)
                logger.info("Deleted downloaded photos...")
            else:
                logger.info("Could not delete downloaded photo...")
        else:
            logger.info("Sorry could not find media..")
            api.update_status(status=f"Hey {tweet.user.name}, sorry I could not find a photo in the tweet you tagged"
                                     f" me in...",
                              in_reply_to_status_id=tweet.id,
                              auto_populate_reply_metadata=True)
    return new_since_id


def main():
    # Creates Tweepy API object
    api = create_api()
    # since_id is used return only statuses with an ID greater than (more recent than) the specified ID.
    since_id = 1
    while True:
        since_id = check_mentions(api, since_id)
        logger.info("Waiting...")
        time.sleep(60)


if __name__ == "__main__":
    main()
