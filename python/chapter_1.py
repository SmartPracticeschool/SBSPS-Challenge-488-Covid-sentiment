import cred
import settings
import re
import tweepy
import mysql.connector
import pandas as pd
from textblob import TextBlob
from datetime import datetime

now = datetime.now()


class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.retweeted:
            # Avoid retweeted info, and only original tweets will be received
            return True
        # Extract attributes from each tweet
        id_str = status.id_str
        created_at = status.created_at
        created_at = now
        text = deEmojify(status.text)    # Pre-processing the text
        sentiment = TextBlob(text).sentiment
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity

        user_created_at = status.user.created_at
        user_location = deEmojify(status.user.location)
        user_description = deEmojify(status.user.description)
        user_followers_count = status.user.followers_count
        longitude = None
        latitude = None
        if status.coordinates:
            longitude = status.coordinates['coordinates'][0]
            latitude = status.coordinates['coordinates'][1]

        retweet_count = status.retweet_count
        favorite_count = status.favorite_count

        print(status.text)
        print("Long: {}, Lati: {}".format(longitude, latitude))

        # Store all data in MySQL
        if mydb.is_connected():
            mycursor = mydb.cursor()
            sql = "INSERT INTO {} (id_str, created_at, text, polarity, subjectivity, user_created_at, user_location, user_description, user_followers_count, longitude, latitude, retweet_count, favorite_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)".format(settings.TABLE_NAME)
            val = (id_str, created_at, text, polarity, subjectivity, user_created_at, user_location,
                   user_description, user_followers_count, longitude, latitude, retweet_count, favorite_count)
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()

    def on_error(self, status_code):
        '''
        Since Twitter API has rate limits, stop srcraping data as it exceed to the thresold.
        '''
        if status_code == 420:
            # return False to disconnect the stream
            return False

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) \
                                    |(\w+:\/\/\S+)", " ", tweet).split())


def deEmojify(text):
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return None


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="TwitterDB",
    charset='utf8'
)
if mydb.is_connected():
    '''
    Check if this table exits. If not, then create a new one.
    '''
    mycursor = mydb.cursor()
    mycursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(settings.TABLE_NAME))
    if mycursor.fetchone()[0] != 1:
        mycursor.execute("CREATE TABLE {} ({})".format(
            settings.TABLE_NAME, settings.TABLE_ATTRIBUTES))
        mydb.commit()
    mycursor.close()

auth = tweepy.OAuthHandler(cred.API_KEY, cred.API_SECRET_KEY)
auth.set_access_token(cred.ACCESS_TOEKN,
                      cred.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(languages=["en"], track=settings.TRACK_WORDS)
# Close the MySQL connection as it finished
# However, this won't be reached as the stream listener won't stop automatically
# Press STOP button to finish the process.
mydb.close()
