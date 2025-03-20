#!/usr/bin/env python
# coding: utf-8

# Import libraries
import glob
import re, os
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import pickle
from gensim import corpora
import itertools
import pandas as pd
from gensim.models import TfidfModel
from gensim import similarities
import matplotlib.pyplot as plt

# ### Load the contents of each book (stored in books folder):
folder = "books/"
# List text files in a folder: 
files = glob.glob(folder + "*.txt")
files.sort()
files


# Initialize the object that will contain the texts and titles
txts = []
titles = []

for n in files:
    # Open each file
    f = open(n, encoding='utf-8-sig')
    # Remove all non-alpha-numeric characters
    # The square brackets [] denote a character class.
    # \w is a special class called "word characters". It is shorthand for [a-zA-Z0-9_]
    data = re.sub('[\W_]+', ' ', f.read())
    # Store the texts and titles of the books in two separate lists
    txts.append(data)
    titles.append(os.path.basename(n).replace(".txt", ""))

print(len(txts))

# Loop through vlist containing all the titles
for i in range(len(titles)):
    # Store the index of the query book
    if titles[i] == query_book:
        index = i
        print(index)
        

# ### Preprocessing / Tokenize Corpus:
# ie. Transform each text into a list(ordered) of the individual words (called tokens) 

stopwords = set(stopwords.words('english'))
additional_stopwords = {'1', '2', '3','4','5','6','7','8','9','10','a','was','e'}
roman_numerals = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
    "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX"
]
# Update the set with additional stopwords
stopwords.update(additional_stopwords)
stopwords.update(roman_numerals) # Noticed this while saving .txt files

# lower case 
txts_lower_case = [text.lower() for text in txts]

# tokenize
txts_split = [text.split() for text in txts_lower_case ]

# Filter out the stopwords
text_corpus = []

for text in txts_split:
    current_text = [word for word in text if word not in stopwords]
    text_corpus.append(current_text)

# ### Stemming of the tokenized corpus
# ie: Group together the same forms of a word so they can be analysed as a single item (example analyze, analysis, analyzations) instead of dilluting the presence of words across their other forms. 

# Load the Porter stemming function from the nltk package
porter = PorterStemmer()

# # For each token of each text, generate its stem 
texts_stem = [[porter.stem(token) for token in text] for text in text_corpus]

# # Save to pickle file
pickle.dump( texts_stem, open( "books/texts_stem_new_recommendations.p", "wb" ) )

# Note to self: If I reopen this doc, run this code instead of re-stemming above
f = open( "books/texts_stem_new_recommendations.p", "rb" )
texts_stem = pickle.load(f)
# The pickle file has the stemmed (root word) for each word/token, from each txt obj (body/texts of all the books)




# ### Bag of Words Model
# Load the functions used for integer id association dict
dictionary = corpora.Dictionary(texts_stem)

# Create a bag-of-words model for each book using a loop
bows = [dictionary.doc2bow(text) for text in texts_stem]


# ### Find the most common words for the book being queried:

# Convert the BoW model for query book into a DF: 
df_query_book = pd.DataFrame(bows[index])
df_query_book.columns =['id', 'frequency']
print(index)

# Add a column containing the token corresponding to the dictionary index
df_query_book['token'] =  [dictionary[id] for id in df_query_book["id"]]

# Sort the DataFrame by descending number of occurrences and print the first 10 values
df_query_book = df_query_book.sort_values(by=['frequency'])
df_sorted = df_query_book.sort_values(by=['frequency'], ascending=[False])

print('Top words in ',query_book, ' are:')
print(df_sorted.head(10))


# ### Build a tf-idf model
# (term frequency–inverse document frequency model)
# Defines the importance of each word depending on how frequent it is in this text and how infrequent it is in all the other documents. As a result, a high tf-idf score for a word will indicate that this word is specific to this text.

model = TfidfModel(bows)

# ### Display the 10 most specific words for the book being queried:

# Convert book into a data frame a DataFrame:
df_tfidf = pd.DataFrame(model[bows[index]])

# rename columns
df_tfidf.columns =['id', 'score']

# Merge the token (from the integer id dictionary)
df_tfidf['token'] = [ dictionary[i] for i in list(df_tfidf["id"]) ]

# Sort the DataFrame by descending tf-idf score and print the first 10 rows.
df_tfidf.sort_values(by="score", ascending=False).head(10)


# ### Compute Similarites between books
sims = similarities.MatrixSimilarity(model[bows])

# as data frame:
sim_df = pd.DataFrame(list(sims))

# Label df: 
sim_df.columns = titles
sim_df.index = titles

sim_df


# ### The book most similar to book of interest:

# Select the column of the book you wish to query:
v = sim_df[query_book]

# Sort by ascending scores
v_sorted = v.sort_values(ascending=True)

title = "Most similar books to "+ query_book
# Plot this data as a horizontal bar plot
v_sorted.plot.barh(x='lab', y='val', rot=0).plot()

# Modify the axes labels and plot title for better readability
plt.xlabel("Cosine distance")
plt.ylabel("")
plt.title(title)


# ### Print common tokens:  

most_similar_book = v_sorted.index[-2]

for i in range(len(titles)):
    if titles[i] == most_similar_book:
        similar_index = i
        
query_index = index
print(similar_index)

corpus_tfidf = model[bows]

#Apply model on just select books: 
query_tfidf = corpus_tfidf[query_index]
similar_tfidf = corpus_tfidf[similar_index]

# Convert TF-IDF vectors to dict (key is id, val is tf-idf score)
query_dict = dict(query_tfidf)
rec_dict = dict(similar_tfidf)

# Get the top N terms for each document
N = 200
top_terms_query = set(term for term, _ in sorted(query_dict.items(), key=lambda x: x[1], reverse=True)[:N])
top_terms_recommendation = set(term for term, _ in sorted(rec_dict.items(), key=lambda x: x[1], reverse=True)[:N])

# Find the common terms
common_terms = top_terms_query.intersection(top_terms_recommendation)
common_terms_words = [dictionary[int(term)] for term in common_terms]
print(f"Top common terms between {query_book} and {most_similar_book}: {common_terms_words}")


