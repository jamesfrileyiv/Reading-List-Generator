from bs4 import BeautifulSoup
import requests
import json


# TODO : Get Author Name
def get_author_name():
    return input("Enter Author's Name: ")


# TODO : Search author on Literature-Map.com
def query_related_authors(author, header):
    base_url = "https://www.literature-map.com/"
    author = author.replace(" ", "+")
    search_string = base_url + author
    return requests.get(search_string, headers=header)


# TODO : Request Error Checking
def check_valid_url(request):
    """Given an http request response, checks status code 200 (good response)"""
    if request.status_code == 200:
        return True
    else:
        return False


# TODO : Get List of Authors
def get_related_authors(request, author):
    """Assumes a valid request. Returns List of Related Authors"""
    soup = BeautifulSoup(request.content, "html.parser")
    result_set = soup.find_all("a", {"class": "S"})
    authors = {}
    for _ in result_set:
        authors[_.string] = []
    return authors


# TODO : For Each Author, return top 3 books on Goodreads.com
def get_books(author_dict, header):
    names_to_pop = []
    for name in author_dict:
        r1 = requests.get(construct_initial_query(name), headers=header)
        if r1.status_code == 200:
            author_goodreads_url = get_goodreads_url(r1, name)
            if author_goodreads_url != "":
                r2 = requests.get(author_goodreads_url, headers=header)
                if r2.status_code == 200:
                    top_three_books = get_top_three_books(r2)
                    author_dict[name] = top_three_books
                else:
                    names_to_pop.append(name)
            else:
                names_to_pop.append(name)
        else:
            names_to_pop.append(name)
    for name in names_to_pop:
        author_dict.pop(name)
    return author_dict


def construct_initial_query(name):
    """Constructs and returns an http query of the author's name on goodreads"""
    base_url = "https://www.goodreads.com/search?utf8=%E2%9C%93&q="
    search_type = "&search_type=books"
    url_query = base_url + name.replace(" ", "+") + search_type
    return url_query


def get_goodreads_url(request, name):
    """Takes in author's name, and a valid request of searching the author's name on goodreads.
    Returns the url to the author's goodreads page"""
    print(name)
    soup = BeautifulSoup(request.content, "html.parser")
    table = soup.find("table", {"class": "tableList"})
    #print(table)
    print(type(table))
    rows = table.find_all("tr")
    url = ""
    for row in rows:
        author = row.find("a", {"class": "authorName"})
        if name in author.string:
            url = author["href"]
            break
    return url


def get_top_three_books(request):
    """Takes in request of an author's goodreads url. Returns first three books"""
    soup = BeautifulSoup(request.content, "html.parser")
    table = soup.find("table", {"class": "stacked tableList"})
    rows = table.find_all("tr")
    max_titles = 3
    title_list = []
    for row in rows:
        row_title = row.find("a", {"class": "bookTitle"})
        row_title_span = row_title.find("span")
        title = row_title_span.string
        title_list.append(title)
        if len(title_list) == max_titles:
            break
    return title_list


# main / testing
def main():
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77"
                      " Safari/537.36"
    }

    author = get_author_name()
    r = query_related_authors(author, header)
    if check_valid_url(r):
        related_authors = get_related_authors(r, author)
        related_authors = get_books(related_authors, header)
        with open(f'{author}_reading_list.txt', 'w', encoding='utf-8') as f:
            json.dump(related_authors, f, ensure_ascii=False, indent=4)
    else:
        print("There was an error. Please make sure you entered the author's full name and spelled"
              "their name correctly.")


if __name__ == "__main__":
    main()
