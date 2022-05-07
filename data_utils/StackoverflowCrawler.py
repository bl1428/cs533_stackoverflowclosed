import stackapi
import datetime
import logging
import time
import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from fp.fp import FreeProxy

# config
startDate = '2022-03-01'
endDate = '2022-03-31'
timeInterval = 43200 #split the request by an hour(3600), half an hour(1800), or 15min(900)
stackType = 'questions' # 'questions', 'answers', 'posts', 'comments'
saveDatasetName = '4_questions'
cleanedDatasetName = '4_questions_cleaned'

proxy_country=[]
pd.set_option('display.max_columns', None)
logging.basicConfig(format='[%(asctime)s %(levelname)-8s] %(message)s', level=logging.DEBUG, handlers=[logging.FileHandler('spider.log',mode='w'), logging.StreamHandler()])

# StackAPI start

# setup API with new proxy
def proxy_change():
    proxy = {'https': FreeProxy(country_id=proxy_country, timeout=0.3, rand=True).get()}
    logging.info('Change proxy server: ' + str(proxy['https']))
    good_proxy_found = False
    while good_proxy_found is False:
        try:
            logging.info('validate proxy server...')
            SITE = stackapi.StackAPI('stackoverflow', proxy=proxy)
            SITE.page_size = 100  # limit per api call is 100
            SITE.max_pages = 1000000  # number of api call
            good_proxy_found = True
            logging.info('This proxy server is workable: ' + str(proxy['https']))
        except Exception as e:
            logging.warning(e)
            logging.info('validation failed')
            proxy = {'https': FreeProxy(country_id=proxy_country, timeout=0.3, rand=True).get()}
            logging.info('Change proxy server: ' + str(proxy['https']))
            pass
    return SITE

spider_start_time = datetime.datetime.utcnow()
fromDate = int(datetime.datetime.strptime(startDate, '%Y-%m-%d').timestamp())
toDate = int(datetime.datetime.strptime(endDate, '%Y-%m-%d').timestamp())
SITE = proxy_change()


#First batch of scraping
timeInterval_start = fromDate
timeInterval_end = fromDate+timeInterval
logging.info('scraping posts from ' + datetime.datetime.fromtimestamp(timeInterval_start).isoformat() + ' to ' + datetime.datetime.fromtimestamp(timeInterval_end).isoformat())
posts = SITE.fetch(stackType, fromdate=timeInterval_start, todate=timeInterval_end, sort='votes', order='desc', filter='withbody')
df = pd.DataFrame(posts['items'])
logging.info('finish batch. size:'+str(len(posts['items']))+' quota_remaining:'+str(posts['quota_remaining'])+' backoff:'+str(posts['backoff']))

#Loop the rest scraping
while(timeInterval_end <= toDate):
    logging.info('scraping posts from '+datetime.datetime.fromtimestamp(timeInterval_start).isoformat()+' to '+ datetime.datetime.fromtimestamp(timeInterval_end).isoformat())
    batch_start_time = datetime.datetime.utcnow()
    try:
        posts = SITE.fetch(stackType, fromdate=timeInterval_start, todate=timeInterval_end, sort='votes', order='desc', filter='withbody')
    except Exception as e:
        logging.warning(e)
        SITE = proxy_change()
        continue
    df = df.append(posts['items'])
    batch_finish_time = datetime.datetime.utcnow()
    batch_time_diff = batch_finish_time - batch_start_time
    logging.info('finish batch. size:'+str(len(posts['items']))+' time:'+str(batch_time_diff.seconds)+'s quota_remaining:'+str(posts['quota_remaining'])+' backoff:'+str(posts['backoff']))
    if posts['backoff']>=1:
        time.sleep(int(posts['backoff'])+1)
    timeInterval_start = timeInterval_start + timeInterval
    timeInterval_end = timeInterval_end + timeInterval

df = df.drop_duplicates(subset=['answer_count','score','last_activity_date','creation_date','last_edit_date','question_id','link'])

# Save it as csv
def save_dataset(df, df_name):
    logging.info('Saving dataset...')
    # if not os.path.exists('/datasets'):
    #     os.makedirs('/datasets')
    df.to_csv(r'./datasets/' + df_name + '.csv', index=False, header=True)
    logging.info('Saved parsed dataset')

save_dataset(df, saveDatasetName)


# Print process time
spider_finish_time = datetime.datetime.utcnow()
time_diff =spider_finish_time-spider_start_time
logging.info("Scraping stackoverflow within {} seconds".format(time_diff.seconds))


# example response for questions
# From https://api.stackexchange.com/docs/questions#page=1&pagesize=5&fromdate=2020-01-01&todate=2020-01-02&order=desc&sort=votes&filter=default&site=stackoverflow&run=true
    # {
    #     "items": [
    #         {
    #             "tags": [
    #                 "c++",
    #                 "c++11",
    #                 "types",
    #                 "stdint",
    #                 "cstdint"
    #             ],
    #             "owner": {
    #                 "reputation": 1996,
    #                 "user_id": 2534689,
    #                 "user_type": "registered",
    #                 "accept_rate": 100,
    #                 "profile_image": "https://i.stack.imgur.com/GoNJo.png?s=128&g=1",
    #                 "display_name": "Rick de Water",
    #                 "link": "https://stackoverflow.com/users/2534689/rick-de-water"
    #             },
    #             "is_answered": true,
    #             "view_count": 1447,
    #             "accepted_answer_id": 59553656,
    #             "answer_count": 2,
    #             "score": 26,
    #             "last_activity_date": 1580421796,
    #             "creation_date": 1577882201,
    #             "last_edit_date": 1580421796,
    #             "question_id": 59552571,
    #             "content_license": "CC BY-SA 4.0",
    #             "link": "https://stackoverflow.com/questions/59552571/how-to-check-if-fixed-width-integers-are-defined",
    #             "title": "How to check if fixed width integers are defined"
    #         },
    #         {
    #             "tags": [
    #                 "go",
    #                 "jetbrains-ide",
    #                 "goland"
    #             ],
    #             "owner": {
    #                 "reputation": 261,
    #                 "user_id": 12637942,
    #                 "user_type": "registered",
    #                 "profile_image": "https://www.gravatar.com/avatar/64ae0a55e5096d8b4672f482be4b886d?s=128&d=identicon&r=PG&f=1",
    #                 "display_name": "David",
    #                 "link": "https://stackoverflow.com/users/12637942/david"
    #             },
    #             "is_answered": true,
    #             "view_count": 5252,
    #             "answer_count": 8,
    #             "score": 25,
    #             "last_activity_date": 1614861337,
    #             "creation_date": 1577915594,
    #             "last_edit_date": 1577917831,
    #             "question_id": 59556394,
    #             "content_license": "CC BY-SA 4.0",
    #             "link": "https://stackoverflow.com/questions/59556394/goland-jetbrains-shows-error-message-unresolved-reference-but-code-compiles",
    #             "title": "GoLand (JetBrains) shows error message &quot;Unresolved Reference&quot;. But Code compiles and runs"
    #         },
    #         {
    #             "tags": [
    #                 "java",
    #                 "java-8",
    #                 "comparator",
    #                 "java-11",
    #                 "treeset"
    #             ],
    #             "owner": {
    #                 "reputation": 27764,
    #                 "user_id": 3764965,
    #                 "user_type": "registered",
    #                 "accept_rate": 94,
    #                 "profile_image": "https://i.stack.imgur.com/5aIx2.jpg?s=128&g=1",
    #                 "display_name": "Nikolas Charalambidis",
    #                 "link": "https://stackoverflow.com/users/3764965/nikolas-charalambidis"
    #             },
    #             "is_answered": true,
    #             "view_count": 655,
    #             "accepted_answer_id": 59553083,
    #             "answer_count": 1,
    #             "score": 21,
    #             "last_activity_date": 1577927284,
    #             "creation_date": 1577886052,
    #             "last_edit_date": 1577927145,
    #             "question_id": 59553029,
    #             "content_license": "CC BY-SA 4.0",
    #             "link": "https://stackoverflow.com/questions/59553029/why-doesnt-removing-from-a-treeset-with-a-custom-comparator-remove-a-larger-set",
    #             "title": "Why doesn&#39;t removing from a TreeSet with a custom comparator remove a larger set of items?"
    #         },
    #         {
    #             "tags": [
    #                 "c++",
    #                 "set",
    #                 "stdset"
    #             ],
    #             "owner": {
    #                 "reputation": 2328,
    #                 "user_id": 5954825,
    #                 "user_type": "registered",
    #                 "profile_image": "https://www.gravatar.com/avatar/b46e345831a9b1beeb8bfee5cbf70b6f?s=128&d=identicon&r=PG&f=1",
    #                 "display_name": "mfnx",
    #                 "link": "https://stackoverflow.com/users/5954825/mfnx"
    #             },
    #             "is_answered": true,
    #             "view_count": 2180,
    #             "accepted_answer_id": 59555327,
    #             "answer_count": 2,
    #             "score": 16,
    #             "last_activity_date": 1577969124,
    #             "creation_date": 1577905155,
    #             "last_edit_date": 1577969124,
    #             "question_id": 59555257,
    #             "content_license": "CC BY-SA 4.0",
    #             "link": "https://stackoverflow.com/questions/59555257/does-stdset-store-objects-contiguously-in-memory",
    #             "title": "Does std::set store objects contiguously in memory?"
    #         },
    #         {
    #             "tags": [
    #                 "flutter",
    #                 "dart",
    #                 "navigation",
    #                 "uinavigationbar",
    #                 "drawer"
    #             ],
    #             "owner": {
    #                 "reputation": 1616,
    #                 "user_id": 11320345,
    #                 "user_type": "registered",
    #                 "profile_image": "https://i.stack.imgur.com/Z4D76.jpg?s=128&g=1",
    #                 "display_name": "lordvidex",
    #                 "link": "https://stackoverflow.com/users/11320345/lordvidex"
    #             },
    #             "is_answered": true,
    #             "view_count": 18793,
    #             "accepted_answer_id": 59554654,
    #             "answer_count": 4,
    #             "score": 15,
    #             "last_activity_date": 1615218326,
    #             "creation_date": 1577897655,
    #             "question_id": 59554348,
    #             "content_license": "CC BY-SA 4.0",
    #             "link": "https://stackoverflow.com/questions/59554348/how-can-i-change-drawer-icon-in-flutter",
    #             "title": "How can I change Drawer icon in flutter?"
    #         }
    #     ],
    #     "has_more": true,
    #     "backoff": 10,
    #     "quota_max": 10000,
    #     "quota_remaining": 9861
    # }