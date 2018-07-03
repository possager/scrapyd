from flask import Flask
from twisted.application.service import IServiceCollection
from six.moves.urllib.parse import urlparse
from scrapyd.interfaces import IPoller, IEggStorage, ISpiderScheduler
from twisted.web import resource, static
import socket
from flask import request
from twisted.web.resource import Resource
from twisted.web.server import Site
from flask import render_template
import os
import sys
from scrapyd.utils import native_stringify_dict,get_spider_list,get_project_list
from copy import copy
import json





curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
sys.path.append(curPath)




class scrapydFlask(Flask):
    def __init__(self,config,app,import_name="scrapydFlask", static_path=None, static_url_path=None,
                 static_folder='static', template_folder='templates',
                 instance_path=None, instance_relative_config=False,
                 root_path=None):
        super(scrapydFlask, self).__init__(import_name=import_name, static_path=static_path, static_url_path=static_url_path,
                 static_folder=static_folder, template_folder=template_folder,
                 instance_path=instance_path, instance_relative_config=instance_relative_config,
                 root_path=root_path)
        self.debug = config.getboolean('debug', False)
        self.runner = config.get('runner')
        logsdir = config.get('logs_dir')
        itemsdir = config.get('items_dir')
        local_items = itemsdir and (urlparse(itemsdir).scheme.lower() in ['', 'file'])
        self.app = app
        self.nodename = config.get('node_name', socket.gethostname())
        # self.putChild(b'', Home(self, local_items))
        # if logsdir:
        #     self.putChild(b'logs', static.File(logsdir.encode('ascii', 'ignore'), 'text/plain'))
        # if local_items:
        #     self.putChild(b'items', static.File(itemsdir, 'text/plain'))
        # self.putChild(b'jobs', Jobs(self, local_items))
        services = config.items('services', ())
        # for servName, servClsName in services:
        #     servCls = load_object(servClsName)
        #     self.putChild(servName.encode('utf-8'), servCls(self))
        self.update_projects()


    def update_projects(self):
        self.poller.update_projects()
        self.scheduler.update_projects()


    @property
    def launcher(self):
        app = IServiceCollection(self.app, self.app)
        return app.getServiceNamed('launcher')

    @property
    def scheduler(self):
        return self.app.getComponent(ISpiderScheduler)

    @property
    def eggstorage(self):
        return self.app.getComponent(IEggStorage)

    @property
    def poller(self):
        return self.app.getComponent(IPoller)

    def putChild(self, path, child):
        """
        Register a static child.

        You almost certainly don't want '/' in your path. If you
        intended to have the root of a folder, e.g. /foo/, you want
        path to be ''.

        @see: L{IResource.putChild}
        """
        self.children[path] = child
        child.server = self.server

def InitFlaskSources(scrapydFlaskapp):
    @scrapydFlaskapp.route('/')
    def index():
        return render_template('root.html',name="jacl")

    @scrapydFlaskapp.route('/listprojects.json/')
    def listprojects():
        requests1=request
        print(request)
        args = native_stringify_dict(copy({b'project':[b'default']}), keys_only=False)
        project = args['project'][0]
        version = args.get('_version', [''])[0]
        spiders = get_spider_list(project, runner=scrapydFlaskapp.runner, version=version)
        returndata= {"node_name": scrapydFlaskapp.nodename, "status": "ok", "spiders": spiders}
        return json.dumps(returndata)








class WSGIRootResource(Resource):
    def __init__(self, wsgiResource, children):
        """
        Creates a Twisted Web root resource.
        """
        Resource.__init__(self)
        self._wsgiResource = wsgiResource
        self.children = children

    def getChild(self, path, request):
        request.prepath.pop()
        request.postpath.insert(0, path)
        return self._wsgiResource


def create_site(resource, **options):
    return Site(resource)
# if __name__ == '__main__':
