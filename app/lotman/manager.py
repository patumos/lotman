import copy
from datetime import datetime
from abc import ABC, abstractmethod


class RootManager:
    def __init__(self, templateClass):
        self.items = []
        self.templateClass = templateClass
        self.loginManger = None
        self.logManager = None
        self.roles = []

        self.loginActions = []
        self.logActions = []



    def checkLoginAndRoles(self):
        self.loginManager.loginRequired()
        if self.roles == []:
            return True

        for r0 in  self.loginManager.currentUser.roles:
            if r0 in self.roles:
                return True

        raise Exception("Role required not enough")

    def filterActions(self, name):
        if name in self.loginActions:
            self.checkLoginAndRoles()

        if name in self.logActions:
            self.logManager.log(self.loginManager.currentUser.email, name)

    def search(self, **kwargs):

        self.filterActions("search")


    def create(self, **kwargs):
        self.filterActions("create")

        temp = self.templateClass(**kwargs)
        self.items.append(temp)
        return temp

    def delete(self, query):
        self.filterActions("delete")

        rs = self.search(**query)
        for r in rs:
            self.items.remove(r)

    def update(self, query, updateData):
        self.filterActions("update")

        rs = self.search(**query)
        for r in rs:
            for k,v in updateData.items():
                setattr(r, k, v)
        return rs

    def clone(self,src):
        self.filterActions("close")
        return copy.deepcopy(src)

    def list(self):
        self.filterActions("list")
        return self.items


class Manager(ABC):
    @abstractmethod
    def create(self, **kwargs):
        pass

    @abstractmethod
    def list(self, **kwargs):
        pass

    @abstractmethod
    def delete(self, **kwargs):
        pass

    @abstractmethod
    def update(self, **kwargs):
        pass





