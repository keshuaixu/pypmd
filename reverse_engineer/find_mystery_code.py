import logging
import pprint

import pyshark
import pickle

cap = pyshark.FileCapture('mystery_code.pcapng')

mysteries = {}

for p in cap:
    try:
        d = p.data.data
        if d.startswith('6240'):
            op_code = int(d[4:6], 16)
            mystery_code = int(d[6], 16)
            if op_code in mysteries and mysteries[op_code] != mystery_code:
                logging.error(
                    f'inconsistent mystery code found! op {op_code} old {mysteries[op_code]} new {mystery_code}')
            mysteries[op_code] = mystery_code
    except Exception as e:
        pass

pprint.pprint(mysteries)

with open('../pypmd/mystery_code.pickle', 'wb') as f:
    pickle.dump(mysteries, f, pickle.HIGHEST_PROTOCOL)
