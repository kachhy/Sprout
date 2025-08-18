import nltk
nltk.download('words')
from nltk.corpus import words
english_words = set(words.words())
print(f"Number of words in NLTK corpus: {len(english_words)}")