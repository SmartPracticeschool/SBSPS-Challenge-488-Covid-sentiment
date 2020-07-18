TRACK_WORDS = ['covid19', 'coronavirus',
               'pandemic', 'lockdown', 'qurantine', 'WHO', 'vaccine', '#InternationalYogaDay', '#ArrestMurdererOfSushant']
TABLE_NAME = "covid"
TABLE_ATTRIBUTES = "id_str VARCHAR(255), created_at DATETIME, text VARCHAR(255), \
            polarity INT, subjectivity INT, user_created_at VARCHAR(255), user_location VARCHAR(255), \
            user_description VARCHAR(255), user_followers_count INT, longitude DOUBLE, latitude DOUBLE, \
            retweet_count INT, favorite_count INT"
