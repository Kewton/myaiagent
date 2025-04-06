from app.core.config import settings
from app.schemas.sample import StatusReq, StatusResponse
from app.core.logger import writedebuglog, writeinfolog, declogger
import uuid


class Sample1():
    def __init__(self):
        self.exeid = uuid.uuid4()
        pass

    def do(self, in_test):
        self.test = in_test
        return settings.CONFIG_TEST + "|" + self.test


class Sample2():
    def __init__(self):
        self.exeid = uuid.uuid4()
        pass

    @declogger
    def do(self, status_in: StatusReq) -> StatusResponse:
        
        writeinfolog("aaaaaa")
        writedebuglog("bbbbbb")

        my_status = {
            "receptid": status_in.user,
            "mystatus": status_in.mystatus + "||" + str(self.exeid)
        }

        if status_in.user != "b":
            self.result = True
            self.response = StatusResponse(**my_status)
        else:
            self.result = False
            self.status_code = 402
            self.detail = "エラーです"
        return
