import logging
import click
import requests
import sys
import zipfile
import os
from azkaban import Azkaban

__version__ = u'0.1.1'

def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    click.echo(u'Azkaban CLI v%s' % (__version__))
    ctx.exit()

# TODO: implement login cache
def __get_azkaban_api(ctx):
    if u'azkaban_api' in ctx.obj.keys():
        return ctx.obj[u'azkaban_api']


def __login(ctx, host, user, password):
    azkaban = Azkaban()

    azkaban.login(host, user, password)

    ctx.obj[u'azkaban_api'] = azkaban

def __upload(ctx, path, project, zip_name):
    azkaban = __get_azkaban_api(ctx)

    azkaban.upload(path, project, zip_name)

def __schedule(ctx, project, flow, cron):
    azkaban = __get_azkaban_api(ctx)

    azkaban.schedule(project, flow, cron)

def __call_for_login(ctx, host):
    ctx.invoke(login, host=host, user=click.prompt('User'), password=click.prompt('Password', hide_input=True))

# ----------------------------------------------------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------------------------------------------------

@click.group(chain=True)
@click.option(u'--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True)
def cli():
    log_level = logging.INFO

    # log record format string
    format_string = u'%(asctime)s\t%(levelname)s\t%(message)s'

    # set default logging (to console)
    logging.basicConfig(level=log_level, format=format_string)
    
    ctx = click.get_current_context()

    ctx.obj = {}

@click.command(u'login')
@click.pass_context
@click.option(u'--host', prompt=True, help=u'Azkaban hostname with protocol.')
@click.option(u'--user', prompt=True, help=u'Login user.')
@click.option(u'--password', prompt=True, hide_input=True, help=u'Login password.')
def login(ctx, host, user, password):
    __login(ctx, host, user, password)

@click.command(u'upload')
@click.pass_context
@click.option(u'--host', prompt=True, help=u'Azkaban hostname with protocol.')
@click.argument(u'path', type=click.STRING)
@click.option(u'--project', type=click.STRING, help=u'Project name in Azkaban, default value is the dirname specified in path argument.')
@click.option(u'--zip-name', type=click.STRING, help=u'Zip file name that will be uploaded to Azkaban. Default value is project name.')
def upload(ctx, host, path, project, zip_name):
    __call_for_login(ctx, host)
    __upload(ctx, path, project, zip_name)

@click.command(u'schedule')
@click.pass_context
@click.option(u'--host', prompt=True, help=u'Azkaban hostname with protocol.')
@click.argument(u'project', type=click.STRING)
@click.argument(u'flow', type=click.STRING)
@click.argument(u'cron', type=click.STRING)
def schedule(ctx, host, project, flow, cron):
    __call_for_login(ctx, host)
    __schedule(ctx, project, flow, cron)

cli.add_command(upload)
cli.add_command(schedule)

# ----------------------------------------------------------------------------------------------------------------------
# Interface
# ----------------------------------------------------------------------------------------------------------------------

        
if __name__ == u'__main__':
    try:
        cli()

    except Exception as ex:
        logging.error(ex)

        sys.exit()

