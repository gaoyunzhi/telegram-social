import yaml

class DB(object):
    questions = ['key']
    
    def __init__(self, lan):
        self.db_loc = lan + '_db'
        with open(self.db_loc) as f:
            self.db = yaml.load(f, Loader=yaml.FullLoader)

    def save(self, usr, index, text):
        self.db[usr] = self.db.get(usr, {})
        self.db[usr][index] = text
        self._save()

    def isProfileComplete(self, usr):
        return self.getQuestionIndex(usr) == float('Inf')

    def getQuestionIndex(self, usr, ask=False):
        if not usr in self.db and not ask:
            return -1
        self.db[usr] = self.db.get(usr, {})
        for q in self.questions:
            if q not in self.db[usr]:
                return q
        return float('Inf')

    def get(self, usr):
        return self.db.get(usr, {})

    def getRaw(self, usr):
        return str(self.get(usr)) + usr

    def usrs(self):
        return [x for x in self.db.keys() if self.isProfileComplete(x)]

    def _save(self):
        with open(self.db_loc, 'w') as f:
            f.write(yaml.dump(self.db, sort_keys=True, indent=2, allow_unicode=True))
