# cyberpunk_me by Jake Funke
# Overlays cyberpunk visuals over user avatars
# Responds to users that tweet "@Cyberpunk_Me " with phrase containing "cyberpunk me"
#
# COMPLETE - Check mentions for string "cyberpunk me"
# COMPLETE - Get that user's profile name
# COMPLETE - GET IMAGE
# COMPLETE - overlay the image with a filter
# COMPLETE - post it back to twitter
# TODO - hacker text instead of "you're cyberpunk now" (i.e. 'mess with the best, die like the rest!')

import tweepy
from PIL import Image, ImageFilter
from random import randint
import json
import urllib


class TwitterAPI:
    def __init__(self):
        consumer_key = '<your_consumer_key>'
        consumer_secret = '<your_consumer_secret>'
        access_token = '<your_access_token>'
        access_token_secret = '<your_access_token_secret>'
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    # Post a tweet
    def tweet(self, message):
        self.api.update_status(status=message)

    # Post an image with a message
    def tweet_image(self, filename, message):
        self.api.update_with_media(filename, status=message)

    # Retrieve a user's profile picture
    def get_profpic(self, username):
        json_data = self.api.get_user(username)._json  # loaded as a python dict
        json_decoded = json.dumps(json_data)
        json_encoded = json.loads(json_decoded)
        profile_url = str(json_encoded['profile_image_url']).replace('_normal',
                                                                     '')  # str value, need to make original size
        urllib.urlretrieve(profile_url, 'profpic.jpg')

    # Retrieve username from most recent mention (need to incorporate streaming)
    def get_mentions(self):
        mentions = self.api.mentions_timeline(count=1)
        for mention in mentions:
            return mention.user.screen_name


# Overlay an image from local library onto user's profile image
def overlay_image(image1, image2):
    background = Image.open(image1)
    background = background.convert('RGBA')
    background = background.resize((600, 600), Image.ANTIALIAS)  # resize to 600x600 for source images to match

    overlay = Image.open(image2)
    overlay = overlay.convert('RGBA')

    new_img = Image.blend(background, overlay, 0.33)  # blend two images together
    new_img = new_img.filter(ImageFilter.EDGE_ENHANCE_MORE)  # apply filter
    new_img.save('new.png', 'PNG')


# Get image from user, create new image, and post it
def create_and_post(username):
    twitter.get_profpic(username)
    overlay_image('profpic.jpg', ('images/%02d.jpg' % randint(1, 40)));
    twitter.tweet_image('new.png', '.@%s you\'re cyberpunk now' % username)


# Override tweepy.StreamListener to add logic to on_status
class mentionListener(tweepy.StreamListener):
    # Print & create image when seeing a tweet with the status specified
    def on_status(self, status):
        global lastuser
        ascii_usernm = status.user.screen_name.encode('ascii', 'replace')
        ascii_tweet = status.text.encode('ascii', errors='replace')
        if (('@cyberpunk_me' in ascii_tweet.lower()) and ('cyberpunk me' in ascii_tweet.lower()) and (
                    ascii_usernm != lastuser)):
            print ascii_usernm
            print ascii_tweet
            create_and_post(ascii_usernm)
            lastuser = ascii_usernm

    def on_error(self, status_code):
        if status_code == 420:
            # returning False in on_data disconnects the stream
            return False


if __name__ == '__main__':
    global lastuser
    lastuser = ' '
    twitter = TwitterAPI()
    print '///// Cyberpunk_Me is now active /////\nUsers may tweet "@Cyberpunk_Me cyberpunk me" to get avatar'
    mentionListener = mentionListener()
    mentionStream = tweepy.Stream(auth=twitter.api.auth, listener=mentionListener)
    mentionStream.filter(track=['cyberpunk', '#cyberpunk'])
