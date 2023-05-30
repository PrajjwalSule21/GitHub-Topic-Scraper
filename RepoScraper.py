import requests
from bs4 import BeautifulSoup
import pandas as pd



def topic_page_authentication(url):
    
    topics_url = url
    response = requests.get(topics_url)
    page_content = response.text
    doc = BeautifulSoup(page_content, 'html.parser')
    return doc


def topicSraper(doc):
    
    # Extract title 
    title_class = 'f3 lh-condensed mb-0 mt-1 Link--primary'
    topic_title_tags = doc.find_all('p', {'class':title_class})

    # Extract description
    description_class = 'f5 color-fg-muted mb-0 mt-1'
    topic_desc_tags = doc.find_all('p', {'class':description_class})

    # Extract link
    link_class = 'no-underline flex-1 d-flex flex-column'
    topic_link_tags = doc.find_all('a',{'class':link_class})

    #Extract all the topic names
    topic_titles = []
    for tag in topic_title_tags:
        topic_titles.append(tag.text)

    #Extract the descrition text of the particular topic
    topic_description = []
    for tag in topic_desc_tags:
        topic_description.append(tag.text.strip())

    #Extract the urls of the particular topics
    topic_urls = []
    base_url = "https://github.com"
    for tags in topic_link_tags:
        topic_urls.append(base_url + tags['href'])

    topics_dict = {
    'Title':topic_titles,
    'Description':topic_description,
    'URL':topic_urls
    }

    topics_df = pd.DataFrame(topics_dict)

    return topics_df


def topic_url_extractor(dataframe):
    
    url_lst = []
    for i in range(len(dataframe)):
        topic_url = dataframe['URL'][i]
        url_lst.append(topic_url)
    return url_lst

def parse_star_count(stars_str):
    
    stars_str = stars_str.strip()[6:]
    if stars_str[-1] == 'k':
        stars_str =  float(stars_str[:-1]) * 1000
    return int(stars_str)


def get_repo_info(h3_tags, star_tag):
    base_url = 'https://github.com'
    a_tags = h3_tags.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url = base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url


def topic_information_scraper(topic_url):
    # page authentication
    topic_doc = topic_page_authentication(topic_url)

    # extract name
    h3_class = 'f3 color-fg-muted text-normal lh-condensed'
    repo_tags = topic_doc.find_all('h3', {'class':h3_class})

    #get sart tag
    star_class = 'tooltipped tooltipped-s btn-sm btn BtnGroup-item color-bg-default'
    star_tags = topic_doc.find_all('a',{'class':star_class})

    #get inforation about the topic
    topic_repos_dict = {
    'username': [],
    'repo_name': [],
    'stars': [],
    'repo_url': []
    }

    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])
        
        
    return pd.DataFrame(topic_repos_dict)


        





if __name__ == "__main__":
    url = 'https://github.com/topics'
    topic_dataframe = topicSraper(topic_page_authentication(url))
    topic_dataframe.to_csv('GitHubtopics.csv', index=None)

    # Make Other CSV files acording to the topics
    url = topic_url_extractor(topic_dataframe) 
    name = topic_dataframe['Title']
    for i in range(len(topic_dataframe)):
        new_df = topic_information_scraper(url[i])
        new_df.to_csv(f'GitHubTopic_CSV-Files/{name[i]}.csv', index=None)

