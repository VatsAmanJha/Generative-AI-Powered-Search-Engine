from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import google.generativeai as genai

genai.configure(api_key="Your API Key")

model = genai.GenerativeModel("gemini-pro")


def google_search(query):
    """Performs a Google search and returns the search result URL."""
    base_url = "https://www.google.com/search"
    params = {"q": query}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        print(response.url)
        return response.url
    else:
        return "Error: Unable to fetch results"


def best_url_according_to_google_search_result(query):
    """Fetches the best URLs from Google search results."""
    query = "+".join(query.split())
    URL = f"https://www.google.com/search?q={query}"
    html_content = requests.get(URL).text
    soup = BeautifulSoup(html_content, "html.parser")
    url_lst = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/url?q=" in href:
            if "https" in href or "http" in href:
                url = href.split("/url?q=")[1].split("&")[0]
                parsed_url = urlparse(url)
                clean_url = (
                    f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                )
                if "google" not in clean_url:
                    url_lst.append(clean_url)

    return url_lst


def retrieve_text_content_from_url(url_lst):
    """Retrieves and cleans text content from the provided URLs."""
    for url in url_lst:
        try:
            html_content = requests.get(url).text
            soup = BeautifulSoup(html_content, "html.parser")
            text_content = soup.get_text()
            cleaned_text_content = " ".join(text_content.split())
            if len(cleaned_text_content) > 1000:
                return cleaned_text_content, url
        except Exception as e:
            print(f"Error fetching content from {url}: {e}")

    return "No Relevant Data Found"


def generate_content(user_question):
    # Get text content from the best URLs according to Google search results
    text_content, url = retrieve_text_content_from_url(
        best_url_according_to_google_search_result(user_question)
    )
    try:
        # Generate content using the model
        response = model.generate_content(
            f"""User Question:{user_question}
        Text Content:{text_content}
        Provide a relevant at least 100-200 word answer to my User Question from my entire Text Content and your content should have good text decoration format in .html format. I display the Response Text on my website, so ensure the output is always well-formatted in .html.
        NOTE response.text always in HTML under container div  format."""
        )

        if response:
            try:
                html_string_cleaned = response.text.replace("```html", "").replace(
                    "```", ""
                )
                return html_string_cleaned, url
            except:
                return response.text, url
        else:
            return "Not Data Fetch"

    except ValueError as e:
        return f"An error occurred: {e}"


if __name__ == "__main__":
    user_question = input("Search: ")
    print(f"User Question: {user_question}")
    generate_content(user_question)
