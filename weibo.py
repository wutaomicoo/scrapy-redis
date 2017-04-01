import re
import datetime
from wechat.items import WechatItem
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisSpider
import redis


r=redis.StrictRedis(host='127.0.0.1',port=6379)
r.lpush('weibo:start_urls', 'https://weibo.cn')
class WeiboSpider(RedisSpider):
    name = "weibo"
    redis_key = 'weibo:start_urls'
    # rules = (
    #     Rule(link_extractor='',callback='parse_page')
    # )
    head = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip,deflate,sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }

    login_url = 'https://passport.weibo.cn/sso/login'

    def start_requests(self):
        print(1)
        return [scrapy.Request('https://passport.weibo.cn/signin/login',meta={'cookiejar': 1}, callback=self.parse_login)]
    #若是不重写该函数，则会raise NotImplementError
    def parse(self, response):
        pass
    #登陆新浪微博手机网页版
    def parse_login(self,response):
        print ('Preparing login')
        return [scrapy.FormRequest('https://passport.weibo.cn/sso/login',
                                  headers=self.head,meta={'cookiejar': response.meta['cookiejar']},
                                  formdata={
                                      'username': 'username',
                                      'password': 'password',
                                      'savestate': '1',
                                      'r': 'http://m.weibo.cn',
                                      'pagerefer': 'http: // m.weibo.cn /',
                                      'entry': 'mweibo'
                                  },
                                  callback=self.after_login,
                                    dont_filter=True
                                    )]
    #获取cookies以后重新打开网页
    def after_login(self,response):
        Cookie = response.headers.getlist('Set-Cookie')
        print(Cookie)
        yield scrapy.FormRequest('http://weibo.cn',meta = {'cookiejar':response.meta['cookiejar']},
                            headers = self.head,
                            callback = self.parse_page
                            )
    #爬取网页相关内容
    def parse_page(self, response):
        html = response.body
        s = response.url
        a = response.xpath('//div[@class="ut"]/text()')#获取你的用户名
        print(a)
        print(s)
        print (html)
