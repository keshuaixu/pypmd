import logging
import pickle
import re
import json
from pprint import pprint, pformat

error_code_regex = re.compile(r'(?:PMD_ERR_)(.\S*)\s*?=.*?(\S.*),')
op_code_regex = re.compile(r'(?:PMDOP)(.\S*)\s*?=.*?(\S.*),')
c_motion_regex = re.compile(
    r'PMDCFunc PMD(.\S*).*?\((.*?)\)[\S\s]*?{[\S\s]*?return SendCommand(.*?)??(?:Get(.*?))?\([\S\s]*?}')

with open('PMDocode.h') as f:
    op_codes = {}
    lines = f.readlines()
    constant_lines = map(op_code_regex.search, lines)
    constant_lines = filter(lambda m: m, constant_lines)
    for match in constant_lines:
        op_codes[match.group(1)] = int(match.group(2), 16)

    pprint(op_codes)

    with open('../pypmd/op_codes.pickle', 'wb') as pf:
        pickle.dump(op_codes, pf, pickle.HIGHEST_PROTOCOL)

with open('PMDecode.h') as f:
    err_codes = {}
    lines = f.readlines()
    constant_lines = map(error_code_regex.search, lines)
    constant_lines = filter(lambda m: m, constant_lines)
    for match in constant_lines:
        err_codes[int(match.group(2), 16)] = match.group(1)

    pprint(err_codes)

    with open('../pypmd/err_codes.pickle', 'wb') as pf:
        pickle.dump(err_codes, pf, pickle.HIGHEST_PROTOCOL)

pmd_types = {'PMDuint8': 'uint:8',
             'PMDuint16': 'uint:16',
             'PMDuint32': 'uint:32',
             'PMDint8': 'int:8',
             'PMDint16': 'int:16',
             'PMDint32': 'int:32',
             }


def convert_to_bitstring_format(pmd_format):
    return str.join(', ', map(pmd_types.get, pmd_format))


with open('c-motion.c') as f:
    c_motion_functions = {}
    lines = str.join('\n', f.readlines())
    for match in c_motion_regex.finditer(lines):
        try:
            function_name = match.group(1)
            args = match.group(2).split(',')[1:]
            input_names = []
            output_names = []
            input_format = []
            output_format = []
            for arg in args:
                arg_type, arg_name = arg.strip().split()
                if arg_type in ('PMDAxis', 'PMDAxis*'):
                    break
                if arg_type.endswith('*'):
                    output_names.append(arg_name)
                    output_format.append(arg_type[:-1])
                else:
                    input_names.append(arg_name)
                    input_format.append(arg_type)
            else:
                entry = {'op_code': op_codes[function_name],
                         'input_names': input_names, 'input_format': convert_to_bitstring_format(input_format),
                         'output_names': output_names, 'output_format': convert_to_bitstring_format(output_format)}
                c_motion_functions[function_name] = entry
        except KeyError:
            logging.warning(f'{function_name} doe not exist in op codes')
    pprint(c_motion_functions)
    with open('../pypmd/c_motion_functions.json', 'w') as cm:
        json.dump(c_motion_functions, cm, sort_keys=True, indent=4)
