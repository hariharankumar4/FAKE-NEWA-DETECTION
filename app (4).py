import streamlit as st
import requests
import nltk
nltk.download('stopwords')
import r

nltk.download('stopwords', quiet=True)

# --- Re-define all necessary variables and functions for the Streamlit app ---

API_KEY = "05cea2c97b219c9a9966a2a2a456f70a" # Use your actual API key here

trusted_sources = [
    'bbc',
    'cnn',
    'reuters',
    'ndtv',
    'times of india',
    'hindustan times',
    'the hindu',
    'india today',
    'al jazeera',
    'guardian',
    'cnbc',
    'economic times',
    'zee news',
    'livemint',
    'firstpost'
]

stop_words = set(stopwords.words('english'))

def extract_keywords(text):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    keywords = [
        w for w in words
        if w not in stop_words and len(w) > 3
    ]
    return keywords[:10]

def fetch_news(user_text):
    keywords = extract_keywords(user_text)
    queries = [
        ' '.join(keywords[:3]),
        ' '.join(keywords[:2]),
        keywords[0] if len(keywords) > 0 else user_text
    ]
    all_articles = []
    for q in queries:
        if not q.strip(): # Skip empty queries
            continue
        url = f"https://gnews.io/api/v4/search?q={q}&lang=en&max=10&token={API_KEY}"
        try:
            response = requests.get(url)
            response.raise_for_status() # Raise an exception for HTTP errors
            data = response.json()
            if 'articles' in data:
                for article in data['articles']:
                    title = article.get('title', '')
                    description = str(article.get('description', ''))
                    source = article.get('source', {}).get('name', 'Unknown')
                    text = title + ' ' + description
                    all_articles.append((text, source))
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching news for query '{q}': {e}")
            continue
    return list(set(all_articles))

def check_source_trust(source):
    source_lower = source.lower()
    for trusted in trusted_sources:
        if trusted in source_lower:
            return True
    return False

def detect_news(user_text):
    articles = fetch_news(user_text)

    keyword_hits = 0
    trusted_hits = 0

    if not articles:
        return 'Cannot determine: No articles found.' # Handle cases where no articles are fetched

    keywords = extract_keywords(user_text)

    for article_text, source in articles:
        text_lower = article_text.lower()
        matches = sum(
            1 for word in keywords
            if word in text_lower
        )
        if matches >= 2:
            keyword_hits += 1
            if check_source_trust(source):
                trusted_hits += 1

    if trusted_hits >= 1:
        return 'REAL NEWS'
    elif keyword_hits >= 3:
        return 'REAL NEWS'
    else:
        return 'FAKE NEWS'

# --- Streamlit UI ---
st.title('Real vs Fake News Detection')

user_news = st.text_input('Enter News Headline:')

if st.button('Detect News'):
    if user_news:
        with st.spinner('Analyzing news...'):
            result = detect_news(user_news)
            st.success('Analysis Complete!')
            st.write('### Final Result:')
            if result == 'REAL NEWS':
                st.markdown(f"<h1 style='color: green;'>{result}</h1>", unsafe_allow_html=True)
            elif result == 'FAKE NEWS':
                st.markdown(f"<h1 style='color: red;'>{result}</h1>", unsafe_allow_html=True)
            else:
                st.info(result) # For 'Cannot determine' cases
    else:
        st.warning('Please enter a news headline to analyze.')
