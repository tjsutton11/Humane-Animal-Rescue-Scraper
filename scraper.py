import requests
from bs4 import BeautifulSoup as soup
import random
import shutil
import cssutils
import os
import tweepy
import time

URL = 'https://www.humaneanimalrescue.org/available-pets/'

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/77.0.3865.90 Safari/537.36'}


class Pet:
    def __init__(self, name, age, gender, breed, location, link, img):
        self.name = name
        self.age = age
        self.gender = gender
        self.breed = breed
        self.location = location
        self.link = link
        self.img = img


# Opens connection with site, scrapes pet information, and returns a List of adoptable pets
def scrape_site():
    # Opening connection with web page, grabbing content
    adoption_page = requests.get(URL, headers=headers)

    # HTML parsing
    page_soup = soup(adoption_page.content, 'html.parser')

    # Grabs every pet available for adoption
    articles = page_soup.findAll("article", {"class": "pet_type-all"})

    pet_list = []

    for article in articles:
        # Grabs pet name
        name_container = article.findAll("h3", {"class": "pet-name"})
        name = name_container[0].text

        # Grabs pet details
        details_container = article.findAll("li")
        age = details_container[0].text
        gender = details_container[1].text
        breed = details_container[2].text
        location = details_container[3].text

        # Grabs link to pet
        for link in article.findAll('a'):
            pet_link = link.get('href')

        # Finds URL for pet photo
        img_container = article.find("div")['style']
        style = cssutils.parseStyle(img_container)
        img = style['background-image']
        img = img.replace('url(', '').replace(')', '')

        pet1 = Pet(name, age, gender, breed, location, pet_link, img)
        pet_list.append(pet1)

    return pet_list


def choose_random_pet(pet_list):
    num = len(pet_list)
    value = random.randint(1, num)
    chosen_pet = pet_list[value]
    return chosen_pet


def retrieve_photo(chosen_pet):
    # Grabs img URL from Pet object
    img_url = chosen_pet.img
    # Opens the url, sets stream to True, will return stream content
    resp = requests.get(img_url, stream=True)
    # Open a local file with 'write binary' permission
    local_file = open('pet_photo.jpg', 'wb')
    # Decode_content to True, otherwise image file size will be 0
    resp.raw.decode_content = True
    # Copy response stream raw data to local image file
    shutil.copyfileobj(resp.raw, local_file)
    # Remove the image url response object
    del resp


# Authenticates access to API
def o_auth():
    consumer_key = os.environ.get('consumer')
    consumer_secret = os.environ.get('consumer_secret')
    access_token = os.environ.get('access')
    access_token_secret = os.environ.get('access_secret')
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        return auth
    except Exception as e:
        return None


web_scrape = scrape_site()
adopt = choose_random_pet(web_scrape)
retrieve_photo(adopt)

# Authenticates user and passes that to Twitter's API
authentication = o_auth()
api = tweepy.API(authentication)

# Posts a tweet that includes the pet name, age, gender, breed, location, and link
api.update_with_media('pet_photo.jpg', 'Name: ' + adopt.name + '\n' + adopt.age + '\n' + adopt.gender + '\n'
                      + adopt.breed + '\n' + adopt.location + '\n' + 'Link: ' + adopt.link + '\n' + '#adopt #pittsburgh')
print('A pet has been posted!')

