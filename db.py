import yaml
from os import path

class DB(object):
    NUM_Q = 6
    def __init__(self):
        with open('mydb') as f:
            self.db = yaml.load(f, Loader=yaml.FullLoader)

    def save(self, usr, index, text):
        self.db[usr] = self.db.get(usr, {})
        self.db[usr][index] = text
        self._save()

    def isProfileComplete(self, usr):
        return self.getQuestionIndex(usr) == NUM_Q and \
            path.exists('photo/' + usr)

    def getQuestionIndex(self, usr, ask=False):
        if not usr in self.db and not ask:
            return None
        self.db[usr] = self.db.get(usr, {})
        i = 0
        while True:
            if i in self.db[usr]:
                i += 1
            else:
                return i

    def get(self, usr):
        return self.db.get(usr, {})

    def getRaw(self, usr):
        return str(self.get(usr))

    def usrs(self):
        return [x for x in self.db.keys() if self.isProfileComplete(x)]

    def _save(self):
        with open('mydb', 'w') as f:
            f.write(yaml.dump(self.db, sort_keys=True, indent=2, allow_unicode=True))
