# Selenium-Craigslist

This is a collection of scripts to manage your [Craigslist](http://www.craigslist.org/) postings using
[Selenium-Python](https://selenium-python.readthedocs.io/).
This script works with Chrome, but I am fairly certain that it will work with any other browser with a few tweaks.

## Disclaimer
I don't work for Craigslist, nor do I have any affiliation with Craigslist.
This module was implemented just for me to speed up my work.
It should not be used for crawling or downloading data from Craigslist.

I was unhappy how Craigslist doesn't have a good API support to manage postings. So, all work that I had to do was manual.
So, I decided to write a Selenium-Python script to do some basic work of mine. Hope this helps you guys!

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You may use your favorite version of Chrome and Python. I use Pyton 3.7.1.
All you need to make sure is you would need the right web-driver that you can download from this [page](https://www.seleniumhq.org/download/).
Depending on your machine, you may want to configure this in System PATH too.

### Installing

Follow the next steps to help you get the project setup:

Clone this project onto your system, and navigate in to the project folder.

```
git clone project
cd project_folder_name
```

Optional step to setup virtualenv. If you don't have it, then you may either follow this page to get it installed,
or just install all the dependencies at system level. Up to you really.

```
virtualenv -p python3.7 venv
source venv/bin/activate
```

This should activate your virtualenv, and you should see a prompt similar to:

```
(venv) personal-mac william$
```

Install all the requirements. There aren't many actually.

```
pip install -r requirements.txt
```

The **main.py** is the entry point. So, let's try running that. You may change the call as you like in this file.
If any variables are not set, then feel free to set them as you would like. If not, then you should get an appropriate
exception mentioning what is missing.

```
python3.7 main.py
```

This should open up a new Chrome instance and start navigating to Login Page, and if the login is successful, you may be
automatically taken to the Craigslist's postings manage page and manage posts as you have called.

## Customize Implementation

Not sure if you noticed. If your main works fine, the code just navigates through the pages, and doesn't really perform
any actions. That is because the **main.py** is just a sample dry run of sorts. To get the code working you would have to
make some code changes.

The beef of this script is in **craigslist_manage_posting.py**. If you really want the script to click some buttons on
the postings page, then pass if **dry_run=False** when calling **manage_posts(action, dry_run)**.

When a button is clicked, usually this navigates to a different page. So, if you want to add more functionality, then best
way is to create a new class and inherit **CraigslistPostManager**, and then override the **perform_action(button, dry_run)**.

```
class MyCustomCraigslistPostManager(CraigslistPostManager):

    def perform_action(button, dry_run):
        print('I am overriding this to click the button and perform more actions, before returning to postings page.')

        return was_button_clicked
```

## License

This project is licensed under the MIT License.
