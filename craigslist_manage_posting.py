import getpass
import logging
import re

from dateutil import parser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

CRAIGSLIST_LOGIN_PAGE_URL = "https://accounts.craigslist.org/login/home"
CRAIGSLIST_LOGOUT_PAGE_URL = "https://accounts.craigslist.org/logout"
POSTING_PAGE_URL = "https://accounts.craigslist.org/login/home?filter_page={page_number}&show_tab=postings"
PAGE_ROWS_LIMIT = 50
ACTIVE_STATUS_BUTTONS_COUNT = 4
DELETED_STATUS_BUTTONS_COUNT = 3
ACTIVE = 'Active'
DELETED = 'Deleted'
DISPLAY = 'display'
DELETE = 'delete'
EDIT = 'edit'
REPOST = 'repost'
ACTIONS = [DISPLAY, DELETE, REPOST, EDIT]


logging.basicConfig(level=logging.INFO)


class CraigslistPostManager:

    def __init__(self, email=None, password=None, statuses=[], from_page=1, to_page=10,
                 pages=[], areas=[], subareas=[], categories=[], posted_dates=[], posting_ids=[], titles=[],
                 titles_regex=None):

        def get_or_override(var, optional_var, var_str, optional_var_str):
            if var and optional_var:
                logging.warning('Value(s) for {} will be used to override value(s) of {}'
                                .format(var_str, optional_var_str))
                return None

            return optional_var

        def check_type_or_raise(var, var_str, expected_var_types):
            if var and type(var) not in expected_var_types:
                raise Exception('Expected type(s) {} for variable {}. Given type is {}'
                                .format(', '.join(expected_var_types), var_str, type(var)))

        self.email = email
        self.password = password

        self.statuses = statuses
        check_type_or_raise(self.statuses, 'statuses', [list])

        self.pages = pages
        check_type_or_raise(self.pages, 'pages', [list, range])

        self.from_page = get_or_override(pages, from_page, 'pages', 'from_page')
        check_type_or_raise(self.from_page, 'from_page', [int])

        self.to_page = get_or_override(pages, to_page, 'pages', 'to_pages')
        check_type_or_raise(self.to_page, 'to_page', [int])

        self.areas = areas
        check_type_or_raise(self.areas, 'areas', [list])

        self.sub_areas = subareas
        check_type_or_raise(self.sub_areas, 'subareas', [list])

        self.categories = categories
        check_type_or_raise(self.categories, 'categories', [list])

        self.posted_dates = [parser.parse(date_str) for date_str in posted_dates]

        self.posting_ids = posting_ids
        check_type_or_raise(self.posting_ids, 'posting_ids', [list])

        self.titles = titles
        check_type_or_raise(self.titles, 'titles', [list])

        self.titles_regex = get_or_override(titles, titles_regex, 'titles', 'titles_regex')
        check_type_or_raise(self.titles_regex, 'titles_regex', [str])

        self.driver = webdriver.Chrome()

    def login(self):
        logging.info('Login page...')

        if not self.email:
            self.email = input('Username: ')

        if not self.password:
            self.password = getpass.getpass('Password: ')

        self.driver.get(CRAIGSLIST_LOGIN_PAGE_URL)
        email_text_field = self.driver.find_element_by_id('inputEmailHandle')
        password_text_field = self.driver.find_element_by_id('inputPassword')
        log_in_button = self.driver.find_element_by_id('login')

        email_text_field.send_keys(self.email)
        password_text_field.send_keys(self.password)
        log_in_button.send_keys(Keys.ENTER)

    def perform_action(self, button, dry_run=False):
        logging.info('Override this method to do more than just click the action button...')
        button_clicked = False
        if not dry_run:
            button.send_keys(Keys.ENTER)
            button_clicked = True
        return button_clicked or dry_run

    def manage_posts(self, perform_action, dry_run=False):

        def parse_buttons(status, buttons, manage_buttons_index):
            buttons_indexes_range = range(
                ACTIVE_STATUS_BUTTONS_COUNT if status == ACTIVE else DELETED_STATUS_BUTTONS_COUNT)

            buttons_dict = dict()
            for i in buttons_indexes_range:
                button = buttons[manage_buttons_index + i]
                buttons_dict[button.get_attribute('value')] = button

            return buttons_dict

        logging.info("Navigating through posting pages...")

        # Actions performed for each row of post
        assert perform_action in ACTIONS

        page_numbers = self.pages or range(self.from_page, self.to_page + 1)
        actioned_ids = set()
        for page_number in page_numbers:

            logging.info('Processing postings on page {}'.format(page_number))

            actioned = True
            while actioned:

                actioned = False
                posting_page_url = POSTING_PAGE_URL.format(page_number=page_number)

                # Navigate to target page
                self.driver.get(posting_page_url)

                # fetch all rows of postings on current page
                rows = self.driver.find_elements_by_class_name('posting-row')

                # Fetch all necessary elements
                statuses = self.driver.find_elements_by_class_name('status')
                manage_buttons = self.driver.find_elements_by_class_name('managebtn')  # About 3 or 4 for each row
                titles = self.driver.find_elements_by_class_name('title')
                area_categories = self.driver.find_elements_by_class_name('areacat')
                dates = self.driver.find_elements_by_class_name('dates')
                posting_ids = self.driver.find_elements_by_class_name('postingID')

                # Initialize manage action buttons index.
                manage_buttons_index = 0

                for i, row in enumerate(rows):

                    posting_id = posting_ids[i].text
                    if posting_id in actioned_ids:
                        continue

                    if self.posting_ids and posting_id not in self.posting_ids:
                        continue

                    status = statuses[i].text
                    manage_buttons_dict = parse_buttons(status, manage_buttons, manage_buttons_index)

                    if self.statuses and status not in self.statuses:
                        continue

                    title = titles[i].text
                    print(title, re.match(self.titles_regex, title))
                    if self.titles and title not in self.titles:
                        continue

                    elif self.titles_regex and not re.match(self.titles_regex, title):
                        continue

                    areacat_tokens = area_categories[i].text.split()
                    area = areacat_tokens[0]
                    sub_area = areacat_tokens[2] if areacat_tokens[1] == '-' else None
                    category = ' '.join(areacat_tokens[3:]) if sub_area else ' '.join(areacat_tokens[1:])
                    if self.areas and area not in self.areas:
                        continue

                    if self.categories and category not in self.categories:
                        continue

                    dt_str = dates[2 * i].text
                    dt = parser.parse(dt_str)
                    if self.posted_dates and dt not in self.posted_dates:
                        continue

                    # Perform Action might navigate to a different manage page. If so, then we need to revisit the
                    # current posting page after navigating away
                    button_clicked = self.perform_action(manage_buttons_dict[perform_action], dry_run)
                    if button_clicked:
                        logging.info('Clicked {} for posting id: {}'.format(perform_action, posting_id))
                        actioned_ids.add(posting_id)
                        actioned = True
                        break

    def logout(self):
        self.driver.get(CRAIGSLIST_LOGOUT_PAGE_URL)

    def close(self):
        self.driver.quit()
