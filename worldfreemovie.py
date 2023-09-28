import streamlit as st
import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures
from tqdm import tqdm

# Function to scrape href links
def scrape_href_links(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', class_='my-button', href=True)
            external_links = []
            for link in links:
                href = link.get('href')
                text = link.text
                if "data-wpel-link" not in link.attrs or link["data-wpel-link"] != "internal":
                    external_links.append({"text": text, "url": href})
            return external_links
        else:
            st.error(f"Failed to fetch the page for URL: {url}. Status code: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"An error occurred for URL: {url} - {str(e)}")
        return None

# Function to extract h4 tag hrefs
def extract_h4_hrefs(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    h4_tags = soup.find_all('h4')
    hrefs = []

    for h4_tag in h4_tags:
        a_tag = h4_tag.find('a')
        if a_tag and 'href' in a_tag.attrs:
            hrefs.append(a_tag['href'])

    return hrefs

# First App: Href Link Scraper
st.title("Href Link Scraper")
st.header("First App")
first_app_url_input = st.text_area("Enter one or more URLs (one per line):")
if st.button("Run First App"):
    first_app_urls = first_app_url_input.strip().split('\n')
    first_app_results = []

    def scrape_href_links_with_progress(url):
        result = scrape_href_links(url)
        return result

    with st.spinner("Running First App..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(scrape_href_links_with_progress, first_app_urls))

        for result in results:
            if result:
                first_app_results.extend(result)

    if first_app_results:
        st.success("First App Execution Successful!")

# Second App: H4 Tag Href Extractor
st.title("H4 Tag Href Extractor")
st.header("Second App")

# Automatically use the URLs from the first app results as input for the second app
if first_app_results:
    st.write("Using the URLs from the first app results as input for the second app:")

    def extract_h4_hrefs_with_progress(url):
        result = extract_h4_hrefs(url)
        return result

    for i, result in enumerate(first_app_results, start=1):
        second_app_url_input = result['url']
        second_app_results = []

        with st.spinner(f"Running Second App - URL {i}..."):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                second_app_results = list(executor.map(extract_h4_hrefs_with_progress, [second_app_url_input]))

        st.header(f"Second App - URL {i}: {second_app_url_input}")

        if second_app_results:
            st.success("Second App Execution Successful!")
            for href in second_app_results[0]:
                st.write(f"- [{href}]({href})")
        else:
            st.warning("Second App Execution Failed!")
