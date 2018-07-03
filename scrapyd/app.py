from twisted.application.service import Application
from twisted.application.internet import TimerService, TCPServer
from twisted.web import server
from twisted.python import log

from scrapy.utils.misc import load_object

from .interfaces import IEggStorage, IPoller, ISpiderScheduler, IEnvironment
from .eggstorage import FilesystemEggStorage
from .scheduler import SpiderScheduler
from .poller import QueuePoller
from .environ import Environment
from scrapyd.flaskwebsite import InitFlaskSources
from scrapyd.flaskwebsite import WSGIRootResource
from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from scrapyd.flaskwebsite import create_site
from scrapyd.flaskwebsite import scrapydFlask
from scrapyd.flaskwebsite import InitFlaskSources



def application(config):
    app = Application("Scrapyd")
    http_port = config.getint('http_port', 6800)
    http_port = 6801
    bind_address = config.get('bind_address', '127.0.0.1')
    poll_interval = config.getfloat('poll_interval', 5)

    poller = QueuePoller(config)
    eggstorage = FilesystemEggStorage(config)
    scheduler = SpiderScheduler(config)
    environment = Environment(config)

    app.setComponent(IPoller, poller)
    app.setComponent(IEggStorage, eggstorage)
    app.setComponent(ISpiderScheduler, scheduler)
    app.setComponent(IEnvironment, environment)

    laupath = config.get('launcher', 'scrapyd.launcher.Launcher')
    laucls = load_object(laupath)
    launcher = laucls(config, app)

    # webpath = config.get('webroot', 'scrapyd.website.Root')
    # webcls = load_object(webpath)

    timer = TimerService(poll_interval, poller.poll)
    # webservice = TCPServer(http_port, server.Site(webcls(config, app)), interface=bind_address)
    app2=scrapydFlask(app=app,config=config)
    #
    # @app2.route("/")
    # def index():
    #     return "<h1>hello</h1?"
    InitFlaskSources(app2)
    resource = WSGIResource(reactor, reactor.getThreadPool(), app2)
    site = create_site(WSGIRootResource(resource, {}), **{})
    webservice = TCPServer(http_port, site, interface=bind_address)
    log.msg(format="Scrapyd web console available at http://%(bind_address)s:%(http_port)s/",
            bind_address=bind_address, http_port=http_port)

    launcher.setServiceParent(app)
    timer.setServiceParent(app)
    webservice.setServiceParent(app)

    return app
