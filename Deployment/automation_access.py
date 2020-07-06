import tweepy
import pandas as pd
import csv


def obtener_tweets(name, tweets):
    consumer_key = "oWU8KiLUwrV3oFOzlFPxIM86a"
    consumer_secret = "EOiShU8htn6Kgarc4Fvc4vAF0Ippe6OAfO7rsq7T6qIeyTgo2l"

    # autentication acces
    auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    corpus = []
    for tweet in tweepy.Cursor(api.search, q=('{0}  -filter:retweets -filter:links'.format(name)), tweet_mode='extended', lang="es", wait_on_rate_limit=True).items(tweets):
        texto = tweet.full_text
        usuario = tweet.user.screen_name
        nombre = tweet.user.name
        id_texto = tweet.id
        tiempo = tweet.created_at
        lugar = tweet.user.location

        info = [str(id_texto),
                nombre,
                usuario,
                texto,
                str(tiempo),
                lugar]
        corpus.append(info)
    info = pd.DataFrame(info)
    info.to_csv("db/{0}.csv".format(name),
                encoding='utf-8', index=False)
    return corpus
