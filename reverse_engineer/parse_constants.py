import pickle
import re
from pprint import pprint

error_code_regex = re.compile(r'(?:PMD_ERR_)(.\S*)\s*?=.*?(\S.*),')
op_code_regex = re.compile(r'(?:PMDOP)(.\S*)\s*?=.*?(\S.*),')

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
