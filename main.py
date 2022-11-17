from fastapi import FastAPI
import os
import requests
from bs4 import BeautifulSoup
import zipfile
import  praw
import asyncpraw
import time
from starlette.responses import FileResponse

app = FastAPI()


@app.get("/")
async def root():
    reddit = asyncpraw.Reddit(
        client_id='WfkcHPYUP8ddD0cCA7tVsQ',
        client_secret='7xeFrkikKbI12AOW8DQdr2WoT5bcJw',
        user_agent='Memeland',
    )
    subreddits = ['meme','animemes','4PanelCringe','funny']

    for subredditItem in subreddits:
        #get all image in memes subreddit and download them
        subreddit = await reddit.subreddit(subredditItem)
        async for submission in subreddit.top(limit=10):
            if submission.url.endswith('.jpg') or submission.url.endswith('.png') or submission.url.endswith('.gif'):
                extension = str(submission.url.split('.')[-1])
                if not os.path.exists(f'./Memes/{subredditItem}/{submission.id}.{extension}'):
                    r = requests.get(submission.url, allow_redirects=True)
                    if not os.path.isdir(f'./Memes/{subredditItem}'):
                        os.makedirs(f'./Memes/{subredditItem}')
                    with open(f'Memes/{subredditItem}/{submission.id}.{extension}', 'wb') as f:
                        f.write(r.content)

     # #make a zip file from memes directory
     # zipObj = zipfile.ZipFile('Memes.zip', 'w')
     # for folderName, subfolders, filenames in os.walk('./Memes'):
     #     for filename in filenames:
     #         filePath = os.path.join(folderName, filename)
     #         zipObj.write(filePath)
     # zipObj.close()
    telegram()

    return {"message": "Hello World"}


def telegram():
    apiToken = '5746760871:AAEZbq_-e01nF602wCinxXjGRFMbWh77YMQ'
    chatID = '-1001615139079'
    apiURL = f'https://api.telegram.org/bot{apiToken}/'+'sendPhoto?chat_id='+chatID

    bin = []

    #send all files in ./Memes directory to telegram
    for folderName, subfolders, filenames in os.walk('./Memes'):
        for filename in filenames:
            #if filename is not in the log file send it to telegram
            if not filename in open('log.txt').read():
                #get the image in manipilable format
                filePath = os.path.join(folderName, filename)
                files = {'photo': open(filePath, 'rb')}
                #send the image to telegram
                r = requests.post(apiURL, files=files)
                #retry 3 times if  status code start with 5 or 4 and different from 429
                if r.status_code == 429:
                    time.sleep(1)
                    r = requests.post(apiURL, files=files)
                else:
                    #write to error log file
                    with open('error.txt', 'a') as f:
                        f.write(f'{r.status_code} {r.reason} {r.text} {filePath}  {time.ctime()}')
                    continue

                print(r.status_code, r.reason, r.content)
                #write all sent files name to a log filr
                with open('log.txt', 'a') as f:
                    f.write(filePath+'\n')
                #wait 1 second to avoid spamming
                time.sleep(1)
                #save the image full path in an array
                bin.append(filePath)
    #remove all sent files
    for i in bin:
        os.remove(i)