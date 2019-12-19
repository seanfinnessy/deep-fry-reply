import tweepy
import logging
import os
import wget
from PIL import Image, ImageOps, ImageEnhance

logger = logging.getLogger()


def create_api():
    # Get environment variable
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    # Create tweepy auth object, then create API object if credentials are valid
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api


def download_media(api, tweet):
    media_files = set()
    if 'media' in tweet.entities:
        for media in tweet.extended_entities['media']:
            print(media['media_url'])
            media_files.add(media['media_url'])

        logger.info("Beginning file download..")
        media_ids = []
        i = 0
        for media_url in media_files:
            wget.download(media_url, f'.\\media\\picture{i}.jpg')
            image_manip(f'.\\media\\picture{i}.jpg')
            res = api.media_upload(f'.\\media\\picture{i}.jpg')
            media_ids.append(res.media_id)
            i += 1

        return media_ids
            
    else:
        print("Sorry, I could not find any attached media! Please DM me if I am wrong. Thanks!")


def image_manip(image):
    img = Image.open(image)

    # crush image
    img = img.convert('RGB')
    width, height = img.width, img.height
    img = img.resize((int(width ** .75), int(height ** .75)), resample=Image.LANCZOS)
    img = img.resize((int(width ** .88), int(height ** .88)), resample=Image.BILINEAR)
    img = img.resize((int(width ** .9), int(height ** .9)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, 4)

    # color overlay
    r = img.split()[0]
    logger.info(img.split()[0])
    r = ImageEnhance.Contrast(r).enhance(2.0)
    r = ImageEnhance.Brightness(r).enhance(1.5)
    r = ImageOps.colorize(r, [194, 0, 0], [194, 0, 221])

    # overlay red and yellow onto main image and sharpen
    img = Image.blend(img, r, 0.75)
    img = ImageEnhance.Sharpness(img).enhance(100.0)

    img.save(image, 'JPEG')

