import logging
import pandas as pd
import numpy as np
from alive_progress import alive_bar
import seaborn as sns
import matplotlib.pyplot as plt


from wordcloud import WordCloud, STOPWORDS
from scipy import stats
import re
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from bs4 import BeautifulSoup

# Config
saveDatasetName = '4_questions'
cleanedDatasetName = '4_questions_cleaned'

stopwordlist = set(stopwords.words("english"))
wordnet_lemmatizer = WordNetLemmatizer()
ps = PorterStemmer()
# pd.set_option('display.max_columns', None)


#TODO: add different clean methods

# remove html tag
def remove_htmltag(body):
    soup = BeautifulSoup(body, 'html.parser')
    new_body = soup.get_text()
    return new_body


# remove stopwords
def remove_stopwords(body):
    body = [w for w in body.split() if not w in stopwordlist]
    return (" ").join(body)


# stemmer and lemmatizer
def stemmer_lemmatizer(body):
    word_list = []
    for word in body.split():
        word = ps.stem(word)
        word = wordnet_lemmatizer.lemmatize(word)
        word_list.append(word)
    return (" ".join(word_list))


# clean pipeline
def stack_clean(stacks, flag):
    new_stacks = [None]*len(stacks)
    with alive_bar(len(stacks)) as bar:
        for i in range(len(stacks)):
            # print(type(stacks[i]))
            # print(stacks[i])
            if flag == 'html_tag':
                new_stacks[i] = remove_htmltag(stacks[i])
            elif flag == 'stop_words':
                new_stacks[i] = remove_stopwords(stacks[i])
            elif flag == 'stemmer_lemmatizer':
                new_stacks[i] = stemmer_lemmatizer(stacks[i])
            elif flag == 'all':
                new_stacks[i] = remove_htmltag(stacks[i])
                new_stacks[i] = remove_stopwords(new_stacks[i])
                new_stacks[i] = stemmer_lemmatizer(new_stacks[i])
            bar()

    return new_stacks


# save dataset
def save_dataset(df, df_name):
    logging.info('Saving dataset...')
    # Create Saving Files
    # if not os.path.exists('/datasets'):
    #     os.makedirs('/datasets')
    df.to_csv(r'./datasets/' + df_name + '.csv', index=False, header=True)
    logging.info('Saved parsed dataset')


# generate word cloud
# def wordcloud(data,backgroundcolor = 'white', width = 400, height = 150):
#     wordcloud = WordCloud(stopwords = STOPWORDS, background_color = backgroundcolor,
#                          width = width, height = height).generate(data)
#     plt.figure(figsize = (15, 10))
#     plt.imshow(wordcloud)
#     plt.axis("off")
#     plt.show()

# read csv file as dataframe
df_clean = pd.read_csv('./datasets/'+saveDatasetName+'.csv')
# clean data
df_clean['body'] = stack_clean(df_clean['body'], 'html_tag')
save_dataset(df_clean, cleanedDatasetName)

df_clean['is_closed'] = df_clean['closed_date'].apply(np.isfinite)
wordcloud(df_clean['title'].to_string())
wordcloud(df_clean['body'].to_string())

print(df_clean.groupby('is_closed').count())
sns.countplot(df_clean['is_closed'])
plt.show()
print(df_clean.groupby('closed_reason').count())
sns.countplot(df_clean['closed_reason'])
plt.show()

print(df_clean.count)
