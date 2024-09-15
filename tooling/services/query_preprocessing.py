import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)

class QueryPreprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess(self, query: str) -> str:
        # Tokenize the query
        tokens = word_tokenize(query.lower())

        # Remove stop words and lemmatize
        processed_tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]

        return ' '.join(processed_tokens)

