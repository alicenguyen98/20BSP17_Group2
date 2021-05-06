from wordcloud import  WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd

db = sqlite3.connect('./db/database.db')
df = pd.read_sql_query("SELECT * FROM tweets",db)

# Get stopwords from wordcloud library
stopwords = set(STOPWORDS) 
 
# Add words to stopwords
app_words = ['https']
stopwords.update(app_words)
 
# Get words from Tweets
text = " ".join(review for review in df.text.astype(str))

# Generate wordcloud
Wordcloud = WordCloud(stopwords=stopwords,background_color="white", margin=4, max_words=100, min_word_length=5).generate(text)

# Layout
plt.figure(figsize=(7,4))
plt.imshow(Wordcloud, interpolation='bilinear')
plt.axis("off")
plt.tight_layout(pad=6)

font = {'family':'serif',
        'color':'darkslategrey',
        'weight':'normal',
        'size': 20,
        }

plt.title('Wordcloud from Tweets',fontdict=font,pad=25)
plt.show()