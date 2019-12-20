import tweepy
import logging
import os
import wget
from PIL import Image, ImageOps, ImageEnhance
import cv2
from collections import namedtuple

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
    # Record media urls found in tweet
    media_files = set()
    for media in tweet.extended_entities['media']:
        print(media['media_url'])
        media_files.add(media['media_url'])

    # Download media
    logger.info("Beginning file download..")
    media_ids = []
    i = 0
    for media_url in media_files:
        wget.download(media_url, f'.\\media\\picture{i}.jpg')
        # Manipulate the image(s)
        image_manip(f'.\\media\\picture{i}.jpg')
        res = api.media_upload(f'.\\media\\picture{i}.jpg')
        media_ids.append(res.media_id)
        i += 1
    return media_ids


def image_manip(image):
    # Find faces in image
    flare_positions = face_detection(image)
    print(type(flare_positions))
    # Open flare as PIL object
    flare_img = Image.open('C:\\PythonLearning\\TwitterBot\\bots\\flare.png')

    img = Image.open(image)
    img = img.convert('RGB')
    '''# crush image
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
    img = ImageEnhance.Color(img).enhance(50.0)'''

    # Apply flares
    for flare in flare_positions:
        flare_transformed = flare_img.copy().resize((flare.size,) * 2, resample=Image.BILINEAR)
        '''  original_image_arr = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
        original_image = Image.fromarray(original_image_arr)
        face_roi_color = cv2.cvtColor(face_roi_color, cv2.COLOR_BGR2RGB)
        face_roi_color = Image.fromarray(face_roi_color)
        print(type(face_roi_color))'''
        img.paste(flare_transformed, (flare.x, flare.y), flare_transformed)
        print("flared")

    img.save(image, 'JPEG')


def face_detection(image):
    # Read in the original image
    original_image = cv2.imread(image)
    # Convert image to grayscale (must have)
    grayscale_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    # Load classifier and create a cascade object for face detection
    face_cascade = cv2.CascadeClassifier('C:\\PythonLearning\\TwitterBot\\bots\\haarcascade_frontalface_alt.xml')
    eye_cascade = cv2.CascadeClassifier('C:\\PythonLearning\\TwitterBot\\bots\\haarcascade_eye.xml')
    # detectMultiScale recieves image as an argument and runs the classifier cascade over the image
    # MultiScale means the algo looks at subregions of the image in multiple scales, to detect faces of diff sizes
    # detected_faces now contains all detections for image.
    detected_faces = face_cascade.detectMultiScale(grayscale_image)

    flare_positions = []
    FlarePosition = namedtuple('FlarePosition', ['x', 'y', 'size'])

    # To visualize the detections, you need to iterate over all detections and draw rect around detected faces
    # Luckily, detections are saved as pixel coordinates. Each detection is defined by its top-left
    # corner coordinates and width and height of the rectangle that encompasses the detected face.
    for (x, y, width, height) in detected_faces:
        #  Get break down region of interest to only look at faces.
        face_roi_gray = grayscale_image[y:y+height, x:x+width]
        face_roi_color = original_image[y:y+height, x:x+width]
        detected_eyes = eye_cascade.detectMultiScale(face_roi_gray)
        cv2.rectangle(
            original_image,
            (x, y),  # top left
            (x + width, y + height),  # bottom right
            (0, 255, 0),
            2
        )

        for (eye_x, eye_y, eye_width, eye_height) in detected_eyes:
            eye_corner = (eye_x, eye_y)
            flare_size = eye_height if eye_height > eye_width else eye_width
            flare_size = flare_size * 4
            eye_corner = FlarePosition(*eye_corner, flare_size)
            flare_positions.append(eye_corner)

            cv2.rectangle(
                face_roi_color,
                (eye_x, eye_y),  # top left
                (eye_x + eye_width, eye_y + eye_height),  # bottom right
                (255, 0, 0),
                2
            )

    cv2.imwrite(image, original_image)
    return flare_positions
