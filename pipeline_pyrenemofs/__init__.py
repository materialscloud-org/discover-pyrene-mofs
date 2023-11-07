"""Defining my color palette for visualization."""
import collections
import yaml
import pandas as pd
import re
import os
from os.path import join, dirname, realpath
from frozendict import frozendict
from functools import lru_cache, wraps
from aiida.orm.querybuilder import QueryBuilder
from aiida.orm import Node, Dict, Group, WorkChainNode, CifData

TAG_KEY = 'tag4'
GROUP_DIR = "curated-mof"
CONFIG_DIR = join(dirname(realpath(__file__)), "static")
EXPLORE_URL = os.getenv('EXPLORE_URL', "https://dev-www.materialscloud.org/explore/curated-cofs")


def update_config():
    """Add AiiDA profile from environment variables, if specified"""
    from aiida.manage.configuration import load_config
    from aiida.manage.configuration.profile import Profile

    profile_name = os.getenv("AIIDA_PROFILE")
    config = load_config(create=True)
    if profile_name and profile_name not in config.profile_names:
        profile = Profile(
            profile_name, {
                "default_user_email": os.getenv("default_user_email"),
                "storage": {
                    "backend": "core.psql_dos",
                    "config": {
                        "database_engine": os.getenv("AIIDADB_ENGINE"),
                        "database_hostname": os.getenv("AIIDADB_HOST"),
                        "database_port": os.getenv("AIIDADB_PORT"),
                        "database_name": os.getenv("AIIDADB_NAME"),
                        "database_username": os.getenv("AIIDADB_USER"),
                        "database_password": os.getenv("AIIDADB_PASS"),
                        "repository_uri": "file://{}/.aiida/repository/{}".format(os.getenv("AIIDA_PATH"), profile_name),
                    }
                },
                "process_control": {
                    "backend": "rabbitmq",
                    "config": {
                        "broker_protocol": "amqp",
                        "broker_username": "guest",
                        "broker_password": "guest",
                        "broker_host": "127.0.0.1",
                        "broker_port": 5672,
                        "broker_virtual_host": ""
                    }
                },
                "options": {}
            })
        config.add_profile(profile)
        config.set_default_profile(profile_name)
        config.store()

    return config


def load_profile():
    import aiida

    update_config()
    aiida.load_profile()


def freezeargs(func):
    """Transform mutable dictionary unto immutable.

    Makes dictionary hashable, enabling use with lru_cache:

    Usage:

      @freezeargs
      @lru_cache
      def func(...):
        pass

    See https://stackoverflow.com/questions/6358481/using-functools-lru-cache-with-dictionary-arguments
    """

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([frozendict(arg) if isinstance(arg, dict) else arg for arg in args])
        kwargs = {k: frozendict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapped


# Get quantities
with open(join(CONFIG_DIR, "quantities.yml"), 'r') as f:
    quantities_list = yaml.load(f, Loader=yaml.SafeLoader)


def _clean(string):
    """Cleaning function for id strings.

    See https://ericmjl.github.io/pyjanitor/_modules/janitor/functions.html#clean_names
    """
    # pylint: disable=import-outside-toplevel
    from janitor.functions import _change_case, _strip_accents, _normalize_1
    string = _strip_accents(string)
    string = _change_case(string, case_type='lower')
    string = _normalize_1(string)
    string = re.sub("_+", "_", string)
    return string


for item in quantities_list:
    if 'descr' not in item.keys():
        item['descr'] = 'Description to be added!'
    if 'scale' not in item.keys():
        item['scale'] = 'linear'
    item['id'] = _clean('{}_{}_{}'.format(item['key'], item['dict'], item['unit']))

quantities = collections.OrderedDict([(q['label'], frozendict(q)) for q in quantities_list])

# keys of all quantities (features & targets)
QUANTITY_IDS = [q['id'] for k, q in quantities.items()]


@lru_cache()
def get_pyrene_mofs_df():
    return pd.read_csv('pipeline_pyrenemofs/static/pynene-mofs-info.csv')


@lru_cache()
def get_db_nodes_dict():
    """Given return a dictionary with all the curated materials having the material label as key, and a dict of
    curated nodes as value."""

    mat_df = get_pyrene_mofs_df()
    mat_list = list(mat_df['refcode'].values)

    qb = QueryBuilder()
    qb.append(CifData, filters={'label': {'in': mat_list}}, tag='n', project=['label'])
    qb.append(Group, with_node='n', filters={'label': {'like': GROUP_DIR + "%"}}, tag='g')
    qb.append(Node, filters={'extras': {'has_key': TAG_KEY}}, with_group='g', project=['*'])

    db_nodes_dict = {}
    for q in qb.all():
        mat_label = q[0]
        if mat_label not in db_nodes_dict:
            db_nodes_dict[mat_label] = {}
        n = q[1]
        db_nodes_dict[mat_label][n.extras[TAG_KEY]] = n

    return db_nodes_dict


def get_figure_values(db_nodes_dict, q_list):
    """Query the AiiDA database for a list of quantities."""

    figure_values = []
    for mat, nodes_dict in db_nodes_dict.items():
        mat_values = [mat]
        dft_opt = False
        for n in nodes_dict.keys():
            if n == 'opt_cif_ddec':
                dft_opt = True
                break
        for q in q_list:
            if q['key'] == 'is_optimized':
                mat_values.append(dft_opt)
            else:
                for n, v in nodes_dict.items():
                    if n == ['orig_zeopp', 'opt_zeopp'][dft_opt]:
                        mat_values.append(v[q['key']])
                        break
        figure_values.append(mat_values)
    return figure_values


# Get queries
@lru_cache(maxsize=128)
def get_data_aiida(quantitites):
    """Query the AiiDA database

    :param quantities: tuple of quantities to project

    TODO: the group version needs to be better rationalized!
    """

    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': r'curated-cof\_%\_v_'}}, tag='curated_groups')
    qb.append(Node,
              project=['label', 'extras.name_conventional', 'extras.class_material'],
              filters={'extras.{}'.format(TAG_KEY): 'orig_cif'},
              with_group='curated_groups')

    for q in quantitites:
        qb.append(Dict,
                  project=['attributes.{}'.format(q['key'])],
                  filters={'extras.{}'.format(TAG_KEY): q['dict']},
                  with_group='curated_groups')

    return qb.all()


def get_mat_nodes_dict(mat_id):
    """Given a MAT_ID return a dictionary with all the tagged nodes for that material."""

    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': r'curated-___\_{}\_v_'.format(mat_id)}}, tag='curated_groups')
    qb.append(Node, filters={'extras': {'has_key': TAG_KEY}}, with_group='curated_groups')

    mat_nodes_dict = {}
    for q in qb.all():
        n = q[-1]  # if more groups are present with different versions, take the last: QB sorts groups by label
        mat_nodes_dict[n.extras[TAG_KEY]] = n

    return mat_nodes_dict


@lru_cache(maxsize=8)
def get_isotherm_nodes(mat_id):
    """Query the AiiDA database, to get all the isotherms (Dict output of IsothermWorkChain, with GCMC calculations).
    Returning a dictionary like: {'co2: [Dict_0, Dict_1], 'h2': [Dict_0, Dict_1, Dict_2]}
    """

    # Get all the Isotherms
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': r'curated-___\_{}\_v_'.format(mat_id)}}, tag='mat_group')
    qb.append(Dict, filters={'extras.{}'.format(TAG_KEY): {'like': r'isot\_%'}}, with_group='mat_group')

    gas_dict = {}
    for x in qb.all():
        node = x[0]
        gas = node.extras[TAG_KEY].split("_")[1]
        if gas in gas_dict:
            gas_dict[gas].append(node)
        else:
            gas_dict[gas] = [node]

    # Quite diry way to get all the isotherms from an IsothermMultiTemp
    qb = QueryBuilder()
    qb.append(Group, filters={'label': {'like': r'curated-___\_{}\_v_'.format(mat_id)}}, tag='mat_group')
    qb.append(Dict,
              filters={'extras.{}'.format(TAG_KEY): {
                           'like': r'isotmt\_%'
                       }},
              with_group='mat_group',
              tag='isotmt_out',
              project=['extras.{}'.format(TAG_KEY)])
    qb.append(WorkChainNode, with_outgoing='isotmt_out', tag='isotmt_wc')
    qb.append(WorkChainNode,
              edge_filters={'label': {
                  'like': 'run_isotherm_%'
              }},
              with_incoming='isotmt_wc',
              tag='isot_wc')
    qb.append(Dict, edge_filters={'label': 'output_parameters'}, with_incoming='isot_wc', project=['*'])

    for x in qb.all():
        node = x[1]
        gas = x[0].split("_")[1]
        if gas in gas_dict:
            gas_dict[gas].append(node)
        else:
            gas_dict[gas] = [node]

    return gas_dict


# Get color palette

myRdYlGn = (  # modified from Turbo256
    '#5dfb6f',
    '#61fc6c',
    '#65fc68',
    '#69fd65',
    '#6dfd62',
    '#71fd5f',
    '#74fe5c',
    '#78fe59',
    '#7cfe56',
    '#80fe53',
    '#84fe50',
    '#87fe4d',
    '#8bfe4b',
    '#8efe48',
    '#92fe46',
    '#95fe44',
    '#98fe42',
    '#9bfd40',
    '#9efd3e',
    '#a1fc3d',
    '#a4fc3b',
    '#a6fb3a',
    '#a9fb39',
    '#acfa37',
    '#aef937',
    '#b1f836',
    '#b3f835',
    '#b6f735',
    '#b9f534',
    '#bbf434',
    '#bef334',
    '#c0f233',
    '#c3f133',
    '#c5ef33',
    '#c8ee33',
    '#caed33',
    '#cdeb34',
    '#cfea34',
    '#d1e834',
    '#d4e735',
    '#d6e535',
    '#d8e335',
    '#dae236',
    '#dde036',
    '#dfde36',
    '#e1dc37',
    '#e3da37',
    '#e5d838',
    '#e7d738',
    '#e8d538',
    '#ead339',
    '#ecd139',
    '#edcf39',
    '#efcd39',
    '#f0cb3a',
    '#f2c83a',
    '#f3c63a',
    '#f4c43a',
    '#f6c23a',
    '#f7c039',

    # just orange
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f8be39',
    '#f9bc39',
    '#f9ba38',
    '#fab737',
    '#fbb537',
    '#fbb336',
    '#fcb035',
    '#fcae34',
    '#fdab33',
    '#fda932',
    '#fda631',
    '#fda330',
    '#fea12f',
    '#fe9e2e',
    '#fe9b2d',
    '#fe982c',
    '#fd952b',
    '#fd9229',
    '#fd8f28',
    '#fd8c27',
    '#fc8926',
    '#fc8624',
    '#fb8323',
    '#fb8022',
    '#fa7d20',
    '#fa7a1f',
    '#f9771e',
    '#f8741c',
    '#f7711b',
    '#f76e1a',
    '#f66b18',
    '#f56817',
    '#f46516',
    '#f36315',
    '#f26014',
    '#f15d13',
    '#ef5a11',
    '#ee5810',
    '#ed550f',
    '#ec520e',
    '#ea500d',
    '#e94d0d',
    '#e84b0c',
    '#e6490b',
    '#e5460a',
    '#e3440a',
    '#e24209',
    '#e04008',
    '#de3e08',
    '#dd3c07',
    '#db3a07',
    '#d93806',
    '#d73606',
    '#d63405',
    '#d43205',
    '#d23005',
    '#d02f04',
    '#ce2d04',
    '#cb2b03',
    '#c92903',
    '#c72803',
    '#c52602',
    '#c32402',
    '#c02302',
    '#be2102',
    '#bb1f01',
    '#b91e01',
    '#b61c01',
    '#b41b01',
    '#b11901',
    '#ae1801',
    '#ac1601',

    # just red
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501',
    '#a91501')
