import pandas as pd
import requests as httpr
from pprint import pprint

from splinter import Browser
from bs4 import BeautifulSoup

def scrape():
    # @NOTE: Replace the path with your actual path to the chromedriver
    #executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    executable_path = {'executable_path': 'chromedriver.exe'}


    #For the sake of performance and my own learning I will be using the Request library for retrieving the HTML 
    #Since it will not need to laod images, there should be improved performance.

    #retrieve nasa news items
    browser = Browser('chrome', **executable_path, headless=False)
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    article_title = soup.find("div", class_="content_title").get_text()
    article_body = soup.find("div", class_="article_teaser_body").get_text()
    print(article_title)
    print(article_body)

    browser.quit()

    #retrieve latest nasa mars image url
    base_url = "https://www.jpl.nasa.gov"
    url = base_url + "/spaceimages/?search=&category=Mars"
    http_result = httpr.get(url)

    soup = BeautifulSoup(http_result.content, "html.parser")

    image_page_url = soup.find("a", class_="button fancybox")['data-link']
    new_url = base_url + image_page_url

    http_result = httpr.get(new_url)
    soup = BeautifulSoup(http_result.content, "html.parser")

    full_img_page_url = base_url + soup.find("img", class_="main_image")['src']

    #retrieve last weather tweet
    url = "https://twitter.com/marswxreport?lang=en"
    http_result = httpr.get(url)
    quoted_tweet_optional = ""

    soup = BeautifulSoup(http_result.content, "html.parser")

    tweet_text = soup.find("p", class_="tweet-text").get_text()
    if soup.find("p", class_="QuoteTweet-text") != None:
        quoted_tweet_optional = soup.find("p", class_="QuoteTweet-text").get_text()

    #retrieve table of facts and load to a pandas dataframe
    #option to read the url with dataframe
    url = "http://space-facts.com/mars/"

    mars_facts_df = pd.DataFrame(pd.read_html(url)[0])
    mars_facts_df.columns = ["Feature", "Value"]
    html_facts_table = mars_facts_df.to_html(classes='table-striped')


    #retrieve the hemisphere titles and image URLs
    base_url = "https://astrogeology.usgs.gov"
    url = base_url + "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    http_result = httpr.get(url)

    soup = BeautifulSoup(http_result.content, "html.parser")

    #instantiate variables to be used in main routine
    hemisphere_img_info = []
    original_img_url = ''
    page_info = {}

    #retrieve the image links by class, then store the text before proceeding to the image URL
    for link in soup.find_all("a", class_="product-item"):
        image_title = link.get_text()
        
        url = base_url + link["href"]
        http_result = httpr.get(url)
        image_soup = BeautifulSoup(http_result.content, "html.parser")
        image_url = base_url + image_soup.find("img", class_="wide-image")["src"]
        
        #with no class nor ID, the text of the link is the next best thing to identify the oringal image
        for img_link in image_soup.find_all("a"):
            if (img_link.get_text() == 'Original'):
                original_img_url = base_url + img_link['href']
                
        img_info = {"title": image_title,
                "url_jpg": image_url,
                "original_image_url": original_img_url}
        
        hemisphere_img_info.append(img_info)

        page_info = [{"article_info":{ "article_title": article_title,
                        "article_body": article_body}},
                        {"feature_image": full_img_page_url},
                        {"weather_tweet": tweet_text},
                        {"facts_table": html_facts_table},
                        {"hemispheres": hemisphere_img_info}]

    return page_info
        



