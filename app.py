from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import wordnet
from spellchecker import SpellChecker
from sumy.parsers.plaintext import PlaintextParser
from deep_translator import GoogleTranslator
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from textblob import TextBlob
import textstat
from wordfreq import word_frequency
import nltk
import random
from collections import Counter
nltk.download('vader_lexicon')
nltk.download('punkt')
app = Flask(__name__)
spell = SpellChecker()
translator = Translator()
sia = SentimentIntensityAnalyzer()
def check_spelling(text):
    words = text.split()
    corrected_words = [spell.correction(word) if spell.correction(word) else word for word in words]
    return " ".join(corrected_words)
def auto_capitalize(text):
    sentences = text.split('. ')
    return '. '.join(sentence.capitalize() for sentence in sentences)
def suggest_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms) if synonyms else ["No synonyms found"]
def count_words(text):
    words = text.split()
    return f"Word Count: {len(words)}"
def count_syllables(text):
    return f"Syllable Count: {textstat.syllable_count(text)}"
def analyze_word_complexity(text):
    words = text.split()
    complexity_scores = {word: round(word_frequency(word, 'en', minimum=0.0000001), 8) for word in words}
    if not complexity_scores:
        return "⚠️ No valid words found."
    formatted_output = "<b>Word Complexity Scores:</b><br>"
    for word, score in complexity_scores.items():
        formatted_output += f"{word}: {score}<br>"
    return formatted_output
def summarize_text(text, num_sentences=2):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)
def analyze_sentiment(text):
    sentiment = TextBlob(text).sentiment.polarity
    if sentiment > 0:
        return "😊 Positive"
    elif sentiment < 0:
        return "😡 Negative"
    else:
        return "😐 Neutral"
def analyze_tone(text):
    scores = sia.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.5:
        return "😊 Happy"
    elif 0.2 <= compound < 0.5:
        return "🙂 Content"
    elif -0.2 < compound < 0.2:
        return "😐 Neutral"
    elif -0.5 <= compound <= -0.2:
        return "😞 Sad"
    else:
        return "😡 Angry"
def translate_text(text, target_lang):
    if target_lang.lower() == "zh-cn":
        target_lang = "zh-CN"
    valid_languages = ["en", "es", "fr", "de", "hi", "zh-CN", "ar", "ru"]
    if target_lang not in valid_languages:
        return "⚠️ Translation Error: Invalid destination language."
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        return f"⚠️ Translation Error: {str(e)}"
def generate_title(text):
    blob = TextBlob(text)
    words = blob.noun_phrases
    word_counts = Counter(blob.words)
    main_topic = words[0].capitalize() if words else (blob.words[0].capitalize() if blob.words else "Untitled")
    common_word = word_counts.most_common(1)[0][0] if word_counts else main_topic
    templates = [
        f"The Power of {main_topic}",
        f"How {main_topic} is Changing the World",
        f"Top 5 Secrets About {main_topic}",
        f"The Ultimate Guide to {main_topic}",
        f"Why {common_word} Matters More Than Ever",
        f"10 Things You Didn’t Know About {main_topic}",
        f"The Future of {main_topic}: What You Need to Know",
        f"{main_topic} Explained: A Beginner’s Guide",
        f"How to Master {main_topic} in 30 Days",
        f"Breaking Down {main_topic}: Insights & Trends"
    ]

    return templates
def generate_blog_outline(text):
    blob = TextBlob(text)
    keywords = blob.noun_phrases
    main_topic = keywords[0].capitalize() if keywords else "Your Topic"
    key_points = [
        f"Understanding {main_topic}",
        f"Importance of {main_topic} in Today's World",
        f"Common Challenges in {main_topic}",
        f"Best Practices for {main_topic}",
        f"Latest Innovations in {main_topic}",
        f"How {main_topic} Impacts Society",
        f"Top Myths About {main_topic}",
        f"Case Studies on {main_topic}",
        f"Future Trends of {main_topic}",
        f"How to Get Started with {main_topic}"
    ]
    random.shuffle(key_points)
    selected_points = key_points[:3]
    outline = {
        "Introduction": f"An overview of {main_topic} and why it matters.",
        "Key Points": selected_points,
        "Conclusion": f"Final thoughts on {main_topic} and its future potential."
    }
    return outline
def generate_hashtags(text):
    blob = TextBlob(text)
    keywords = blob.noun_phrases
    hashtags = [f"#{word.replace(' ', '')}" for word in keywords]
    random.shuffle(hashtags)
    return hashtags[:10] if hashtags else ["#NoHashtagsFound"]
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/process', methods=['POST'])
def process():
    text = request.form.get('text', '')
    option = request.form.get('option', '')
    target_lang = request.form.get('target_lang', 'en')
    if not text:
        return jsonify({"result": "⚠️ Please enter some text."})
    if option == 'title_generator':
        result = generate_title(text)
    elif option == 'blog_outline':
        result = generate_blog_outline(text)
    elif option == 'translate_text':
        result = translate_text(text, target_lang)
    elif option == 'tone_analysis':
        result = analyze_tone(text)
    elif option == 'sentiment_analysis':
        result = analyze_sentiment(text)
    elif option == 'spell_checker':
        result = check_spelling(text)
    elif option == 'synonym_suggestion':
        result = {word: suggest_synonyms(word) for word in text.split()}
    elif option == 'auto_capitalize':
        result = auto_capitalize(text)
    elif option == 'word_counter':
        result = count_words(text)
    elif option == 'text_summarization':
        result = summarize_text(text)
    elif option == 'syllable_counter':
        result = count_syllables(text)
    elif option == 'word_complexity':
        result = analyze_word_complexity(text)
    elif option == 'hashtag_generator':
        result = generate_hashtags(text)
    else:
        return jsonify({"result": "⚠️ Invalid option selected."})
    return jsonify({"result": result})


if __name__ == '__main__':
    app.run(debug=True)
