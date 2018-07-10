import json

import scrapy
from scrapy_spider.common.ignore import douyin  # 不公开
from scrapy_spider.common.log import log
from scrapy_spider.spiders.douyin.items import DouyinItem


class DouyinSpider(scrapy.Spider):
    """
    参考 https://github.com/a232319779/appspider
    感谢
    """
    name = 'douyin'

    # 防 ban
    custom_settings = {
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_DELAY': 0,
        'DOWNLOAD_TIMEOUT': 10,  # 设置超时，默认是 180
        'DOWNLOADER_MIDDLEWARES': {
            # 'scrapy_spider.common.middleware.middlewares.RandomAgentDownloaderMiddleware': 300,
            'scrapy_spider.common.middleware.middlewares.DouyinRandomProxyDownloaderMiddleware': 300,
        },
        'ITEM_PIPELINES': {
            'scrapy_spider.spiders.douyin.pipelines.DouyinPostgreSQLPipeline': 300,
        },
    }
    # 好像使用 user-agent 标识，所以保持不变
    headers = {
        'user-agent': douyin.generate_default_agent(),
    }
    has_more = 1
    exit_code = 1
    total_items = 0

    def start_requests(self):
        i = 0
        while i < 1:
            # i += 1
            # 并发的时候，time 是相同的，被 scrapy 认为是相同地址而忽略
            # 后来发现要设置 dont_filter
            url = douyin.generate_feed_url()
            log.info("crawl " + url)
            yield scrapy.Request(url=url, headers=self.headers, dont_filter=True)
            if self.has_more == 0 or self.exit_code == 0:
                break

    def parse(self, response):
        try:
            result = json.loads(response.body.decode())
            status_code = result['status_code']
            if result['status_code'] == 0:
                self.has_more = result['has_more']
                aweme_list = result['aweme_list']
                self.total_items += len(aweme_list)
                log.info(f'scraped {len(aweme_list)}/{self.total_items} items')
                for aweme in aweme_list:
                    item = DouyinItem(aweme)
                    yield item
            elif status_code == 2145:
                log.warning('请求已过期')
                self.exit_code = 0
            elif status_code == 2151:
                log.warning('签名错误')
                self.exit_code = 0
            elif status_code == 2154:
                # 大约会被禁 1 个小时
                # 已经在下载器中间件拦截，应该不会走到这里的
                log.warning('请求太频繁，设备被禁')
                # log.warning('休息 10 分钟')
                # self.sleep_time = 10 * 60
                # self.exit_code = 0
            else:
                log.warning('错误码 %d' % status_code)
                log.warning(response.body.decode())
                self.exit_code = 0
        except Exception as e:
            # TODO 这里要解析代理出错，或者在中间件里处理
            log.error('出错了')
            log.error(repr(e))
