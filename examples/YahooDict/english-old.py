import urllib.request;
from urllib.parse import quote
from bs4 import BeautifulSoup
import subprocess
import platform
import datetime
import json
import wget

# Download_dir="C:/Users/Yu-Hsien/AppData/Roaming/Anki2/YuHsien/collection.media/"
Download_dir="/home/yu/.local/share/Anki2/YuHsien/collection.media/"
Anki="../../addToAnkiEnglish.py"

def look_up_from_yahoo(word, Collection, Deck):
    # Eliminate the end of line delimiter
    word = word.splitlines()[0]
    wordUrl = urllib.parse.quote(word, safe='')
    url="https://tw.dictionary.search.yahoo.com/search?p={}".format(wordUrl)
    content = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(content, 'lxml')
    front_word = ""
    back_word = ""

    print(" ")
    print('<<'+word+'>>')
    print(" ")
    # Get the URL of the sound media
    sound = json.loads(soup.find('span', id='iconStyle').get_text())
    
    # Download the sound media and store at the specific directory (%username%/collection.media) and with a specific file name (Py_%word%.mp3)
    for soundCnt in range(0,len(sound['sound_url_1'])):
        if(bool(sound['sound_url_1'][soundCnt]) == True):
            wget.download(sound['sound_url_1'][soundCnt]["mp3"], out=Download_dir+"Py_"+word+".mp3")
            break

    # Insert the sound media into the card
    front_word = "[sound:Py_"+word+".mp3]" + word + "<br>"

    explain = soup.find('div', class_='explain')
    partOfSpeech = explain.find_all('div', class_='compTitle')

    # POScont => the content of part of speech 
    POScont = explain.find_all('ul', class_='compArticleList')

    for i in range(0,len(POScont)):
        cnt = 1
        if(len(partOfSpeech) == 0):
            POSclean = ""
        else:
            POSclean = '(' + partOfSpeech[i].get_text().split('.')[0] + '.)' + "<br>"
        front_word = front_word + POSclean
        for j in POScont[i].find_all('span', id='example', class_='example'):
            front_word = front_word + str(cnt) + '. '
            for k in range(0,len(j.contents)-1):
                front_word += j.contents[k].string
            front_word += "<br>"
            cnt = cnt + 1 
        back_word = back_word + POSclean
        for j in POScont[i].find_all('h4'):
            back_word = back_word + j.get_text() + '<br>'
    print("")
    print('front_card={}'.format(front_word))
    print('back_card={}'.format(back_word))

    if 0 == len(back_word):
        return
    if "Windows" == platform.system():
        subprocess.run(['python', Anki, Collection, Deck, front_word, back_word])
    else:
        subprocess.run(['python3', Anki, Collection, Deck, front_word, back_word])

count=0
with open('config_E.json', encoding='utf-8') as data_file:
    data = json.load(data_file)

start_time=datetime.datetime.now().replace(microsecond=0)
for profile in data["profiles"]:
    with open(profile["file"], "r", encoding='utf-8') as file:
		# Get the word from each line in file
        for word in file:
            count += 1
            look_up_from_yahoo(word, profile["collection"], profile["deck"])

end_time=datetime.datetime.now().replace(microsecond=0)
print("--------------------------")        
print("Takes {} to add {} cards".format(end_time - start_time ,count))
