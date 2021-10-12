import json
import os
import re
import subprocess
import threading
import time

import git
import py_cui

from mi_manager.data.mi_version import version


class Loading:
    def __init__(self, render: py_cui.PyCUI):
        self.render = render

    def start(self, title: str, message: str, callback=None):
        self.render.show_loading_icon_popup(title, message, callback)

    def stop(self):
        self.render.stop_loading_popup()


class CreateInstanceCUI:
    def __init__(self, render: py_cui.PyCUI):
        self.render = render
        self.edition_list = ['Misskey', 'Ayuskey', 'Mei']
        self.create_instance = render.create_new_widget_set(2, 2)
        self.loading = Loading(self.render)
        self.edition_select = self.create_instance.add_scroll_menu(
            'Select the edition to use',
            0,
            0,
            row_span=1,
            column_span=1)
        self.log_aria = self.create_instance.add_scroll_menu(
            'action logs',
            0,
            1,
            row_span=1,
            column_span=1)
        self.log_aria.set_color(4)
        self.edition_select.add_item_list(self.edition_list)
        self.edition_select.add_key_command(py_cui.keys.KEY_ENTER, self.selected_edition)
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

    def clone(self, edition_base, branch: str=None):
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
        command = ['yarn', 'config', 'set', 'network-timeout', '600000', '&&' ,'yarn', 'install']
        self.run_proc('Currently running: yarn install', command, self.instance_data['instance_path'])
        self.run_build()

    def run_build(self):
        if os.name == 'nt':
            command = ['set', 'NODE_ENV=production', '&&', 'yarn', 'install']
        else:
            command = ['NODE_ENV=production', 'yarn', 'install']
        self.run_proc('Currently running: yarn build', command, self.instance_data['instance_path'])

#def input_config_data:
#    # TODO: default.ymlの設定を作る
