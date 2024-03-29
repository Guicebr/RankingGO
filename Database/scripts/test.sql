insert into users(nick,tgid,lang) values("Wicisian",13922907,"es");
insert into users(nick,tgid,lang) values("Bugimaemper0r",1441409608,"es");
insert into users(nick,tgid,lang) values("PabloLuis94",525153728,"es");


SELECT r.personid, u.nick, u.tgid, r.amount
FROM ((ranking r
INNER JOIN (
    SELECT personid, type, MAX(dcreate) max_dcreate
    FROM ranking
    WHERE type = 1
    GROUP BY personid
) AS t
ON r.dcreate = t.max_dcreate
AND r.personid = t.personid)
INNER JOIN (
    SELECT id, nick, tgid
    FROM users
    group by id
) AS u
ON u.id = r.personid)
ORDER BY r.amount DESC
LIMIT 100;

from Database import dbhelper
dbconn = dbhelper.DBHelper()
print(str(dbconn.get_ranking(1, 100)))

DELIMITER $$
CREATE TRIGGER 'checkValueIncrement'
BEFORE INSERT ON 'ranking'
FOR EACH ROW
BEGIN
  DECLARE maxvalue INT;
  SELECT MAX(amount)
         FROM ranking,
         WHERE NEW.type = OLD.type AND NEW.personid = OLD.personid
         INTO maxvalue;
  IF maxvalue >= NEW.value:
  THEN
  END IF;
END$$

DELIMITER ;

SELECT MAX(amount)
         FROM ranking
         WHERE type = 1 AND personid = 1;

-1001329014844 Prueba Grupo Bot

from Database import dbhelper
dbconn = dbhelper.DBHelper()
dbconn.add_group("Prueba Grupo Bot", -1001329014844)


