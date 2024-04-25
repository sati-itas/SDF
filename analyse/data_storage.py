from typing import List

import numpy as np
import yaml


class DataStorage:
    def __init__(self, test_loop=1, solver: str = '', file_path=None) -> None:
        self.file_path = file_path
        # domain
        self.domain = ''
        self.graph_object_number = 0
        self.relation_number = 0
        # agent
        self.action = ''
        # rdf-lib
        self.graph_processing_time = []
        self.query_processing_time = []
        self.effect_execute_processing_time = []
        self.execute_processing_time = (
            []
        )  # effect_execute_processing_time + query_processing_time + graph_processing_time + DELTA
        # solver specific
        self.solver = solver
        self.state_count = 0
        self.state_processing_time = []
        self.planning_processing_time = []
        self.solution = []

        # STATISTIC #
        self.test_loop = test_loop
        self.loop_count = 0
        self.state_count_per_testloop = []

        # rdf_statistic list of means values for each test loop
        self.mean_query_processing_time = []
        self.mean_graph_processing_time = []
        self.mean_effect_execute_processing_time = []
        self.mean_execute_processing_time = []

        # planning
        self.mean_planning_processing_time = np.mean(np.array(self.planning_processing_time))

    def convert2dict_rdfprocessing(self):
        rdf_data_dict = {}

        # rdf_data_dict['graph_processing_time'] = self.graph_processing_time
        # rdf_data_dict['query_processing_time'] = self.query_processing_time
        # rdf_data_dict['effect_execute_processing_time'] = self.effect_execute_processing_time
        # rdf_data_dict['execute_processing_time'] = self.execute_processing_time

        rdf_data_dict['mean_graph_processing_time'] = self.mean_graph_processing_time
        rdf_data_dict['mean_query_processing_time'] = self.mean_query_processing_time
        rdf_data_dict['mean_effect_execute_processing_time'] = self.mean_effect_execute_processing_time
        # rdf_data_dict['mean_execute_processing_time'] = self.mean_execute_processing_time

        return rdf_data_dict

    def convert2dict_planning_time(self):
        rdf_data_dict = {}

        # rdf_data_dict['state_processing_time'] = self.state_processing_time
        rdf_data_dict['planning_processing_time'] = self.planning_processing_time
        # rdf_data_dict['state_count'] = self.state_count

        return rdf_data_dict

    def mean_value(self, list):
        np_array = self.convert_2_nparray(list)
        return np.mean(np_array)

    def convert_2_nparray(self, list):
        try:
            if isinstance(list, List):
                data = np.array(list)
            return data
        except ValueError as exc:
            print(exc)

    def read_yaml(self):
        with open(self.file_path, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                for key, value in data.item():
                    if isinstance(value, list):
                        data[key] = np.array(value)
                return data
            except yaml.YAMLError as exc:
                print(exc)

    def write_yaml(self, data):
        with open(self.file_path, 'w') as outfile:
            try:
                yaml.dump(data, outfile, default_flow_style=False)
            except yaml.YAMLError as exc:
                print(exc)
