import ConfigParser

cf = ConfigParser.SafeConfigParser()

cf.read("spider.conf")

print cf.get("db", "db_host")

cf.set("db", "db_host", "127.0.0.1")

print cf.get("db", "db_host")
