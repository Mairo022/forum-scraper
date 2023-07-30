import random
import time

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = ""


def main() -> None:
    browser = brave_browser()
    browser.get(URL)
    browser.set_page_load_timeout(30)
    add_cookies(browser)
    browser.refresh()

    boards = get_boards(browser)

    for board, link in boards.items():
        try:
            browser.get(link)
            create_txt_file(board)
            handle_board(browser, board)

        except TimeoutException:
            browser.stop_client()

    print("Program has finished")


def handle_board(browser, board) -> None:
    pagination = get_pagination(browser, 18)
    pages_amount = pagination.get("pages_amount")
    next_pages = pagination.get("next_pages")

    for i in range(1, pages_amount + 1):
        topics = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'topictitle')))
        board_url = browser.current_url

        for j in range(0, len(topics)):
            try:
                title = topics[j].text
                topics[j].click()
                handle_topic(browser, title, board, board_url)

                topics = WebDriverWait(browser, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, 'topictitle')))
            except Exception as e:
                print(e)
                pass

        if i == pages_amount:
            break

        if pages_amount > 1:
            load_next_page(browser, next_pages, i)


def handle_topic(browser, topic, board, board_url) -> None:
    pagination = get_pagination(browser, 10)
    pages_amount = pagination.get("pages_amount")
    next_pages = pagination.get("next_pages")

    for i in range(1, pages_amount + 1):
        print(f" -- Saving {topic}, page {i}, total pages {pages_amount}")
        find_post_details(browser, topic, board)
        time.sleep(random.uniform(0.4, 1.6))

        if i == pages_amount:
            break

        if pages_amount > 1:
            load_next_page(browser, next_pages, i)

    time.sleep(random.uniform(0.4, 1.6))
    browser.get(board_url)


def find_post_details(browser, topic, board) -> None:
    with open(f"{board}.txt", "a") as f:
        posts = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "post")))

        for post in posts:
            post_detail = post.find_element(By.CLASS_NAME, "author")

            author = post_detail.find_element(By.CSS_SELECTOR, "[class^='username']").text
            content = post.find_element(By.CLASS_NAME, "content").text
            date = post_detail.text.split("» ")[1]

            f.write(
                f"Board: {board}\n"
                f"Topic: {topic}\n"
                f"Author: {author}\n"
                f"Date: {date}\n"
                f"\n"
                f"{content}"
                f" \n"
            )


def get_boards(browser) -> dict:
    boards = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[class^='row-itemforum']")))
    board_data = {}

    for board in boards:
        title_element = board.find_element(By.CLASS_NAME, "forumtitle")
        title = title_element.text
        link = title_element.get_attribute("href")

        board_data[title] = link

    return board_data


def get_pagination(browser, posts_amount) -> dict:
    pages = browser.find_element(By.CLASS_NAME, "pagination").find_elements(By.CSS_SELECTOR,
                                                                            ".button:not(.button-icon-only)")
    pages_amount = 1
    next_pages = []

    if pages:
        pages_amount = int(pages[-1].text)
        next_pages = get_next_pages(pages_amount, posts_amount)

    return {"pages_amount": pages_amount, "next_pages": next_pages}


def get_next_pages(pages_amount: int, posts_amount: int) -> list[int]:
    next_pages = []

    for i in range(0, pages_amount):
        next_pages.append(i * posts_amount)

    return next_pages


def load_next_page(browser, next_pages, page) -> None:
    query_prop = "start="
    url_current = browser.current_url
    url_new = url_current.split(query_prop)[0] + "&" + query_prop + str(next_pages[page])

    browser.get(url_new)


def brave_browser() -> webdriver:
    options = webdriver.ChromeOptions()
    options.binary_location = '/usr/bin/brave-browser'
    options.page_load_strategy = 'normal'

    return webdriver.Chrome(options=options)


def create_txt_file(filename) -> None:
    with open(f"{filename}.txt", "w") as f:
        pass


def add_cookies(browser) -> None:
    browser.delete_all_cookies()
    browser.add_cookie({"name": "sid", "value": "m2x37e8d225a5c99c01av695a3k1f6c1"})


main()
