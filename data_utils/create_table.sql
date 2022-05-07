-- Please see the following link for the detail description of table:
-- https://meta.stackexchange.com/questions/2677/database-schema-documentation-for-the-public-data-dump-and-sede
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO postgres;

CREATE TABLE Users (
    Id serial PRIMARY KEY,
    Reputation INTEGER,
    CreationDate TIMESTAMP NOT NULL,
    DisplayName TEXT,
    LastAccessDate TIMESTAMP,
    WebsiteUrl TEXT,
    Location TEXT,
    AboutMe TEXT,
    Views INTEGER,
    UpVotes INTEGER,
    DownVotes INTEGER,
    ProfileImageUrl TEXT,
    AccountId INTEGER
);

CREATE TABLE Posts (
    Id serial PRIMARY KEY,
    PostTypeId INTEGER NOT NULL,
    AcceptedAnswerId INTEGER,
    ParentId INTEGER,
    CreationDate TIMESTAMP NOT NULL,
    Score NUMERIC NOT NULL,
    ViewCount INTEGER,
    Body TEXT,
    OwnerUserId INTEGER,
    OwnerDisplayName TEXT,
    LastEditorUserId INTEGER,
    LastEditorDisplayName TEXT,
    LastEditDate TIMESTAMP,
    LastActivityDate TIMESTAMP NOT NULL,
    Title TEXT,
    Tags TEXT,
    AnswerCount INTEGER,
    CommentCount INTEGER,
    FavoriteCount INTEGER,
    ClosedDate TIMESTAMP,
    CommunityOwnedDate TIMESTAMP,
    ContentLicense TEXT
--     CONSTRAINT fk_Posts_AcceptedAnswer FOREIGN KEY (AcceptedAnswerId) REFERENCES Posts (Id),
--     CONSTRAINT fk_Posts_Parent FOREIGN KEY (ParentId) REFERENCES Posts (Id),
--     CONSTRAINT fk_Posts_OwnerUsers FOREIGN KEY (OwnerUserId) REFERENCES Users (Id),
--     CONSTRAINT fk_Posts_LastEditorUsers FOREIGN KEY (LastEditorUserId) REFERENCES Users (Id)
);

CREATE TABLE PostHistory (
    Id serial PRIMARY KEY,
    PostHistoryTypeId INTEGER NOT NULL,
    PostId INTEGER NOT NULL,
    RevisionGUID TEXT,
    CreationDate TIMESTAMP NOT NULL,
    UserId INTEGER,
    UserDisplayName TEXT,
    Comment TEXT,
    Text TEXT,
    ContentLicense TEXT
--     CONSTRAINT fk_PostHistory_Posts FOREIGN KEY (PostId) REFERENCES Posts (Id) ON DELETE SET NULL
--     CONSTRAINT fk_PostHistory_Users FOREIGN KEY (UserId) REFERENCES Users (Id) ON DELETE SET NULL
);

CREATE TABLE PostLinks (
    Id serial PRIMARY KEY,
    CreationDate TIMESTAMP NOT NULL,
    PostId INTEGER NOT NULL,
    RelatedPostId INTEGER NOT NULL,
    LinkTypeId INTEGER NOT NULL
--     CONSTRAINT fk_PostLinks_Posts FOREIGN KEY (PostId) REFERENCES Posts (Id),
--     CONSTRAINT fk_PostLinks_RelatedPosts FOREIGN KEY (RelatedPostId) REFERENCES Posts (Id)
);

CREATE TABLE Comments (
    Id serial PRIMARY KEY,
    PostId INTEGER NOT NULL,
    Score INTEGER,
    Text TEXT,
    CreationDate TIMESTAMP NOT NULL,
    UserDisplayName TEXT,
    UserId INTEGER,
    ContentLicense TEXT
--     CONSTRAINT fk_Comments_Posts FOREIGN KEY (PostId) REFERENCES Posts (Id),
--     CONSTRAINT fk_Comments_Users FOREIGN KEY (UserId) REFERENCES Users (Id)
);



CREATE TABLE Tags (
    Id serial PRIMARY KEY,
    TagName TEXT,
    Count INTEGER,
    ExcerptPostId INTEGER,
    WikiPostId INTEGER
);



