"""
简单的示例，获取 zentao 的具体页面对应的 json 数据
1. 获取 sid
2. 注入登录态
3. 将需要的页面最后的 php/html 改为 json，添加 zentaosid 参数，获取页面数据
"""

import requests,json,re
import logging

logger = logging.getLogger(__name__)

logging.basicConfig(filename="test.log", filemode="w", 
    format="%(asctime)s %(name)s:%(levelname)s:%(message)s", datefmt="%d-%M-%Y %H:%M:%S", level=logging.DEBUG)

class Zentao_cli(object):
    session = None  # 用于实现单例类，避免多次申请sessionID
    sid = None

    def __init__(self, url, account, password, override=False):
        self.url = url
        self.account = account  # 账号
        self.password = password  # 密码
        self.session_override = override  # 是否覆盖原会话
        self.pages = {
            "sid": "/api-getsessionid.json",  # 获取sid的接口
            "login": "/user-login.json?account={0}&password={1}&zentaosid={2}",  # 登录的接口
            "get_story_list_by_account": "/index.json?zentaosid={0}",
            "extract_json": "json?zentaosid={0}"
        }
        self.s = None
        self.sid = None


    def req(self, url):
        # 请求并返回结果
        web = self.s.get(url)
        if web.status_code == 200:
            # print(web.content)            
            resp = json.loads(web.content)
            if resp.get("status") == "success":
                return True, resp
            else:
                return False, resp

    def login(self):
        if self.s is None:
            if not self.session_override and Zentao_cli.session is not None:
                self.s = Zentao_cli.session
                self.sid = Zentao_cli.sid
            else:
                # 新建会话
                self.s = requests.session()
                res, resp = self.req(self.url.rstrip("/") + self.pages["sid"])
                if res:
                    logger.info("获取sessionID成功")
                    self.sid = json.loads(resp["data"])["sessionID"]
                    Zentao_cli.sid = self.sid
                    login_res, login_resp = self.req(
                        self.url.rstrip("/") + self.pages["login"].format(self.account, self.password, self.sid))
                    if login_res:
                        logger.info("登录成功")
                        Zentao_cli.session = self.s


    def get_story_list_by_account(self):
        req_url = self.url.rstrip("/") + self.pages["get_story_list_by_account"].format(self.sid)
        web = self.s.get(req_url)
        resp = json.loads(web.content.decode())
        return resp

    def extract_json_from_html(self, url):
        req_url = url.rstrip("html") + self.pages["extract_json"].format(self.sid)
        web = self.s.get(req_url)
        resp = json.loads(web.content.decode())
        content = json.loads(resp["data"])
        return content


if __name__ == "__main__":
    cli = Zentao_cli("https://zentaobiz.demo.qucheng.cc", "demo", "quickon4You")
    cli.login()

    resp = cli.get_story_list_by_account()

    # content = json.loads(resp['data'])
    # print(json.dumps(content))

    c = cli.extract_json_from_html("https://zentaobiz.demo.qucheng.cc/task-view-12.html")
    print(json.dumps(c))