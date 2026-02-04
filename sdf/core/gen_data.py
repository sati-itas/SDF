import importlib
import os
import sys

from sdf.core.rdf_wrapper import RDFWrapper


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
base_dir = os.path.join(parent_dir, '..')
# append parent and base direction
sys.path.append(parent_dir)
sys.path.append(base_dir)


class DataGenerator:
    def __init__(self, graph_file: str):
        self.graph_file = graph_file

        self.rdf_wrapper = RDFWrapper()
        self._graph_datagen = self.rdf_wrapper.load_rdf_graph(self.graph_file, 'ttl')
        self.rdf_wrapper.get_base_uri(self._graph_datagen)
        self.gen_path = 'sdf/data/_gen'

    def gen_enum_types(self, class_type: str, py_file: str, import_modul=False):
        subcls = self.rdf_wrapper.get_subclasses(
            self._graph_datagen, f'{self.rdf_wrapper.base_uri}{class_type}'
        )
        self.gen_enumfile_from_subcls(self.gen_path, py_file, subcls, class_type)

        # import generated file as modul
        if import_modul:
            module_path = self.gen_path.replace('/', '.')
            module_name = f'{module_path}.{py_file}'
            module = importlib.import_module(module_name)
            Type = getattr(module, class_type, None)
            if Type is None:
                raise ImportError(f"enum class '{class_type}' not found in '{py_file}'")
            # from typing import cast # fake-import for Pylance (optional)
            # from data._gen.domain_otypes import DomainTypes
            # Type = cast(DomainTypes,Type)
            return Type

    def gen_types(self, class_type: str):
        subclasses = self.rdf_wrapper.get_subclasses(
            self._graph_datagen, f'{self.rdf_wrapper.base_uri}#{class_type}'
        )
        return subclasses

    def gen_predicates(self, py_filename=None):
        # generate SDF Predicates from data
        predicates = self.rdf_wrapper.get_predicates(self._graph_datagen)
        from core.sdf_core import Predicate

        predicate_dict = {}
        for pred_str in predicates:
            predicate = Predicate(f'{pred_str}')
            predicate_dict[f'{pred_str}'] = predicate

        if py_filename:
            os.makedirs(self.gen_path, exist_ok=True)
            with open(f'{self.gen_path}/{py_filename}', 'w', encoding='utf-8') as f:
                pred_list = ''
                for pred in predicates:
                    pred_list += f'{pred}\n'
                f.write(pred_list)

        return predicate_dict

    @staticmethod
    def gen_enumfile_from_subcls(gen_path, py_filename, subclasses, type_str):
        """generates pythonfile with enum class from given graph subclasses"""
        if '.' in py_filename:
            if py_filename.split('.')[-1] == 'py':
                pass
            else:
                py_filename = py_filename.split('.')[-1] + '.py'
        else:
            py_filename = py_filename + '.py'

        enum_code = 'from enum import Enum\n\n'

        def gen_enum_code(class_name, subclasses, processed=None):
            """generates enum classes with correct ordering, so that references
            are only made after definition.
            """
            if processed is None:
                processed = set()

            code = ''

            # 1. define all subclasses before referencing them in the main class.
            for name, deeper in subclasses.items():
                if deeper and name not in processed:
                    code += gen_enum_code(name, deeper, processed)
                    processed.add(name)

            # 2. define the actual class
            code += f'\nclass {class_name}(Enum):\n'

            # 3. enum-values first
            enum_values = [name for name, deeper in subclasses.items() if not deeper]
            for name in enum_values:
                code += f"\t{name.upper()} = '{name}'\n"

            # 4. set the references to other enums.
            nested_classes = [name for name, deeper in subclasses.items() if deeper]
            for name in nested_classes:
                code += f'\t{name.upper()} = {name}\n'

            code += '\n'
            return code

        enum_code += f'{gen_enum_code(type_str, subclasses)}'

        os.makedirs(gen_path, exist_ok=True)
        with open(f'{gen_path}/{py_filename}', 'w', encoding='utf-8') as f:
            f.write(enum_code)

        print(f'File {py_filename} generated. Location in "data/{py_filename}"')
