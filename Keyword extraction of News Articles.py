#!/usr/bin/env python
# coding: utf-8

# In[310]:


import requests
import re
from bs4 import BeautifulSoup
import nltk
import subprocess


# In[311]:


url = "https://www.reuters.com/markets"
site = requests.get(url)
soup2 = BeautifulSoup(site.content)
urls = []
for link in soup2.find_all("a", href=re.compile('/article')):
    link = url + link["href"]
    urls.append(link)
urls = set(urls)


# In[312]:


from sklearn.feature_extraction.text import TfidfVectorizer

rawDocs = []
for link in urls:
    soup = BeautifulSoup(requests.get(link).content)
    if soup.find("h1") != None:
        title = soup.find("h1").get_text()
        article = requests.get(link)
        soup = BeautifulSoup(article.content)
        content = ""
        paragraphs = soup.find_all("p")
        for p in paragraphs:
            content += p.get_text() + "\n"
        if (len(content) > 1200) :
            rawDocs.append((title, content, link))
stopWords = nltk.corpus.stopwords.words("english")
stopWords.append("live")
stopWords.append("minute")
stopWords.append("half")
stopWords.append("first half")
stopWords.append("quarter")
tfidf = TfidfVectorizer(stop_words=stopWords, 
                        token_pattern=u'(?ui)\\b\\w*[a-z]+\\w*\\b',
                       ngram_range=(1,2))
tfidfVector = tfidf.fit_transform([i[1] for i in rawDocs])


# In[313]:


import numpy as np

articlesKeywordPairs = []
for i in range(0, len(rawDocs)):
    topIndices = np.flip(np.argsort(tfidfVector[i].toarray()))
    articlesKeywordPairs.append((rawDocs[i][0], rawDocs[i][2], [tfidf.get_feature_names()[j] for j in topIndices[0][:5]]))
topIndices = np.flip(np.argsort(tfidfVector[7].toarray()))
#tfidf.get_feature_names()[np.argmax(tfidfVector[2].toarray())]



# In[228]:


import smtplib, ssl


smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "newskeywordextractor@gmail.com"
password = "ENTER PASSWORD HERE!"

# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to server and send email
try:
    server = smtplib.SMTP(smtp_server,port)
    server.ehlo() # Can be omitted
    server.starttls(context=context) # Secure the connection
    server.ehlo() # Can be omitted
    server.login(sender_email, password)
    # TODO: Send email here
    message = ""
    for i in articlesKeywordPairs:
        message += i[0] + "\n" + "Keywords: " + ', '.join(i[2]) + "\n" + i[1] + "\n\n"
    server.sendmail("keywords@sidnews.com", "siddharthgupta555t@gmail.com", message)
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    print("Sent the email!")
    server.quit()
    

