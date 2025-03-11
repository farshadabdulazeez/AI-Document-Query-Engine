import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter


def generate_wordcloud(text):
    """
    Generate a word cloud visualization from the given text.
    :param text: Text to visualize.
    """
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.savefig("wordcloud.png")


def generate_insights(text):
    """
    Generate insights from the given text.
    :param text: Text to analyze.
    """
    words = text.split()
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(10)

    # Bar chart of most common words
    plt.figure(figsize=(10, 5))
    plt.bar(*zip(*most_common_words), color='skyblue')
    plt.title("Top 10 Most Common Words")
    plt.xlabel("Words")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("insights.png")