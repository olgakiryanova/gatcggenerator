import random
import re
from itertools import permutations, product
from typing import Dict, List, Union

import numpy as np

GOMO_REGEX = re.compile(r'(A{2,})|(C{2,})|(T{2,})|(G{2,})', re.IGNORECASE)
DI_REGEX = re.compile(r'AA|CC|GG|TT|UU', re.IGNORECASE)


def GC(sequence: Union[List, str]) -> float:
    GC_col = sequence.count('G') + sequence.count('C')
    GC_perc = GC_col / len(sequence) * 100
    return GC_perc


def generator(user_data: Dict[str, str]) -> None:
    """Sequence generator function

    Args:
        user_data (Dict[str, str]): General user data for the generator
    Returns:
        str: Returns the path of output file
    """
    nuc = 'ACGT'
    generator_type = user_data['generator_type']
    SEQ_LEN = 5000 if int(user_data['seq_length']) > 5000 else int(user_data['seq_length'])
    SEQ_NUM = 10000 if int(user_data['num_seqs']) > 10000 else int(user_data['num_seqs'])
    gc_min, gc_max = float(user_data['gc_min']), float(user_data['gc_max'])
    NN_min, NN_max = float(user_data['di_min']), float(user_data['di_max'])
    user_id = user_data['user_id']
    rep_list = set()
    for i in permutations(nuc, 2):
        rep_2 = ''.join(i) * 5
        rep_list.add(rep_2)
    for i in permutations(nuc, 3):
        rep_3 = ''.join(i) * 5
        rep_list.add(rep_3)
    for i in permutations(nuc, 4):
        rep_4 = ''.join(i) * 5
        rep_list.add(rep_4)
    rr = []
    for i in product(nuc, repeat=5):
        rep_5 = ''.join(i)
        if len(GOMO_REGEX.findall(rep_5)) == 0:
            rr.append(rep_5 * 5)
    rep_list.update(rr)
    output_file_name = f'{user_id}_output.csv'
    with open(output_file_name, 'w') as f:
        if generator_type != 'RNA':
            f.write('sequence;GC[%];NN[%];A[%];T[%];С[%];G[%]\n')
        else:
            f.write('sequence;GC[%];NN[%];A[%];U[%];С[%];G[%]\n')
        col_seq = 0
        sequences = set()
        while col_seq < SEQ_NUM:
            line = [random.choice(nuc) for _ in range(SEQ_LEN)]
            if (NN_min == 0) and (NN_max == 0):
                NN_perc = 0
                for i in range(SEQ_LEN - 1):
                    if line[i] == line[i + 1]:
                        line[i + 1] = random.choice(list(nuc.replace(line[i], '')))
            else:
                NN_count = len(DI_REGEX.findall(''.join(line)))
                NN_perc = (NN_count * 2 / SEQ_LEN) * 100.0
            GC_p = GC(line)
            line = ''.join(line)
            if (GC_p >= gc_min) and (GC_p <= gc_max) and (line not in rep_list) and (line not in sequences) and (NN_perc >= NN_min) and (NN_perc <= NN_max):
                if generator_type == 'RNA':
                    line = line.replace('T', 'U')
                sequences.add(line)
                A_perc = line.count('A') / SEQ_LEN * 100.0
                G_perc = line.count('G') / SEQ_LEN * 100.0
                C_perc = line.count('C') / SEQ_LEN * 100.0
                if generator_type != 'RNA':
                    T_perc = line.count('T') / SEQ_LEN * 100.0
                    f.write(f'{line};{np.round(GC_p, 2)};{np.round(NN_perc, 2)};{np.round(A_perc, 2)};{np.round(T_perc, 2)};{np.round(C_perc, 2)};{np.round(G_perc, 2)}\n')
                else:
                    U_perc = line.count('U') / SEQ_LEN * 100.0
                    f.write(f'{line};{np.round(GC_p, 2)};{np.round(NN_perc, 2)};{np.round(A_perc, 2)};{np.round(U_perc, 2)};{np.round(C_perc, 2)};{np.round(G_perc, 2)}\n')
                col_seq += 1
