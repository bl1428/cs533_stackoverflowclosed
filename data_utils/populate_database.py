# reference:https://mikemadisonweb.github.io/2017/01/08/import-xml-into-sql/
import datetime
from lxml import etree
import psycopg2
import psycopg2.extras
import config
import os
import psutil
import logging

logging.basicConfig(format='[%(asctime)s %(levelname)-8s] %(message)s', level=logging.DEBUG, handlers=[logging.FileHandler('populate_database.log',mode='w'), logging.StreamHandler()])

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def import_xml(filename, connect, insert_command, db_table_columns, batch = [], batch_size = 100000):
    count = 0
    batch = []
    cursor = connect.cursor()
    process = psutil.Process(os.getpid())
    for event, element in etree.iterparse(filename, events=('end',), tag='row'):
        count += 1
        row = [element.get(n) for n in db_table_columns]
        batch.append(row)
        # Free memory
        element.clear()
        if element.getprevious() is not None:
            del(element.getparent()[0])
        # Save batch to DB
        if count % batch_size == 0:
            psycopg2.extras.execute_values(cursor, insert_command, batch)
            logging.info("From: {} | Imported rows: {} | Memory usage: {}".format(filename, count, sizeof_fmt(process.memory_info().rss)))
            batch = []
    # Save the rest
    if len(batch):
        psycopg2.extras.execute_values(cursor, insert_command, batch)


def import_dump(db_name = config.DB_NAME, db_host = config.DB_HOST, db_user = config.DB_USER, db_pass = config.DB_PASS, db_table = 'Posts'):
    filename = './datasets/'+db_table+'.xml'
    start_date = datetime.datetime.now()
    db_table_columns = []
    insert_command = []
    logging.info("Import data from {}".format(filename))
    connect = psycopg2.connect(database=db_name, user=db_user, host=db_host, password=db_pass)
    connect.autocommit = True
    cursor = connect.cursor()

    # Insert Command for different tables
    if db_table == 'Users':
        db_table_columns = ['Id', 'Reputation', 'CreationDate', 'DisplayName', 'LastAccessDate', 'WebsiteUrl',
                            'Location', 'AboutMe', 'Views', 'UpVotes', 'DownVotes', 'ProfileImageUrl', 'AccountId']
        insert_command = 'INSERT INTO {} (Id, Reputation, CreationDate, DisplayName, LastAccessDate, WebsiteUrl, Location, AboutMe, Views, UpVotes, DownVotes, ProfileImageUrl, AccountId) VALUES %s'.format(
            db_table)

    elif db_table == 'Posts':
        db_table_columns = ['Id', 'PostTypeId', 'ParentId', 'AcceptedAnswerId', 'CreationDate', 'Score', 'ViewCount',
                            'Body', 'OwnerUserId', 'OwnerDisplayName', 'LastEditorUserId', 'LastEditorDisplayName',
                            'LastEditDate', 'LastActivityDate', 'Title', 'Tags', 'AnswerCount', 'CommentCount',
                            'FavoriteCount', 'ClosedDate', 'CommunityOwnedDate', 'ContentLicense']
        insert_command = 'INSERT INTO {} (Id, PostTypeId, ParentId, AcceptedAnswerId, CreationDate, Score, ViewCount, Body, OwnerUserId, OwnerDisplayName, LastEditorUserId, LastEditorDisplayName, LastEditDate, LastActivityDate, Title, Tags, AnswerCount, CommentCount, FavoriteCount, ClosedDate, CommunityOwnedDate, ContentLicense) VALUES %s'.format(
            db_table)

    elif db_table == 'PostHistory':
        db_table_columns = ['Id', 'PostHistoryTypeId', 'PostId', 'RevisionGUID', 'CreationDate', 'UserId',
                            'UserDisplayName', 'Comment', 'Text', 'ContentLicense']
        insert_command = 'INSERT INTO {} (Id, PostHistoryTypeId, PostId, RevisionGUID, CreationDate, UserId, UserDisplayName, Comment, Text, ContentLicense) VALUES %s'.format(
            db_table)

    elif db_table == 'PostLinks':
        db_table_columns = ['Id', 'CreationDate', 'PostId', 'RelatedPostId', 'LinkTypeId']
        insert_command = 'INSERT INTO {} (Id, CreationDate, PostId, RelatedPostId, LinkTypeId) VALUES %s'.format(
            db_table)

    elif db_table == 'Comments':
        db_table_columns = ['Id', 'PostId', 'Score', 'Text', 'CreationDate', 'UserDisplayName', 'UserId',
                            'ContentLicense']
        insert_command = 'INSERT INTO {} (Id, PostId, Score, Text, CreationDate, UserDisplayName, UserId, ContentLicense) VALUES %s'.format(
            db_table)

    elif db_table == 'Tags':
        db_table_columns = ['Id', 'TagName', 'Count', 'ExcerptPostId', 'WikiPostId']
        insert_command = 'INSERT INTO {} (Id, TagName, Count, ExcerptPostId, WikiPostId) VALUES %s'.format(
            db_table)

    import_xml(filename, connect, insert_command, db_table_columns)

    # Add foreign key for Posts
    # if db_table == 'Posts':
        # cursor.execute('ALTER TABLE Posts ADD CONSTRAINT fk_Posts_AcceptedAnswer FOREIGN KEY (AcceptedAnswerId) REFERENCES Posts (Id)')
        # cursor.execute('ALTER TABLE Posts ADD CONSTRAINT fk_Posts_Parent FOREIGN KEY (ParentId) REFERENCES Posts (Id)')
        # cursor.execute('ALTER TABLE Posts ADD CONSTRAINT fk_Posts_OwnerUsers FOREIGN KEY (OwnerUserId) REFERENCES Users (Id)')
        # cursor.execute('ALTER TABLE Posts ADD CONSTRAINT fk_Posts_LastEditorUsers FOREIGN KEY (LastEditorUserId) REFERENCES Users (Id)')
        # connect.commit()
    connect.close()

    end_date = datetime.datetime.now()
    seconds = (end_date - start_date).total_seconds()
    logging.info("Executed in {}s".format(seconds))


if __name__ == '__main__':

    # overall disk usage: 162 GB
    # To query disk usage: SELECT pg_size_pretty(pg_database_size('postgres'));
    import_dump(db_table='Users') # takes about 8.65 mins for 14,080,580 rows
    import_dump(db_table='Posts') # takes about 75 mins for 52,166,063 rows
    import_dump(db_table='PostHistory') # takes about 2 hrs 16 mins for 138,808,451 rows (query for 13m13s)
    import_dump(db_table='PostLinks') # takes about 2.5 mins for 7,302,589 rows
    import_dump(db_table='Comments') # takes about 44 mins for 79,220,809 rows
    import_dump(db_table='Tags') # takes about 2 secs for 60,534 rows

