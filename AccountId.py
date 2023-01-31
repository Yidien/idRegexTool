import re


class AccountId:
    default_type = 'none_type'

    def __init__(self, account_id=None, row=-1):
        # 赋值
        self.pattern_dict = dict()
        self.account_id = None
        self.reg_type = self.default_type
        self.other_type = ''
        self.re_result = None
        self.in_phone = None
        self.remark = None
        self.len = None
        self.row = row

        # 初始化
        self.init_pattern()

        # 执行
        self.set_account_id(str(account_id))
        return

    def init_pattern(self):
        self.pattern_dict['phone_reg'] = \
            r'1(3[0-9]|4[5,7]|5[0,1,2,3,5,6,7,8,9]|6[2,5,6,7]|7[0,1,7,8]|8[0-9]|9[1,8,9])\d{8}'
        self.pattern_dict['mail_reg'] = r'(?P<mail_name>.+)@(?P<firm_name>.+)\.(?P<domain_type>.+)'
        self.pattern_dict['char_num_reg'] = r'(?P<char>[A-Za-z]+)(?P<num>\d+)'
        self.pattern_dict['char_reg'] = r'[A-Za-z]+'
        return

    def add_pattern(self, key, value):
        self.pattern_dict[key] = value
        return

    def jude_char_type(self, char):
        if char.isdigit():
            return 'n'
        if char.islower():
            return 'c'
        if char.isupper():
            return 'C'
        return 'f'

    def full_match_pattern(self):
        for key, value in self.pattern_dict.items():
            re_result = re.fullmatch(value, self.account_id)
            if re_result:
                self.reg_type = key
                self.re_result = re_result
                break
        if self.reg_type == self.default_type:
            char_type = None
            other_type = ''
            for char in self.account_id:
                current_type = self.jude_char_type(char)
                if current_type != char_type:
                    other_type += current_type + '_'
                char_type = current_type
            self.other_type = other_type[:-1]
        self.remark = \
            self.reg_type == 'mail_reg' and '@' + self.re_result[2] + '.' + self.re_result[3]\
            or self.reg_type == 'none_type' and self.other_type \
            or str(self.len)
        return

    def match_phone(self):
        reg = r'(?<![0-9])1(3[0-9]|4[5,7]|5[0,1,2,3,5,6,7,8,9]|6[2,5,6,7]|7[0,1,7,8]|8[0-9]|9[1,8,9])\d{8}(?![0-9])'
        self.in_phone = re.search(reg, self.account_id)
        return

    def set_account_id(self, account_id):
        if account_id:
            self.account_id = account_id
            self.len = len(account_id)
            self.match_phone()
            self.full_match_pattern()
        return
