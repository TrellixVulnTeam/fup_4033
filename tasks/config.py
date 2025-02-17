import argparse
from dataclasses import dataclass, field
import yaml
import os
import re
import sys
from typing import List, Dict, Union

import tasks.http
import tasks.unless

DEFAULT_CONFIG_FILE = os.path.expanduser('~/.config/fup/fup.yml')
CONFIG_FILE_ENV = 'FUP_CONFIG_FILE'


@dataclass
class Settings:
    archive_dir: str = '~'
    clone_dir: str = '~'
    github_user: str = ''
    host_facts: Dict[str, Dict[str, str]] = field(default_factory=dict)
    self_clone_dir: str = '~'
    virtualenv_dir: str = '~'


@dataclass
class Whenable:
    when: str = ''


@dataclass
class Archive(Whenable):
    url: str = ''
    binary: str = ''
    execute_after: str = ''
    set_permissions: bool = False
    symlink: str = ''
    target: str = ''
    unless: Union[tasks.unless.UnlessCmd, tasks.unless.UnlessFile] = None
    version: str = ''


@dataclass
class CargoCrate:
    name: str
    unless: Union[tasks.unless.UnlessCmd, tasks.unless.UnlessFile] = None
    bins: bool = False


@dataclass
class GoPkg:
    name: str
    unless: Union[tasks.unless.UnlessCmd, tasks.unless.UnlessFile] = None
    host: str = 'github.com'
    version: str = 'latest'


@dataclass
class Template(Whenable):
    dest: str = ''
    src: str = ''
    mode: str = '0644'
    context: Dict[str, str] = field(default_factory=dict)


@dataclass
class ServiceUnit:
    exec: str
    description: str
    before: str = ''
    type: str = ''
    wanted_by: str = 'default'
    environment: List[Dict[str, str]] = field(default_factory=list)
    service_options: Dict[str, str] = field(default_factory=dict)


@dataclass
class Service:
    name: str
    user: bool = True
    start: bool = True
    enable: bool = True
    unit: ServiceUnit = None
    context: Dict[str, str] = field(default_factory=dict)
    when: str = ''


@dataclass
class GithubUserKeys:
    user: str = ''


@dataclass
class Repo(Whenable):
    name: str = ''
    host: str = 'github.com'
    ref: str = ''
    submodule: bool = False
    recursive_submodule: bool = False
    remotes: Dict = field(default_factory=dict)


@dataclass
class PipPkg:
    name: str
    reqs: List[str] = field(default_factory=list)


@dataclass
class EnsureLine(Whenable):
    name: str = ''
    file: str = ''
    text: str = ''
    replace: str = ''


@dataclass
class Config:
    accept_host_keys: List[str] = field(default_factory=list)
    archives: List[Archive] = field(default_factory=list)
    cargo: List[CargoCrate] = field(default_factory=list)
    ensure_lines: List[EnsureLine] = field(default_factory=list)
    github_user_keys: Dict[str, str] = field(default_factory=dict)
    gopkg: List[GoPkg] = field(default_factory=list)
    packages: Dict[str, List[str]] = field(default_factory=dict)
    pip_pkgs: List[PipPkg] = field(default_factory=list)
    preflight: Dict = field(default_factory=dict)
    recipes: Dict = field(default_factory=dict)
    repos: List[Repo] = field(default_factory=list)
    services: List[Service] = field(default_factory=list)
    settings: Dict = field(default_factory=dict)
    templates: List[Template] = field(default_factory=list)
    unwanted_packages: Dict[str, List[str]] = field(default_factory=dict)
    unwanted_dirs: List[str] = field(default_factory=list)


def get_config_file() -> str:
    return os.getenv(CONFIG_FILE_ENV, DEFAULT_CONFIG_FILE)


def read_remote_config(config_file: str):
    return tasks.http.http_request(config_file, 'GET', return_response_object=True)


def get_config_body():
    config_file = get_config_file()

    if re.match('^http(s)://.*', config_file):
        return read_remote_config(config_file)

    return open(os.path.realpath(config_file))


def get_config():
    with get_config_body() as f:
        cfg_dict = yaml.load(f, Loader=yaml.SafeLoader)
        cfg = Config(**cfg_dict)
        cfg.settings = Settings(**cfg.settings)
        return cfg
