import time
import unittest

from scrapy import cmdline
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from scrapy.utils.spider import iter_spider_classes
from scrapy_spider.common.log import log
from scrapy_spider.spiders.proxy.spiders import regex_proxy_spider
from twisted.internet import reactor, defer


class TestDouyinSpider(unittest.TestCase):
    """抖音爬虫"""

    def test_run_spider_to_json(self):
        spider = "douyin"
        args = "-o items.json"
        cmd = "scrapy crawl %s %s" % (spider, args)
        cmdline.execute(cmd.split())

    def test_run_spider(self):
        """运行抖音爬虫"""
        spider = "douyin"
        args = "--set SPIDER_MODULES=scrapy_spider.spiders.douyin"
        cmd = "scrapy crawl %s %s" % (spider, args)
        cmdline.execute(cmd.split())


class TestProxySpider(unittest.TestCase):
    """爬取代理的爬虫"""

    def test_xicidaili_spider(self):
        self.test_proxy_spider('xicidaili')

    def test_data5u_spider(self):
        self.test_proxy_spider('data5u')

    def test_goubanjia_spider(self):
        self.test_proxy_spider('goubanjia')

    def test_coderbusy_spider(self):
        self.test_proxy_spider('coderbusy')

    def test_ip3366_spider(self):
        self.test_proxy_spider('ip3366')

    def test_66ip_spider(self):
        self.test_proxy_spider('66ip')

    # 以下已不可用
    def test_kuaidaili_spider(self):
        self.test_proxy_spider('kuaidaili')

    def test_jiangxianli_spider(self):
        self.test_proxy_spider('jiangxianli')

    def test_iphai_spider(self):
        self.test_proxy_spider('iphai')

    def test_89ip_spider(self):
        self.test_proxy_spider('89ip')

    def test_swei360_spider(self):
        self.test_proxy_spider('swei360')

    # 测试方法
    def test_proxy_spider(self, spider):
        """运行代理爬虫"""
        args = "--set SPIDER_MODULES=scrapy_spider.spiders.proxy.spiders"
        cmd = "scrapy crawl %s %s" % (spider, args)
        cmdline.execute(cmd.split())


class TestAllProxySpider(unittest.TestCase):
    """所有的代理爬虫"""

    @defer.inlineCallbacks
    def crawl(self, runner):
        # 遍历取出 spider
        spider_list = []
        for spider_class in iter_spider_classes(regex_proxy_spider):
            ip_count = getattr(spider_class, 'ip_count', 0)
            if ip_count > 0:
                spider_list.append(spider_class)
        times = 0
        # 无限循环
        while times >= 0:
            times += 1
            for i in range(len(spider_list)):
                spider = spider_list[i]
                log.info(f'第 {times} 轮,第 {i+1}/{len(spider_list)} 个爬虫 {spider.name} 开始爬取')
                try:
                    yield runner.crawl(spider)
                except SystemExit:
                    log.info(f'第 {times} 轮,第 {i+1}/{len(spider_list)} 个爬虫 {spider.name} 爬取结束')
                sleep_time = 10
                log.info(f'等待执行下一爬虫,sleep {sleep_time}')
                time.sleep(sleep_time)
            # 延时下一轮
            sleep_time = 600
            log.info(f'等待下一轮,sleep {sleep_time}')
            time.sleep(sleep_time)
        reactor.stop()

    def test_proxy_spider_list(self):
        """多个代理爬虫"""
        configure_logging()
        runner = CrawlerRunner(get_project_settings())
        self.crawl(runner)
        reactor.run()