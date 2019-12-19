import tweepy
import logging
import os
import wget
from PIL import Image, ImageOps, ImageEnhance
import cv2

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


def image_manip(image):
    face_detection(image)
    '''
    
    Turned off while I test face detection
    
    img = Image.open(image)

    # crush image
    img = img.convert('RGB')
    width, height = img.width, img.height
    img = img.resize((int(width ** .93), int(height ** .93)), resample=Image.LANCZOS)
    img = img.resize((int(width ** .95), int(height ** .95)), resample=Image.BILINEAR)
    img = img.resize((int(width ** .97), int(height ** .97)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, 4)

    # color overlay
    r = img.split()[0]
    logger.info(img.split()[0])
    r = ImageEnhance.Contrast(r).enhance(2.0)
    r = ImageEnhance.Brightness(r).enhance(1.5)
    r = ImageOps.colorize(r, [254, 0, 2], [255, 255, 15])

    # overlay red and yellow onto main image and sharpen
    # img = Image.blend(img, r, 0.75)

    img = ImageEnhance.Sharpness(img).enhance(200.0)
    img = ImageEnhance.Contrast(img).enhance(100.0)
    img = ImageEnhance.Brightness(img).enhance(50.0)
    img = ImageEnhance.Color(img).enhance(50.0)
    img.save(image, 'JPEG')
    '''


def face_detection(image):
    original_image = cv2.imread(image)
    grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier('C:\\PythonLearning\\TwitterBot\\bots\\haarcascade_frontalface_alt.xml')
    detected_faces = face_cascade.detectMultiScale(grayscale_image)

    for (column, row, width, height) in detected_faces:
        cv2.rectangle(
            original_image,
            (column, row),
            (column + width, row + height),
            (0, 255, 0),
            2
        )
    cv2.imwrite(image, original_image)

