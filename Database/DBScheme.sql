CREATE DATABASE RankingPOGO;
USE RankingPOGO;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS telegroups;
DROP TABLE IF EXISTS group_user;
DROP TABLE IF EXISTS tranking;
DROP TABLE IF EXISTS ranking;
DROP VIEW IF EXISTS rankingview;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE users (
     id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
     nick VARCHAR(255) NOT NULL,
     tgid INTEGER NOT NULL UNIQUE,
     lang VARCHAR(10)
);
CREATE INDEX idx_tgid ON users(tgid);

CREATE TABLE telegroups (
     id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
     tgid BIGINT NOT NULL UNIQUE,
     lang VARCHAR(10),
     name VARCHAR(255)
);

CREATE INDEX idx_tgid ON telegroups(tgid);

CREATE TABLE group_user (
    groupid INTEGER NOT NULL,
    usertgid INTEGER NOT NULL,
    CONSTRAINT PK_group PRIMARY KEY (groupid, usertgid),
    CONSTRAINT FK_groupid FOREIGN KEY (groupid) REFERENCES telegroups(id)
);


CREATE TABLE tranking (
     id INTEGER NOT NULL PRIMARY KEY,
     name varchar(255),
     description varchar(255)
);

CREATE TABLE ranking (
     personid INTEGER,
     type INTEGER,
     dcreate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     amount INTEGER,
     PRIMARY KEY (personid,type,dcreate),
     CONSTRAINT FK_personid FOREIGN KEY (personid) REFERENCES users(id),
     CONSTRAINT FK_type FOREIGN KEY (type) REFERENCES tranking(id)
);
CREATE INDEX idx_type ON ranking(type);

CREATE VIEW rankingview AS
SELECT u.nick, t.name as type, r.amount, r.dcreate
FROM ranking r, users u, tranking t
WHERE r.personid = u.id AND r.type = t.id;
SELECT * FROM rankingview;

insert into tranking(id,name,description) values (1,"totalxp","Total Experience");
insert into tranking(id,name,description) values (2,"collector","Pokémon Caught");
insert into tranking(id,name,description) values (3,"jogger","Distance Walked");
insert into tranking(id,name,description) values (4,"backpacker","PokéStops Visited");
insert into tranking(id,name,description) values (5,"breeder","Eggs Hatched");
insert into tranking(id,name,description) values (6,"battlegirl","Gym Battles Won");
insert into tranking(id,name,description) values (7,"gymleader","Gym Defenders Hours");
insert into tranking(id,name,description) values (8,"pokemon_ranger","Field Research Task Completed");
insert into tranking(id,name,description) values (9,"scientist","Pokémon Evolved");
insert into tranking(id,name,description) values (10,"fisher","Big Magikarp Caught");
insert into tranking(id,name,description) values (11,"youngster","Tiny Ratata Caught");
insert into tranking(id,name,description) values (12,"pikachu_fan","Pikachu Caught");
insert into tranking(id,name,description) values (13,"berry_master","Berries at Gyms");
insert into tranking(id,name,description) values (14,"idol","Best Friends");
insert into tranking(id,name,description) values (15,"gentleman","Pokémon Traded");
insert into tranking(id,name,description) values (16,"ace_trainer","Trains");
insert into tranking(id,name,description) values (17,"champion","Raids Won");
insert into tranking(id,name,description) values (18,"battle_legend","Legendary Raids Won");
insert into tranking(id,name,description) values (19,"pilot","Distance of all Pokémon Trades");
insert into tranking(id,name,description) values (20,"great_league_veteran","Great League Battles Won");
insert into tranking(id,name,description) values (21,"master_league_veteran","Master League Battles Won");
insert into tranking(id,name,description) values (22,"cameraman","Surprise Encounters Snapshot");
insert into tranking(id,name,description) values (23,"purifier","Shadow Pokémon Purified");
insert into tranking(id,name,description) values (24,"hero","Team GO Rocket Members Defeated");
insert into tranking(id,name,description) values (25,"ultra_hero","Team GO Rocket Boss Defeated");
insert into tranking(id,name,description) values (26,"ultra_league_veteran","Ultra League Battles Won");
insert into tranking(id,name,description) values (27,"best_buddy","Best Buddies");
insert into tranking(id,name,description) values (28,"wayfarer","Wayfarer Agreements");
insert into tranking(id,name,description) values (29,"successor","Mega Evolved Pokémon");
insert into tranking(id,name,description) values (30,"sightseer","PokéStops Unique Visited");

insert into users(nick,tgid,lang) values("Wicisian",13922907,"es");
insert into users(nick,tgid,lang) values("Bugimaemper0r",1441409608,"es");
