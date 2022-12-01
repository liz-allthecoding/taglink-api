SET collation_connection = 'utf8_general_ci';
USE apiservice;
ALTER TABLE taglink DROP FOREIGN KEY taglink_ibfk_1; -- tag_id
ALTER TABLE taglink DROP FOREIGN KEY taglink_ibfk_2; -- link_id
ALTER TABLE taglink DROP FOREIGN KEY taglink_ibfk_3; -- account_id

ALTER TABLE link DROP FOREIGN KEY link_ibfk_1; -- account_id
ALTER TABLE tag DROP FOREIGN KEY tag_ibfk_1; -- account_id

ALTER TABLE account CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE link CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE tag CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE taglink CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;
ALTER TABLE user CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci;

ALTER TABLE taglink ADD CONSTRAINT FOREIGN KEY (tag_id) REFERENCES tag (tag_id);
ALTER TABLE taglink ADD CONSTRAINT FOREIGN KEY (link_id) REFERENCES link (link_id);
ALTER TABLE taglink ADD CONSTRAINT FOREIGN KEY (account_id) REFERENCES account (account_id);
ALTER TABLE link ADD CONSTRAINT FOREIGN KEY (account_id) REFERENCES account (account_id);
ALTER TABLE tag ADD CONSTRAINT FOREIGN KEY (account_id) REFERENCES account (account_id);