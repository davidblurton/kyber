import dulwich
import os
import pykube
import yaml
from dulwich import porcelain as git
from functools import wraps


class ContextError(Exception):
    pass


class Context(object):
    """ A Context object represents the current kyber context, derived from a combination of:
    - the app config found in $CWD/.kyber/config
    - the git repo in $CWD
    - the current kubectl context
    """
    name = None             # current app name
    docker = None           # docker image (repo/app)
    port = None             # app port (not used?) XXX
    tag = None              # git HEAD commit (deployment tag)
    target = None           # kubectl context
    git_dirty = False       # is the git repo dirty? (we only deploy built images)
    _git_status = None
    def __init__(self):
        self.cwd = os.path.abspath('.')
        print "Getting context from {}".format(self.cwd)
        self.load_config()
        self.inspect_git()

    def load_config(self):
        cfg_name = os.path.join(self.cwd, '.kyber/config')
        try:
            with open(cfg_name) as app_config:
                cfg = yaml.load(app_config.read())
        except IOError:
            raise ContextError("Not working within a kyber context (can't read {})".format(
                cfg_name))
        except yaml.ParserError:
            raise ContextError("YAML parsing failed for '{}', unable to load context".format(
                cfg_name))
        self.name = cfg['app']['name']
        self.docker = cfg['app']['docker']
        self.port = cfg['app']['port']

    def inspect_git(self):
        """
        """
        try:

    def inspect_git(self):
        """
        """
        try:
            status = git.status()
        except dulwich.errors.NotGitRepository:
            raise ContextError("{} is not a valid git repository".format(self.cwd))

        repo = git.Repo(self.cwd)
        self.tag = 'git_{}'.format(repo.head)
        for state in ('add', 'modify', 'delete'):
            if status['staged'][state]:
                self.is_dirty = True
                break
        if status['unstaged']:
            self.is_dirty = True
        self._git_status = status

    def inspect_kube(self):
        # XXX: maybe this should be derived from environment variables exported by
        # kube-ctx.bash ?
        kube_cfg_path = "~/.kube/config"
        try:
            cfg = pykube.KubeConfig.from_file(kube_cfg_path)
        except pykube.exceptions.PyKubeError
            raise ContextError("Can't find a kube config in '{}'".format(kube_cfg_path))
        self.target = cfg.current_context


_ctx = Context()
name = _ctx.name
docker = _ctx.docker
tag = _ctx.tag
target = _ctx.target
dirty = _ctx.git_dirty
dirty_reason = _ctx._git_status


__all__ = [name, docker, tag, target, dirty, dirty_reason]