import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
STOPWORDS = stopwords.words("english")


def preprocess(text):
    """Normalise & clean search term"""
    if isinstance(text, str):
        # Remove punctuation
        text = re.sub(r'[^\w\s,->]', '', text)                                          
        # Remove numbers and alphanumeric characters
        text = re.sub(r'\w*\d\w*', '', text)                                             
        # Replace "nan" with a space
        text = re.sub(r'\bnan\b', ' ', text)                                             
        text = re.sub(r'[>,:]', ' ', text)                                               
        # Convert to lowercase
        text = text.lower()
        # Remove stopwords
        text = " ".join([word for word in text.split() if word not in STOPWORDS])
        # Replace " - " with " " to handle hyphenated words
        text = re.sub(r'\s-\s|-\s|\s-', ' ', text)
        return text
    return ""


def non_alpha_1_word(row):
    # Remove unwanted words
    lower_keyword = row["lower_keyword"]
    if isinstance(lower_keyword, float):
        return 0
    lower_keyword = str(lower_keyword)
    if len(lower_keyword) < 3:
        return 0
    first_char = lower_keyword[0]
    if re.match(r"^[^\w\d]|^\d", first_char, flags=re.UNICODE) or re.search(
        r"[₀-₉⁰-⁹ₐ-ₔₕ-ₙₚ-ₛₜ₊₌₍₎]", first_char, flags=re.UNICODE
    ):
        return 0
    if re.match(r"^[a-zA-Z]", first_char):
        return 1
    return 0
