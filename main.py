from craigslist_manage_posting import CraigslistPostManager


if __name__ == '__main__':
    cl = CraigslistPostManager(statuses=['Active'], to_page=3, posting_ids=['1', '2'])
    cl.login()
    cl.manage_posts('display', dry_run=True)
    cl.logout()
    cl.close()
