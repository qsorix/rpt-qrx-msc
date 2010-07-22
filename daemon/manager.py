#!/usr/bin/evn python
# coding=utf-8

class Manager:

    def __init__(self, conn):
        self.conn = conn

    def create_test(self, parent_id=None, params):
        pass

    def delete_test(self, parent_id=None , params):
        pass

    def add_check_command(self, test_id, params):
        pass

    def add_setup_command(self, test_id, params):
        pass

    def add_task_command(self, test_id, params):
        id = params['id']
        if params.haskey('at'):
            params['at']
        elif params.haskey('every'):
            params['every']
        if params.haskey('output'):
            params['output']
 
    def add_clean_command(self, test_id, params):
        pass

    def add_file(self, test_id, params):
        id = params['id']
        if params.haskey('output'):
            params['output']
 
    def delete_command(self, test_id, params):
        pass

    def get_results(self, test_id, params):
        pass

    def prepare_test(self, parent_id=None, params):
        pass

    def start_test(self, parent_id=None, params):
        pass

    def stop_test(self, parent_id=None, params):
        pass

