import yaml

with open('mydb') as f:
    old_db = yaml.load(f, Loader=yaml.FullLoader)

with open('zh_db') as f:
    zh_db = yaml.load(f, Loader=yaml.FullLoader)

with open('en_db') as f:
    en_db = yaml.load(f, Loader=yaml.FullLoader)

for usr in old_db:
	value = old_db[usr].get(4)
	if value:
		zh_db[usr] = zh_db.get(usr, {})
		zh_db[usr]['key'] = value
		en_db[usr] = en_db.get(usr, {})
		en_db[usr]['key'] = value

with open('zh_db', 'w') as f:
	f.write(yaml.dump(zh_db, sort_keys=True, indent=2, allow_unicode=True))

with open('en_db', 'w') as f:
	f.write(yaml.dump(en_db, sort_keys=True, indent=2, allow_unicode=True))