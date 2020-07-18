auth = tweepy.OAuthHandler(credentials.API_KEY, credentials.API_SECRET_KEY)
# auth.set_access_token(credentials.ACCESS_TOEKN,
#                       credentials.ACCESS_TOKEN_SECRET)
# api = tweepy.API(auth)

# myStreamListener = MyStreamListener()
# myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
# myStream.filter(languages=["en"], track=settings.TRACK_WORDS)
# # Close the MySQL connection as it finished
# # However, this won't be reached as the stream listener won't stop automatically
# # Press STOP button to finish the process.
# conn.close()