
#run "pip install openpyxl"
import pandas
import requests
from bs4 import BeautifulSoup
import pandas
import numpy
import openpyxl
import os
a=[]
data= pandas.read_csv("Input.csv")
data=data.dropna()
new_data=numpy.array(data)
URLS={}
for i in new_data:
    URLS[i[0]]=i[1]


for i in URLS.items():
    try:
        r=requests.get(i[-1]).content
        soup=BeautifulSoup(r,'html.parser')
        heading=soup.find("h1")
        heading=heading.text.strip()
        para=soup.find_all(class_="td-post-content")
        with open(f'resource/{i[0]}.txt','w') as f:
            f.writelines(heading)
            for i in para:
                f.writelines(i.get_text(separator=" ",strip=True))
    except:
        pass


stop_words = []
for file in os.listdir("StopWords"):
    with open (f"StopWords/{file}","r") as f:
        a=f.read()      
        a=a.replace("|"," ")
        a=a.replace("\n"," ")
        a=a.split(" ")
    
    stop_words.extend(list(a))


new_stop_words=[]
for i in stop_words:
    if(i!=""):
        new_stop_words.append(i)


with open ("MasterDictionary/positive-words.txt","r") as f:
    poitivewords=f.read()
    poitivewords=poitivewords.split("\n")


with open ("MasterDictionary/negative-words.txt","r") as f:
    negativewords=f.read()
    negativewords=negativewords.split("\n")


words={}
words_unclean={}
for file in os.listdir("resource"):
    with open (f"resource/{file}","r") as f:
        a=f.read()
        words[file.split(".")[0]]=a.replace(","," ").replace("!"," ").replace("."," ").replace("/"," ").replace(":"," ").replace('"'," ").replace("?"," ").replace("("," ").replace(")"," ").replace("“"," ").replace("’"," ").split(" ")
        words_unclean[file.split(".")[0]]=a.replace(","," ").replace("/"," ").replace(":"," ").replace('"'," ").replace("("," ").replace(")"," ").replace("“"," ").replace("’"," ").split(".")



old_words=words
new_stop_words.append("")
for i,j in words.items():
    temp=[]
    for k in j:
        if k.upper() not in new_stop_words:
            temp.append(k)
    words[i]=temp


score={}
for i,j in words.items():
    pos=0
    neg=0
    for k in j:
        if k.lower() in poitivewords:
            pos+=1
        elif k.lower() in negativewords:
            neg+=1
    score[i]={"URL_ID":i,"URL":URLS[i],"POSITIVE SCORE":pos, "NEGATIVE SCORE":neg}



for i,j in score.items():
    score[i]["POLARITY SCORE"] = (j["POSITIVE SCORE"] - j["POSITIVE SCORE"]) / ((j["POSITIVE SCORE"] + j["POSITIVE SCORE"]) + 0.000001)

    score[i]["SUBJECTIVITY SCORE"] = (j["POSITIVE SCORE"] + j["POSITIVE SCORE"]) / ( len(words[i]) + 0.000001)

    score[i]["AVG SENTENCE LENGTH"] = len(words[i]) / len(words_unclean[i])

    complex_words=0
    total_syllables=0
    for x in words[i]:
        syllables=0
        for y in x:
            if y in ["a","e","i","o","u","A","E","I","O","U"]:
                syllables+=1
        if x[-2:] in ["es","ed"]:
            syllables-=1

        total_syllables += syllables

        if syllables>2 :
            complex_words+=1
    
    score[i]["PERCENTAGE OF COMPLEX WORDS"] = complex_words / len(words[i])

    score[i]["FOG INDEX"] = 0.4 * ( score[i]["AVG SENTENCE LENGTH"] + score[i]["PERCENTAGE OF COMPLEX WORDS"])

    #score[i]["Average Number of Words Per Sentence"] = 
    length=0
    for x in words_unclean[i]:
        split_length=x.split(" ")
        try:

            split_length.remove("")
        except:
            pass
        length+=len(split_length)
    
    score[i]["AVG NUMBER OF WORDS PER SENTENCE"] = length / len(words_unclean[i])

    score[i]["COMPLEX WORD COUNT"]= complex_words

    score[i]["WORD COUNT"] = len(words[i])

    score[i]["SYLLABLE PER WORD"] = total_syllables / len(words[i])
    No_of_pronouns=0
    for x in old_words[i]:
        for y in x:
            if y.lower() in ['i','we','us','ours']:
                if y!="US":
                    No_of_pronouns+=1
    
    score[i]["PERSONAL PRONOUNS"]=No_of_pronouns
    character=0
    for z in words[i]:
        character+=len(z)
        

    score[i]["Average Word Length"] = character / len(words[i])


output=pandas.DataFrame(score.values())
output.to_excel("Output.xlsx",index=False)