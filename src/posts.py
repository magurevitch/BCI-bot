import requests
from .tumblr_keys import *
import html
import re
from bs4 import BeautifulSoup

url = "https://api.tumblr.com/v2/blog/badconlangingideas/posts?tag=conlanging&api_key=" + consumer_key
common_tags = ['submissions', 'submission', 'conlang', 'conlanging', 'conlangs', 'bad conlanging ideas']
rename = {"mag":"matan-matika","tanner swett":"Tanner Swett"}

class Posts:
    def __init__(self):
        self.by_author = {}
        self.by_number = {}
        
        self.getData()
        
    def getData(self):
        offset = 0
    
        response = requests.get(url)
        json = response.json()
        posts = json["response"]["posts"]
        
        while len(posts) > 0:     
            for post in posts:
                if post["summary"][0] == '#':
                    title = ''.join(c for c in post["summary"] if not c in "#0123456789.-").strip()
                
                    full_number = re.search("\d*\.?\d",post["summary"]).group()
                    base_number = int(float(full_number))
                    decimal = float(full_number) % 1
                    
                    author = findAuthor(post)
                    text = findText(post)
                    
                    post_url = post["post_url"]
                    note_count = post["note_count"]
                    
                    if author not in self.by_author:
                        self.by_author[author] = []
                    self.by_author[author] += [full_number]
                    
                    self.by_number[full_number] = {"author":author,"title":title,"text":text,"base":base_number,"url":post_url,"note count":note_count}
                    if decimal > 0:
                        self.by_number[full_number]["following"] = 2
                    elif base_number + 0.5 in self.by_number:
                        self.by_number[full_number]["following"] = 1
                    else:
                        self.by_number[full_number]["following"] = 0
            offset += 20
            
            response = requests.get(url + "&offset=" + str(offset))
            json = response.json()
            posts = json["response"]["posts"]
        print(self.by_author)
            
def findAuthor(post):
    if "post_author" in post and post["post_author"] != "official-data":
        author = post["post_author"]
    else:
        tags = [tag for tag in post["tags"] if tag not in common_tags]
        if tags == []:
            #one of them Anaïs forgot to tag, but it was made by poster mag
            author = "mag"
        else:
            author = tags[0]
                    
    if author in rename:
        return rename[author]
    return author
    
def findText(post):
    if "body" in post:
        text = post["body"]
    else:
        text = post["description"]
    soup = BeautifulSoup(text, "html.parser")
                        
    return fixHTML(soup)

def fixHTML(string):
    if string.string:
        newString = html.unescape(string.string).replace("<br/>","\n")
        if string.name == 'p':
            newString += '\n\n'
        return newString 
    else:
        return "".join(map(fixHTML, string.contents))