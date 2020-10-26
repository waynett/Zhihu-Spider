from frame import SpyderFrame
import json

KWD = ''


class HTMLParser(SpyderFrame.HtmlParser):

    def __init__(self, get_detail):
        super().__init__()
        self.get_detail = get_detail
        if get_detail:
            self.url_manager = SpyderFrame.UrlManager(db_set_name='知乎@' + KWD)

    def parser(self, data_list: list) -> dict:
        for data in data_list:
            _type = data['type']
            if _type == 'knowledge_ad':
                yield self._knowledge_ad(data)
            elif _type == "wiki_box":
                yield self._wiki_box(data)
            elif _type == 'search_result':
                if data['object']['type'] == "answer":
                    yield self._search_result_answer(data)
                else:
                    print(data)
            elif _type == "relevant_query" or "multi_answers" or "search_club" or "video_box":
                continue
            else:
                print(data)

    def _knowledge_ad(self, data):
        self._find_new_url(data['object']['url'])
        authors = data["object"]["body"]["authors"]
        for i in range(len(authors)):
            authors[i].pop("icon")
        return {
            "type": "knowledge_ad",
            "id": data["id"],
            "title": data["object"]["body"]["title"],
            "authors": authors,
            "description": data["object"]["body"]["description"],
            # "commodity_type": data["object"]["body"]["commodity_type"],
            "footer": data["object"]["footer"],
            "url": data['object']['url']
        }

    def _search_result_answer(self, data):
        self._find_new_url("https://www.zhihu.com/question/" + data['object']['question']['url'].split('/')[-1])
        return {
            "id": data["object"]["id"],
            "q_id": data["object"]["question"]["id"],
            "type": "search_result_answer",
            "author": data["object"]["author"],
            "q_name": data["object"]["question"]["name"],
            "content": data["object"]["content"],
            "excerpt": data["object"]["excerpt"],
            "created_time": data["object"]["created_time"],
            "updated_time": data["object"]["updated_time"],
            "comment_count": data["object"]["comment_count"],
            "voteup_count": data["object"]["voteup_count"],
            "q_url": "https://www.zhihu.com/question/" + data['object']['question']['url'].split('/')[-1]
        }

    def _wiki_box(self, data):
        data = data['object']
        self._find_new_url("https://www.zhihu.com/topic/" + data['url'].split('/')[-1])
        return {
            "id": data["id"],
            "aliases": data['aliases'],
            "discussion_count": data["discussion_count"],
            "essence_feed_count": data["essence_feed_count"],
            "excerpt": data["excerpt"],
            "follower_count": data["follower_count"],
            "followers_count": data["followers_count"],
            "introduction": data["introduction"],
            "questions_count": data["questions_count"],
            "top_answer_count": data["top_answer_count"],
            "type": "wiki_box",
            "url": "https://www.zhihu.com/topic/" + data['url'].split('/')[-1]
        }

    def _find_new_url(self, url):
        if self.get_detail:
            self.url_manager.add_url(url)
        return

    def _search_result_article(self, data):
        return

    def _search_result_question(self, data):
        return


def search(keyword):
    global KWD
    KWD = keyword
    base_url = 'https://api.zhihu.com/search_v3'
    html_downloader = SpyderFrame.HtmlDownloader()
    data_saver = SpyderFrame.DataSaver(db_name='知乎', set_name=keyword)
    html_downloader.headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "cache-control": "no-cache",
        "cookie": "d_c0=\"AADWzpXyDxKPTkP_r53qvH9ipDf4dAG7XE4=|1603087870\"; "
                  "_zap=b47b3886-7c4a-4101-9ee5-4c803bcf6cd8; _xsrf=LRWrd8I0FyQr3hxZ49tYEABlJI0MFizY; "
                  "capsion_ticket=\"2|1:0|10:1603262862|14:capsion_ticket|44"
                  ":N2UxNWE4YzExZWYxNDUwYWFkZjM4MjQ4MDhjNWExNjY"
                  "=|fa44c3793ac9cf5fac96aab9dc9d8faadba2d384e00351c9c9642028ceace6ad\"; "
                  "r_cap_id=\"YmY4MWY5YzA0OWRlNDk0Yjk2MTEyYWEzZDU5MjZmMmM=|1603262864"
                  "|9dbd3b9caeccd1669c26ee92e5b543543a611713\"; "
                  "cap_id=\"OGVlYjJjOTQ2YTgyNGMzZTlmODk4NDUzMzQ0ZTkyNjA=|1603262864"
                  "|5e52e69215700dd4539d66e5a0833dd4a0c4c1fe\"; "
                  "l_cap_id=\"ODViMjY0YmExNWNlNGVmYWJmMGY5MGUyNTUzMjQxMzM=|1603262864"
                  "|8a107e67c1f9223cd88f066cda42b6ce2102b632\"; "
                  "z_c0=Mi4xQnNEUkNBQUFBQUFBQU5iT2xmSVBFaGNBQUFCaEFsVk5saWQ5WUFERVEzVUJpOVdzZHRZcnloaE9OZWVXVDZwTlhR"
                  "|1603262870|42b123d5ae8b1fb74a8815b13eae8cb34f92508c; tst=r; "
                  "q_c1=582f701a20454c59be03f2470d62b194|1603326280000|1603326280000; "
                  "Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1603653130,1603680022,1603682173,1603683176; "
                  "Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1603683176; "
                  "KLBRSID=af132c66e9ed2b57686ff5c489976b91|1603684342|1603684271",
        "pragma": "no-cache",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.51 "
    }
    prams = {
        "advert_count": "0",
        "correction": "1",
        "lc_idx": "0",
        "limit": "20",
        "offset": "0",
        "q": keyword,
        "search_hash_id": "1e3c9a021028e71019c7977637948651",
        "show_all_topics": "0",
        "t": "general",
        "vertical_info": "0,1,0,0,0,0,0,0,0,2"
    }
    html_parser = HTMLParser(get_detail=0)
    res = html_downloader.download(url=base_url, params=prams)
    while True:
        res = json.loads(res)
        for data in html_parser.parser(res['data']):
            data_saver.mongo_insert(data)
        if res['paging']['is_end']:
            break
        next_url = res['paging']['next']
        res = html_downloader.download(next_url)
    # exit
    html_downloader.proxies.__exit__()


if __name__ == '__main__':
    kwd = input("请输入搜索关键词：")
    search(kwd)