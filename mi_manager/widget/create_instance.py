import json
import os
import subprocess
import threading

import py_cui

from mi_manager.data.mi_version import version


class Loading:
    def __init__(self, render: py_cui.PyCUI):
        self.render = render

    def start(self, title: str, message: str, callback=None):
        self.render.show_loading_icon_popup(title, message, callback)

    def stop(self):
        self.render.stop_loading_popup()


# row_span=縦の長さ
# column_span=横の長さ

class CreateInstanceCUI:
    def __init__(self, render: py_cui.PyCUI):
        self.render = render
        self.edition_list = ['Misskey', 'Ayuskey', 'Mei']
        self.create_instance = render.create_new_widget_set(4, 4)
        self.loading = Loading(self.render)
        self.edition_select = self.create_instance.add_scroll_menu(
            'Select the edition to use',
            0,
            0,
            row_span=1,
            column_span=2)
        self.edition_select.add_item_list(self.edition_list)
        self.edition_select.add_key_command(py_cui.keys.KEY_ENTER, self.selected_edition)
        self.log_aria = self.create_instance.add_scroll_menu(
            'action logs',
            0,
            2,
            row_span=3,
            column_span=2)
        self.log_aria.set_color(4)
        self.config_editor = self.create_instance.add_text_block('Config Editor', 1,
                                                                 0,
                                                                 row_span=3,
                                                                 column_span=2)
        self.create_instance.add_button('Save', 3, 2, command=self.export_config)
        self.render.apply_widget_set(self.create_instance)
        self.instance_data = {}

    def selected_edition(self):
        self.render.show_yes_no_popup(f'Are you sure in {self.edition_select.get()}?', self.version_select)

    def version_select(self, yes_no: bool):
        if not yes_no:
            return
        self.render.show_menu_popup('Select Version', version[self.edition_select.get()].keys(), self.input_instance_name)

    def input_instance_name(self, instance_version):
        self.instance_data['edition_version'] = instance_version
        self.render.show_text_box_popup(
            'Please enter an instance name', self.input_instance_path
        )
        # self.clone_project

    def input_instance_path(self, instance_name):
        self.render.show_text_box_popup(
            'Please enter an instance directory path', self.save_data
        )
        self.instance_data['name'] = instance_name

    def save_data(self, instance_path: str):
        instance_name = self.instance_data['name']
        self.instance_data['edition'] = self.edition_select.get()
        self.instance_data['instance_path'] = instance_path
        with open('mi_manager.json', 'a+', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                data = {}
            data[instance_name] = self.instance_data
            json.dump(data, f, indent=2, ensure_ascii=False)
        self.clone_project(self.instance_data['edition_version'])

    def clone_project(self, item):
        edition_base = version[self.edition_select.get()][item]
        if edition_base.get('branch'):
            clone_option = {'branch': edition_base['branch']}
        else:
            clone_option = {}
        self.render.show_loading_icon_popup('Currently process is running', 'Waiting for clone end')
        threading.Thread(target=self.clone, args=(edition_base,), kwargs=clone_option).start()

    def clone(self, edition_base, branch: str = None):
        if branch:
            command = ['git', 'clone', edition_base['url'], self.instance_data['instance_path'], '--branch', branch]
        else:
            command = ['git', 'clone', edition_base['url'], self.instance_data['instance_path']]
        self.run_proc('Currently running: git clone', command)
        self.render.stop_loading_popup()
        self.run_yarn()

    def run_proc(self, title: str, command: list, chdir: str = None):
        self.log_aria.set_title('title')
        self.log_aria.clear()
        current_dir = os.getcwd()
        if chdir:
            os.chdir(chdir)
        proc = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        while proc.poll() is None:
            log = proc.stdout.readline().decode('cp932')
            self.log_aria.add_item(log)
        if chdir:
            os.chdir(current_dir)

    def run_yarn(self):
        self.render.show_loading_icon_popup('Currently process is running', 'Waiting for yarn install end')
        command = ['yarn', 'config', 'set', 'network-timeout', '600000', '&&', 'yarn', 'install']
        self.run_proc('Currently running: yarn install', command, self.instance_data['instance_path'])
        self.render.stop_loading_popup()
        self.input_config_data()

    def input_config_data(self):
        self.render.show_message_popup('Success',
                                       'Please customize the part displayed in the config editor and press the save button')
        self.config_editor.set_text(
            """
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Misskey configuration
#━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

#      ┌─────┐
#───┘ URL      └─────────────────────────────────────────────────────

# Final accessible URL seen by a user.
url: https://example.tld/

# ONCE YOU HAVE STARTED THE INSTANCE, DO NOT CHANGE THE
# URL SETTINGS AFTER THAT!

#      ┌───────────────┐
#───┘ Port settings                └───────────────────────────────────────────

#                 +----- https://example.tld/ ------------+
#   +------+      |+-------------+      +----------------+|
#   | User | ---> || Proxy (443) | ---> | Misskey (3000) ||
#   +------+      |+-------------+      +----------------+|
#                 +---------------------------------------+
#
#   You need to setup reverse proxy. (eg. nginx)
#   You do not define 'https' section.

# Listen port
port: 3000

#      ┌──────────────────────────┐
#───┘ PostgreSQL configuration                           └────────────────────────────────

db:
  #host: /var/run/postgresql #unixsocket
  host: localhost
  port: 5432

  # Database name
  db: misskey

  # Auth
  user: example-misskey-user
  pass: example-misskey-pass

  # Whether disable Caching queries
  #disableCache: true

  # Extra Connection options
  #extra:
  #  ssl: true

  # Use PGroonga
  #pgroonga: false

#      ┌─────────────────────┐
#───┘ Redis configuration                      └─────────────────────────────────────

redis:
  #path: /var/run/redis/redis-server.sock #unixsocket
  host: localhost
  port: 6379
  #pass: example-pass
  #prefix: example-prefix
  #db: 1

#      ┌─────────────────────────────┐
#───┘ Elasticsearch configuration                              └─────────────────────────────

#elasticsearch:
#  host: localhost
#  port: 9200
#  ssl: false
#  user: 
#  pass: 

#      ┌─────────────────────┐
#───┘ Sonic configuration                      └─────────────────────────────────────

#sonic:
#  host: localhost
#  port: 1491
#  pass: example-pass


#      ┌───────────────┐
#───┘ ID generation                └───────────────────────────────────────────

# You can select the ID generation method.
# You don't usually need to change this setting, but you can
# change it according to your preferences.

# Available methods:
# aid ... Short, Millisecond accuracy. Not recommended.
# meid ... Similar to ObjectID, Millisecond accuracy
# ulid ... Millisecond accuracy
# objectid ... This is left for backward compatibility

# Use meid or ulid

# ONCE YOU HAVE STARTED THE INSTANCE, DO NOT CHANGE THE
# ID SETTINGS AFTER THAT!

id: 'meid'

#      ┌─────────────────────┐
#───┘ Instance configuration                   └─────────────────────────────────────

# Disable Federation: (default: false)
#disableFederation: true

# Disable URL Preview (default: false)
# disableUrlPreview: true

# If enabled:
#  The first account created is automatically marked as Admin.
autoAdmin: true

# Number of worker processes
#clusterLimit: 1

# Job concurrency per worker
# deliverJobConcurrency: 128
# inboxJobConcurrency: 16

# Job rate limiter
# deliverJobPerSec: 128
# inboxJobPerSec: 16

# Job attempts
# deliverJobMaxAttempts: 12
# inboxJobMaxAttempts: 8

# Syslog option
#syslog:
#  host: localhost
#  port: 514

# Media Proxy
#mediaProxy: https://example.com/proxy

# Sign to ActivityPub GET request (default: true)
#signToActivityPubGet: true

# Upload or download file size limits (bytes)
#maxFileSize: 262144000

#      ┌─────────────────────┐
#───┘ Network configuration                    └─────────────────────────────────────

# IP address family used for outgoing request (ipv4, ipv6 or dual)
#outgoingAddressFamily: ipv4

# Proxy for HTTP/HTTPS
#proxy: http://127.0.0.1:3128

#proxyBypassHosts: [
#  'example.com',
#  '192.0.2.8'
#]

#allowedPrivateNetworks: [
#  '127.0.0.1/32'
#]

# Proxy for SMTP/SMTPS
#proxySmtp: http://127.0.0.1:3128   # use HTTP/1.1 CONNECT
#proxySmtp: socks4://127.0.0.1:1080 # use SOCKS4
#proxySmtp: socks5://127.0.0.1:1080 # use SOCKS5

#      ┌─────────────────────┐
#───┘ Other configuration                      └─────────────────────────────────────

# url-preview "Access-Control-Allow-Origin: *" (default: false) (for External FE)
#urlPreviewCors: true
""")

    def export_config(self):
        if self.instance_data['instance_path'][-1] != '/':
            path = f"{self.instance_data['instance_path']}/"
        else:
            self.instance_data['instance_path']
        with open(path + '.config/default.yml', 'w') as f:
            f.write(self.config_editor.get())

        self.run_build()

    def run_build(self):
        if os.name == 'nt':
            command = ['set', 'NODE_ENV=production', '&&', 'yarn', 'build']
        else:
            command = ['NODE_ENV=production', 'yarn', 'build']
        self.run_proc('Currently running: yarn build', command, self.instance_data['instance_path'])

    def run_migrate(self):
        command = ['yarn', 'migrate']
        self.run_proc('Currently running: yarn migrate', command, self.instance_data['instance_path'])
