""" Ratpy Settings module """

# You can pass a specific setting using comand line : -s SETTING_NAME="setting_value"

import os
# import datetime  # pylint: disable=unused-import

# ############################################################### #
# ############################################################### #

BOT_NAME = 'ratpy-test'

# RESOURCES
RESOURCES_DIR = './resources/'

# WORK
WORK_DIR = './work/'

# LOGS
LOG_ENABLED = True
LOG_LEVEL = 'INFO'
LOG_DIR = './logs/'
LOG_FILE = None
# LOG_FILE = LOG_DIR + '%s-%s.logs' % (BOT_NAME, datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f'))
LOG_ENCODING = 'utf-8'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FORMAT = '%(asctime)s  %(levelname)9s | %(name)-55s %(message)s'
LOG_FORMATTER = 'scrapy.logformatter.LogFormatter'
LOG_IN_FILES = True
LOG_LEVEL_IN_FILES = 'INFO'
LOG_IN_ONE_FILE = True
LOG_LEVEL_IN_ONE_FILE = 'INFO'
LOG_SHORT_NAMES = False
LOG_STDOUT = False

# ############################################################### #
# ############################################################### #

# COMMANDS
COMMANDS_MODULE = 'ratpy.commands'
EDITOR = 'atom'
BROWSER = 'google-chrome'

NEW_SPIDER_MODULE = ''
TEMPLATES_DIR = './ratpy/utils/resources/templates'

# TEST SERVER
TEST_SERVER_URL = 'http://localhost:8998'
TEST_SERVER_NB_PAGES = 1000
TEST_SERVER_NB_PAGE_LINKS = 50

# DOWNLOADER
CONCURRENT_ITEMS = 100

CONCURRENT_REQUESTS = 32
CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 0

DOWNLOADER = 'scrapy.core.downloader.Downloader'

DOWNLOAD_DELAY = 0

DOWNLOAD_HANDLERS = {}
DOWNLOAD_HANDLERS_BASE = {
    'data': 'scrapy.core.downloader.handlers.datauri.DataURIDownloadHandler',
    'file': 'scrapy.core.downloader.handlers.file.FileDownloadHandler',
    'http': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
    'https': 'scrapy.core.downloader.handlers.http.HTTPDownloadHandler',
    'ftp': 'scrapy.core.downloader.handlers.ftp.FTPDownloadHandler',
    's3': None
}

DOWNLOAD_MAXSIZE = 1024 * 1024 * 1024
DOWNLOAD_WARNSIZE = 32 * 1024 * 1024
DOWNLOAD_FAIL_ON_DATALOSS = True

DOWNLOADER_HTTPCLIENTFACTORY = 'scrapy.core.downloader.webclient.ScrapyHTTPClientFactory'
DOWNLOADER_CLIENTCONTEXTFACTORY = 'scrapy.core.downloader.contextfactory.ScrapyClientContextFactory'
DOWNLOADER_CLIENT_TLS_CIPHERS = 'DEFAULT'
DOWNLOADER_CLIENT_TLS_METHOD = 'TLS'
DOWNLOADER_CLIENT_TLS_VERBOSE_LOGGING = False

FTP_USER = 'anonymous'
FTP_PASSWORD = 'guest'
FTP_PASSIVE_MODE = True

RANDOMIZE_DOWNLOAD_DELAY = True

SCRAPER_SLOT_MAX_ACTIVE_SIZE = 5000000

# LOADER
SPIDER_LOADER_CLASS = 'scrapy.spiderloader.SpiderLoader'
SPIDER_LOADER_WARN_ONLY = False
SPIDER_MODULES = ['projects']

# MAILER
MAIL_HOST = 'localhost'
MAIL_PORT = 25
MAIL_FROM = 'scrapy@localhost'
MAIL_PASS = None
MAIL_USER = None

# PIPELINE
ITEM_PIPELINES = {
    'ratpy.config.pipelines.RatpyItemPipeline': 94
    }
ITEM_PIPELINES_BASE = {}
ITEM_PROCESSOR = 'scrapy.pipelines.ItemPipelineManager'
FEED_STORAGE_FTP_ACTIVE = False
FEED_STORAGE_S3_ACL = ''
FILES_STORE_S3_ACL = 'private'
FILES_STORE_GCS_ACL = ''
IMAGES_STORE_S3_ACL = 'private'
IMAGES_STORE_GCS_ACL = ''

# RESOLVER
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000
DNS_RESOLVER = 'scrapy.resolver.CachingThreadedResolver'
DNS_TIMEOUT = 60

# SCHEDULER
SCHEDULER = 'ratpy.config.scheduler.RatpyScheduler'
SCHEDULER_DISK_QUEUE = 'ratpy.config.scheduler.queues.PickleDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'ratpy.config.scheduler.queues.PickleMemoryQueue'
SCHEDULER_PRIORITY_QUEUE = 'ratpy.config.scheduler.queues.RatpyPriorityQueue'
DUPEFILTER_CLASS = 'ratpy.config.scheduler.dupefilter.RatpyDupefilter'

# SHELL
DEFAULT_ITEM_CLASS = 'scrapy.item.Item'

# STATS
STATS_CLASS = 'ratpy.config.stats.StatsCollector'
STATS_DUMP = True
STATS_STORE = True

# ############################################################### #
# ############################################################### #

# DOWNLOADER MIDDLEWARES
DOWNLOADER_MIDDLEWARES = {
    'ratpy.config.middlewares.RatpyDownloaderMiddleware': 94
    }
DOWNLOADER_MIDDLEWARES_BASE = {
    # Engine side
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 560,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
    # Downloader side
}

# AJAX CRAWL
AJAXCRAWL_ENABLED = False
# COOKIES
COOKIES_ENABLED = False
COOKIES_DEBUG = False
# DEFAULT HEADERS
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'application/json,text/html;q=0.75',
    'Accept-Language': 'fr,en;q=0.75,*;q=0.5'
    }
# HTTP CACHE
HTTPCACHE_ENABLED = False
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_MISSING = False
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPCACHE_EXPIRATION_SECS = 0
HTTPCACHE_ALWAYS_STORE = False
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_IGNORE_SCHEMES = ['file']
HTTPCACHE_IGNORE_RESPONSE_CACHE_CONTROLS = []
HTTPCACHE_DBM_MODULE = 'dbm'
HTTPCACHE_POLICY = 'scrapy.extensions.httpcache.DummyPolicy'
HTTPCACHE_GZIP = False
# HTTP COMPRESSION
COMPRESSION_ENABLED = True
# HTTP PROXY
HTTPPROXY_ENABLED = True
HTTPPROXY_AUTH_ENCODING = 'latin-1'
# REDIRECT
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 10
REDIRECT_PRIORITY_ADJUST = +5
METAREFRESH_ENABLED = True
METAREFRESH_IGNORE_TAGS = []
METAREFRESH_MAXDELAY = 100
# RETRY
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]
RETRY_PRIORITY_ADJUST = -1
# ROBOT.TXT
ROBOTSTXT_OBEY = False
ROBOTSTXT_PARSER = 'scrapy.robotstxt.ProtegoRobotParser'
ROBOTSTXT_USER_AGENT = None
# STATS
DOWNLOADER_STATS = True
# USER AGENT
USER_AGENT = 'ratpy-project'
# TIMEMOUT
DOWNLOAD_TIMEOUT = 180

# ############################################################### #
# ############################################################### #

# SPIDER MIDDLEWARES
SPIDER_MIDDLEWARES = {
    'ratpy.config.middlewares.RatpySpiderMiddleware': 94
    }
SPIDER_MIDDLEWARES_BASE = {
    # Engine side
    'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 100,
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 500,
    'scrapy.spidermiddlewares.referer.RefererMiddleware': 700,
    'scrapy.spidermiddlewares.urllength.UrlLengthMiddleware': 800,
    'scrapy.spidermiddlewares.depth.DepthMiddleware': 900,
    # Spider side
}

# DEPTH
DEPTH_LIMIT = 0
DEPTH_STATS_VERBOSE = False
DEPTH_PRIORITY = 0
# REFERER
REFERER_ENABLED = False
REFERRER_POLICY = 'scrapy.spidermiddlewares.referer.DefaultReferrerPolicy'
# URL LENGTH
URLLENGTH_LIMIT = 2083

# ############################################################### #
# ############################################################### #

# EXTENSIONS
EXTENSIONS = {}
EXTENSIONS_BASE = {
    'ratpy.config.extensions.corestats.CoreStats': 1,
    'ratpy.config.extensions.logstats.LogStats': 2,
    'ratpy.config.extensions.spiderstate.SpiderState': 3,
    'ratpy.config.extensions.memusage.MemoryUsage': 4
}
# CORE STATS
CORE_STATS_ENABLED = True
# LOG STATS
LOG_STATS_ENABLED = True
LOG_STATS_INTERVAL = 10.0
# MEMORY USAGE
MEMORY_USAGE_ENABLED = True
MEMORY_USAGE_WARNING_MB = 0
MEMORY_USAGE_LIMIT_MB = 0
MEMORY_USAGE_CHECK_INTERVAL_SECONDS = 30.0
MEMORY_USAGE_NOTIFY_MAIL = ['raphael.manger+ratpy@gmail.com']
# SPIDER STATE
SPIDER_STATE_ENABLED = True

# ############################################################### #

# AUTO THROTTLE
AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_DEBUG = False
AUTOTHROTTLE_MAX_DELAY = 15.0
AUTOTHROTTLE_START_DELAY = 5.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# CLOSE SPIDER
CLOSESPIDER_TIMEOUT = 0
CLOSESPIDER_PAGECOUNT = 0
CLOSESPIDER_ITEMCOUNT = 0
CLOSESPIDER_ERRORCOUNT = 0
# FEED EXPORT
FEED_TEMPDIR = None
FEEDS = {}
FEED_URI_PARAMS = None  # a function to extend uri arguments
FEED_STORE_EMPTY = False
FEED_EXPORT_ENCODING = None
FEED_EXPORT_FIELDS = None
FEED_STORAGES = {}
FEED_STORAGES_BASE = {
    '': 'scrapy.extensions.feedexport.FileFeedStorage',
    'file': 'scrapy.extensions.feedexport.FileFeedStorage',
    'stdout': 'scrapy.extensions.feedexport.StdoutFeedStorage',
    's3': None,
    'ftp': 'scrapy.extensions.feedexport.FTPFeedStorage',
}
FEED_EXPORTERS = {}
FEED_EXPORTERS_BASE = {
    'json': 'scrapy.exporters.JsonItemExporter',
    'jsonlines': 'scrapy.exporters.JsonLinesItemExporter',
    'jl': 'scrapy.exporters.JsonLinesItemExporter',
    'csv': 'scrapy.exporters.CsvItemExporter',
    'xml': 'scrapy.exporters.XmlItemExporter',
    'marshal': 'scrapy.exporters.MarshalItemExporter',
    'pickle': 'scrapy.exporters.PickleItemExporter',
}
FEED_EXPORT_INDENT = 0
# MEMORY DEBUG
MEMDEBUG_ENABLED = False
MEMDEBUG_NOTIFY = []
# TELNET
TELNETCONSOLE_ENABLED = False
TELNETCONSOLE_PORT = [6023, 6073]
TELNETCONSOLE_HOST = '127.0.0.1'
TELNETCONSOLE_USERNAME = 'ratpy'
TELNETCONSOLE_PASSWORD = None

# ############################################################### #
# ############################################################### #
