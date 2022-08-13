class LoginManager:
    def __init__(self, um):
        self.userManager = um
        self.currentUser = None
        self.users = [{'user_id': 'tum', 'passwd': '1234'}, {'user_id': 'suthi', 'passwd': '1234'}]

    def login(self, email, passwd):
        for u in self.userManager.users:
            if u.email == email and u.passwd == passwd:
                self.currentUser = u

    def isLogin(self):
        return True if self.currentUser != None else None

    def loginRequiredDecorator(self, func):
        def wrapper():
            if self.isLogin == True:
                return func()
            else:
                raise
        return wrapper

    def loginRequired(self):
        if self.isLogin() == True:
            return True
        else:
            raise Exception("Login Required")
