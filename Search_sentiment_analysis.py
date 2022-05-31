import tweepy
from textblob import TextBlob
import config_keys
import re
import hand_over_results
import psycopg2
from database_connection_config import config


# import of database config-file to run the database
try:
    params_ = config()
    conn = psycopg2.connect(**params_)
    cur = conn.cursor()
    conn.autocommit = True
except:
    pass


# function to get the query and the quntity of tweets wich will be given to the Gui
def searchTweets(query, get_quantity):
    client = tweepy.Client(bearer_token=config_keys.BEARER_TOKEN)

    tweets_pack = client.search_recent_tweets(query=query, max_results=get_quantity)# search_recent_tweets is the function to call to get data from Twitter Api

    tweet_data = tweets_pack.data
    results = []

    for tweet in tweet_data:
        if not tweet_data is None and len(tweet_data) > 0:
            results.append(tweet.text)
        else:
            return []
    return results

# emoji pattern to retrieve all the emojis from the given tweets
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002500-\U00002BEF"  # chinese char
                           u"\U00002702-\U000027B0"
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           u"\U0001f926-\U0001f937"
                           u"\U00010000-\U0010ffff"
                           u"\u2640-\u2642"
                           u"\u2600-\u2B55"
                           u"\u200d"
                           u"\u23cf"
                           u"\u23e9"
                           u"\u231a"
                           u"\ufe0f"  # dingbats
                           u"\u3030"
                           "]+", flags=re.UNICODE)


# function cleans the tweets to get only the text wich will be uploaded to the database
def cleanText(text):
    text = re.sub(r'@[A-Za-z0-9]+', '', text)  # remove.substring mentions
    text = re.sub(r'#', '', text)  # removing the # symbol
    text = re.sub(r'RT[\s]+', '', text)  # remove RT
    text = re.sub(r'http\S+', '', text)  # remove hyper link'
    text = emoji_pattern.sub(r'', text)
    return text


# function wich implements the textblob library which analysis the given text
def get_polarity(text):
    polarity = TextBlob(text).sentiment.polarity
    return polarity



# function wich gets the keyword and the quantity of tweets wich will given to the gui
def printTweets(get_keyword, get_quantity, run):
    if run:

        tweets = searchTweets(get_keyword, get_quantity)

        String_text = '##ll=='.join(tweets)
        String_text_1 = String_text.split('##ll==')

        try:
            cur.execute("Delete from sentimentresults")

        except psycopg2.ProgrammingError:
            hand_over_results.create_table()
            cur.execute("Delete from sentimentresults") # cursor uploads the fetched tweets into the database

        for element in String_text_1: # loop through the joined String and call the clean and polarity function

            cleaning_tweet = cleanText(element)
            score_polarity = get_polarity(cleaning_tweet)
            cur.execute("INSERT INTO sentimentresults (orginaltweet,sentiment)"
                        "VALUES(%s, %s)", (cleaning_tweet, score_polarity,))

        cur.close() # cursor for the database must be closed
        conn.close()
