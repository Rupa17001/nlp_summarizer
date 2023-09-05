import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def Query_Filter(user_input):
    wordnet = WordNetLemmatizer()
    corpus =[] 
    sentences = nltk.sent_tokenize(user_input)
    for i in range (len(sentences)):
         review = re.sub('[^a-zA-Z,]'," ",sentences[i])
         review = review.lower()
         review = review.split()
         review = [wordnet.lemmatize(word) for word in review if not word in set(stopwords.words("english"))]
         review = ' '.join(review)
         corpus.append(review)
    return corpus[0]