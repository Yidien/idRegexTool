import numpy as np
import pandas as pd
from AccountId import AccountId


# data = analyse_account(self.line_edit1.text())
column_account = -1


def analyse_account(filename):
    global column_account

    df = pd.read_excel(filename)
    tmp = np.where(df.columns.values == 'accountname')[0]
    column_account = tmp[0] if tmp.size else 0.

    acc_list = []
    for index, row in df.iterrows():
        acc_list.append(AccountId(row.iloc[column_account], index))

    ret = {}
    ret_count = {}
    for acc in acc_list:
        reg_type = acc.reg_type
        sub_type = acc.remark
        if reg_type not in ret:
            ret[reg_type] = {sub_type: [acc]}
            ret_count[reg_type] = {'self': 1, sub_type: {'self': 1}}
            continue
        key = ret[reg_type]
        ret_count[reg_type]['self'] += 1
        if sub_type not in key:
            key[sub_type] = [acc]
            ret_count[reg_type][sub_type] = {'self': 1}
        else:
            key[sub_type].append(acc)
            ret_count[reg_type][sub_type]['self'] += 1
    return ret, ret_count


def copy_row(row_input, row_output, sheet_input, sheet_output, acc=None):
    if acc:
        sheet_output.cell(row=row_output, column=sheet_input.max_column).value = (
            acc.reg_type == 'col_name' and '类型一'
            or acc.reg_type
        )
        sheet_output.cell(row=row_output, column=sheet_input.max_column+1).value = (
            acc.reg_type == 'col_name' and '类型二'
            or acc.remark
        )
    return


def output_file(acc_data, _input_file, _output_file):
    input_df = pd.read_excel(_input_file)
    index_list = [acc.row for acc in acc_data]
    type_1 = [acc.reg_type for acc in acc_data]
    type_2 = [acc.remark for acc in acc_data]
    tmp_df = input_df.iloc[index_list, :]
    tmp_df.insert(tmp_df.shape[1], 'type_1', type_1)
    tmp_df.insert(tmp_df.shape[1], 'type_2', type_2)
    tmp_df.to_excel(_output_file, index=False)
    return
