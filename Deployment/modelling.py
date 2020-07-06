import joblib
from nltk.corpus import stopwords
from automation_access import obtener_tweets
#import libraries
import pandas as pd
import nltk
import spacy
import re
import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
sn = SnowballStemmer(language='spanish')
ps = PorterStemmer()
nlp = spacy.load("es_core_news_sm")
# nltk.download('stopwords')
clf = joblib.load('classifier')
vectorizer = joblib.load('vectorizer')


def prediction(words, items):
    palabra = words
    cantidad = items
    data = obtener_tweets(palabra, cantidad)
    data = pd.DataFrame(data)
    # data.columns = [['Id', 'Nombre', 'Usuario', 'Texto', 'Fecha', 'Lugar']]
    cuerpo = []
    for i in range(0, len(data)):
        pat = r'[^a-zA-zÑñxáéíóú]'
        review = re.sub(pat, ' ', data[3][i])
        review = review.split()
        review = ' '.join(review)
        doc = nlp(review)
        review = []
        for token in doc:
            words_tokenize = token.lemma_
            words_tokenize = words_tokenize.lower()
            words_tokenize = ps.stem(words_tokenize)
            words_tokenize = sn.stem(words_tokenize)
            review.append(words_tokenize)
        review = [ps.stem(word) for word in review if not word in set(
            stopwords.words('spanish'))]
        review = ' '.join(review)
        new = []
        new.append(review)
        cuerpo.append(new)

    cuerpo = [item for val in cuerpo for item in val]
    cuerpo = pd.DataFrame(cuerpo)
    X = cuerpo.iloc[:, 0].values
    proof = vectorizer.transform(X).toarray()
    pred = clf.predict(proof)
    # comentarios_negativos = data.join(pred)
    # comentarios_negativos = pd.DataFrame(comentarios_negativos)
    # comentarios_negativos.columns = [
    #     ['Id', 'Nombre', 'Usuario', 'Texto', 'Fecha', 'Lugar', 'Sentimiento']]

    return pred
