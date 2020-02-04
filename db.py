import yaml

class DB(object):
    def __init__(self):
        with open('mydb') as f:
            self.db = yaml.load(f, Loader=yaml.FullLoader)

    def save(self, usr, index, text):
        self.db[usr] = self.db.get(usr, {})
        self.db[usr][index] = text
        self._save()

    def getQuestionIndex(self, usr):
        if not user in self.db:
            return None
        i = 0
        while True:
            if i in self.db[usr]:
                i += 1
            else:
                return i

    def _save(self):
        with open('mydb', 'w') as f:
            f.write(yaml.dump(self.db, sort_keys=True, indent=2, allow_unicode=True))
