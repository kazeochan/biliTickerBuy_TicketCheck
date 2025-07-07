import time
import loguru
import requests
from util.RandomUA import get_global_ua

class CheckTicketRequest:
    def __init__(
        self, proxy: str = "none"
    ):
        self.session = requests.Session()
        self.proxy_list = (
            [v.strip() for v in proxy.split(",") if len(v.strip()) != 0]
            if proxy
            else []
        )
        if len(self.proxy_list) == 0:
            raise ValueError("at least have none proxy")
        self.now_proxy_idx = 0
        self.headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5,ja;q=0.4",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": "",
            "referer": "https://show.bilibili.com/",
            "priority": "u=1, i",
            "user-agent": get_global_ua(),
        }
        self.request_count = 0  # 记录请求次数

    def switch_proxy(self):
        self.now_proxy_idx = (self.now_proxy_idx + 1) % len(self.proxy_list)
        current_proxy = self.proxy_list[self.now_proxy_idx]

        if current_proxy == "none":
            self.session.proxies = {}  # 不使用任何代理，直连
        else:
            self.session.proxies = {
                "http": current_proxy,
                "https": current_proxy,
            }

    def count_and_sleep(self, threshold=60, sleep_time=60):
        self.request_count += 1
        if self.request_count % threshold == 0:
            loguru.logger.info(f"达到 {threshold} 次请求 412，休眠 {sleep_time} 秒")
            time.sleep(sleep_time)

    def clear_request_count(self):
        self.request_count = 0

    def get(self, pid):
        url=f"https://show.bilibili.com/api/ticket/project/getV2?version=134&id={pid}&project_id={pid}"
        response = self.session.get(
            url=url,
            headers=self.headers
        )
        if response.status_code == 412:
            self.count_and_sleep()
            self.switch_proxy()
            loguru.logger.warning(
                f"412风控，切换代理到 {self.proxy_list[self.now_proxy_idx]}"
            )
            return self.get(url)
        return response
    
    def rotating_UA(self):
        self.headers["user-agent"] = get_global_ua()