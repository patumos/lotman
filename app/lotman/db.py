from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import sys
import gridfs


class DBConfig:
    dbName = "ministock"
    dbHost = "db"
    dbPort = 27017

class MongoConnector:

    client = MongoClient(DBConfig.dbHost, DBConfig.dbPort)
    db = client[DBConfig.dbName]
    pageSize = 50
    fs = gridfs.GridFS(db)


    @classmethod
    def putFile(cls,filename, content, messageId, profile, isProcess):
        cls.fs.put(content, filename=filename, messageId=messageId, profile=profile, isProcess=isProcess)

    @classmethod
    def getFile(cls, messageId):
        return cls.fs.get_last_version(filename=messageId)

    @classmethod
    def find(cls, query={}, sortOptions=None, page=1):
        if sortOptions == None:
            cursor = cls.db[cls.__name__].find(query)
        else:
            cursor = cls.db[cls.__name__].find(query).sort(sortOptions) \
                .skip(cls.pageSize * (page - 1)).limit(cls.pageSize)

        for o in cursor:
            c = cls()
            for k,v in o.items():
                setattr(c, k, v)

            c.id = o['_id']
            yield c

    @classmethod
    def findOne(cls, query={}, sortOptions=None):
        #print("findOne")
        #print(query)
        obj  = cls.db[cls.__name__].find_one(query)

        if obj is None:
            return None

        c = cls()
        for k,v in obj.items():
            setattr(c, k, v)

        c.id = obj['_id']
        return c


    @classmethod
    def findById(cls, oid):
        r = cls.db[cls.__name__].find_one({'_id': ObjectId(oid)})

        c = cls()
        for k,v in r.items():
            setattr(c, k, v)

        c.id = r['_id']
        return c

    @classmethod
    def deleteAll(cls, query={}):
        return cls.db[cls.__name__].delete_many(query)

    def __init__(self):
        #self.fields = fields
        self.id = None
        #self.tblName = self.__class__.tblName()
        #print(self.tblName)
        self.tbl = self.__class__.db[self.__class__.__name__]
        self.created_at = datetime.utcnow()

    def commit(self):
        obj = dict((name, getattr(self, name)) for name in self.fields)
        if self.id == None:
            #insert to db
            self.id  = self.tbl.insert_one(obj).inserted_id
            return self
        else:
            #update
            self.tbl.update_one({'_id': self.id},{'$set':  obj}, upsert=True)
            return self

        for f in self.fields:
            print(getattr(self, f))

    def to_dict(self):
        print(self.id, file=sys.stderr)
        fields = self.fields
        obj = dict((name, getattr(self, name)) for name in fields)
        obj['id'] = str(self.id)
        return obj

    def delete(self):
        return self.tbl.delete_one({"_id": self.id})

class SampleModel(MongoConnector):
    def __init__(self):
        #self.tblName = self.__class__.__name__
        self.fields = ['name', 'age', 'created_at']
        self.name = "Tum"
        self.age = 24
        MongoConnector.__init__(self)

class User(MongoConnector):
    def __init__(self, name="", age=10, department=""):
        #self.tblName = self.__class__.__name__
        self.fields = ['name', 'age', 'department', 'created_at']
        self.name = name
        self.age = age
        self.department = department
        MongoConnector.__init__(self)


if __name__ == "__main__":
    c = SampleModel()
    c.name = "mm"
    c.age = 33
    c.commit()
    c.age = 24
    c.commit()
    print(c.id)


    print("list")
    print(list(SampleModel.find({'name': 'mm'})))

    print("mm")
    for i in SampleModel.find({'name': 'mm'},[("created_at", -1)]):
        print(i.created_at)
        i.delete()


    #print(dir(SampleModel.deleteAll()))


    '''
    s0 = SampleModel.findById('61cff4c9b519dbfdbe946a71')
    print(vars(s0))
    s0.age = 99
    s0.commit()

    s0 = SampleModel.findById('61cff4c9b519dbfdbe946a71')
    assert s0.age == 99
    '''

    User.deleteAll()
    u = User("tum", "27", "software engineering")
    u.commit()

    assert len(list(User.find({'department': "software engineering"}))) == 1


