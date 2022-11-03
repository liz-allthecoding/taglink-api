CREATE USER 'apiservice_user'@'localhost' IDENTIFIED BY 'PASSWORD'; -- Replace PASSWORD with a suitable password
CREATE DATABASE IF NOT EXISTS apiservice;
GRANT SELECT, INSERT, UPDATE, DELETE ON apiservice.* TO apiservice_user@'localhost';
USE apiservice;
CREATE TABLE IF NOT EXISTS link (link_id CHAR(36) NOT NULL, link TEXT, PRIMARY KEY (link_id));
CREATE TABLE IF NOT EXISTS tag (tag_id CHAR(36) NOT NULL, tag VARCHAR(255), PRIMARY KEY (tag_id), INDEX (tag));
CREATE TABLE IF NOT EXISTS taglink (tag_id CHAR(36), link_id CHAR(36), CONSTRAINT FOREIGN KEY (tag_id) REFERENCES tag (tag_id), CONSTRAINT FOREIGN KEY (link_id) REFERENCES link (link_id), PRIMARY KEY (tag_id, link_id), INDEX (tag_id), INDEX (link_id));
CREATE TABLE IF NOT EXISTS user (user_id CHAR(36) NOT NULL DEFAULT UUID(), username VARCHAR(255), hashed_password VARCHAR(255), PRIMARY KEY (user_id), INDEX (username));
INSERT INTO user SET username='apiuser', hashed_password='HASHED_PASSWORD'; -- Replace HASHED_PASSWORD with the output of hash_password.py
CREATE TABLE IF NOT EXISTS account (account_id CHAR(36) NOT NULL, email VARCHAR(255), hashed_password VARCHAR(255), created DATETIME DEFAULT UTC_TIMESTAMP(), PRIMARY KEY (account_id), UNIQUE KEY (email));
ALTER TABLE taglink ADD COLUMN IF NOT EXISTS account_id CHAR(36) NOT NULL AFTER link_id;
ALTER TABLE taglink ADD INDEX(account_id, tag_id);
ALTER TABLE taglink ADD INDEX(account_id, link_id);
ALTER TABLE taglink ADD CONSTRAINT FOREIGN KEY (account_id) REFERENCES account (account_id);
ALTER TABLE link ADD COLUMN IF NOT EXISTS account_id CHAR(36) NOT NULL AFTER link_id;
ALTER TABLE link ADD INDEX(account_id);
ALTER TABLE link ADD CONSTRAINT FOREIGN KEY (account_id) REFERENCES account (account_id);
ALTER TABLE tag ADD COLUMN IF NOT EXISTS account_id CHAR(36) NOT NULL AFTER tag_id;
ALTER TABLE tag ADD UNIQUE KEY (account_id, tag);
ALTER TABLE tag ADD CONSTRAINT FOREIGN KEY (account_id) REFERENCES account (account_id);
INSERT INTO user SET user_id=UUID(), username='integration_test_user', hashed_password='INTEGRATION_TEST_USER_HASHED_PASSWORD';
