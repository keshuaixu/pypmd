import logging
import pprint

import pyshark
import pickle


def analyze(filename: str):
    mysteries = {}
    cap = pyshark.FileCapture(filename)
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
    return mysteries


mys = analyze('mystery_code.pcapng')
mys.update(analyze('mystery_current.pcapng'))
mys.update(analyze('mystery_position.pcapng'))



pprint.pprint(mys)

with open('../pypmd/mystery_code.pickle', 'wb') as f:
    pickle.dump(mys, f, pickle.HIGHEST_PROTOCOL)
