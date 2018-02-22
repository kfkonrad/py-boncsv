import collections
import math
import sys
import copy


def pre_postfix(string, prefix='', postfix=''):
    if prefix != '' and postfix != '':
        return prefix + string + postfix
    elif prefix != '':
        return prefix + string
    elif postfix != '':
        return string + postfix
    else:
        return string


def strpatch(string, replace=' ', by=' '):
    ret = ''
    for char in string:
        ret += by if char == replace else char
    return ret


def extend_strings(seq, prefix='', postfix='', range_begin=0, range_end=None):
    range_end = len(seq) + 1 if range_end is None else range_end
    ret = []
    for i, elem in enumerate(seq):
        if i >= range_begin and i < range_end:
            ret.append(pre_postfix(elem, prefix=prefix, postfix=postfix))
        else:
            ret.append(elem)
    return ret


def insert_all(*elems,
               source_seq=None,
               into=[],
               position=0,
               prefix='',
               postfix=''):
    if source_seq:
        elems.extend(source_seq)
    for i, elem in enumerate(extend_strings(sorted(elems), prefix, postfix)):
        into.insert(position + i, elem)
    return into


def remove_duplicates(seqseq):
    seq = []
    for subseq in seqseq:
        for elem in subseq:
            seq.append(elem)
    return sorted(set(seq))


def strip_all(seq):
    ret = []
    for elem in seq:
        if elem.strip():
            ret.append(elem.strip())
    return ret


def split_all(seq, split_by=';'):
    return [line.split(split_by) for line in seq]


class Empty_CSV_entry():
    pass


class CSV():
    filename = ""
    csv_content = []
    head = []

    def __init__(self, filename):
        self.filename = filename
        self._readfile_()
        self._remove_empty_lines_()
        self._seperate_head_()

    def _readfile_(self):
        self.csv_content = split_all(open(
            "Auswertung_Fragebogen_nur_Fragebogen.csv",
            'r'
        ).readlines(), ';')

    def _seperate_head_(self):
        self.head = self.csv_content.pop(0)

    def _remove_empty_lines_(self):
        noempty_csv = []
        for line in self.csv_content:
            if line != '':
                noempty_csv.append(line[:-1])
        self.csv_content = noempty_csv

    def declare_numeric(self, seq):  # TODO
        for linenum, line in enumerate(self.csv_content):
            for i in seq:
                if line[i] == '':
                    self.csv_content[linenum][i] = '0'

    def declare_dichotomous(self, seq):  # TODO
        for linenum, line in enumerate(self.csv_content):
            for i in seq:
                if line[i] == '1':
                    self.csv_content[linenum][i] = 't'
                else:
                    self.csv_content[linenum][i] = 'f'

    def extend_head_strings(self,
                            prefix='',
                            postfix='',
                            range_begin=None,
                            range_end=None,
                            seq=[]):  # TODO
        if range_end is None:
            range_end = len(self.head) + 1
        if range_begin is None:
            range_begin = range_end = len(self.head)
        for i, elem in enumerate(self.head):
            if (i >= range_begin and i < range_end) or i in seq:
                self.head[i] = pre_postfix(elem,
                                           prefix=prefix,
                                           postfix=postfix
                                           )

    def rename_head(self, column, newname):
        column_nr = self._soft_flex_col_deref_(column)
        if column_nr is not None:
            self.head[column_nr] = newname

    def replace_spaces_in_head(self, column):
        column_nr = self._soft_flex_col_deref_(column)
        if column_nr is not None:
            self.rename_head(
                column_nr,
                strpatch(self.head[column_nr],
                         replace=' ',
                         by='_'
                         )
            )

    def extract_column(self, column):
        column_nr = self._soft_flex_col_deref_(column)
        return [line[column_nr]
                for line in self.csv_content]

    def _extract_and_split_column_(self, column_nr, split_by=','):
        return [strip_all(entry) for entry in
                split_all(
                    self.extract_column(column_nr),
                    split_by=split_by)
                ]

    def _extend_by_column_(self,
                           name,
                           position,
                           headerprefix='',
                           headerpostfix=''):
        self. head = insert_all(name,
                                into=self.head,
                                position=position,
                                prefix=headerprefix,
                                postfix=headerpostfix)
        for linenr in range(len(self.csv_content)):
            self.csv_content[linenr] = insert_all(
                Empty_CSV_entry(),
                into=self.csv_content[linenr],
                position=position
            )

    def _extend_by_columns_(self,
                            name_seq,
                            begin_position,
                            headerprefix='',
                            headerpostfix=''):
        for i, elem in enumerate(name_seq):
            self._extend_by_column_(elem,
                                    i + begin_position,
                                    headerprefix=headerprefix,
                                    headerpostfix=headerpostfix
                                    )

    def _dichotomous_fill_(self,
                           begin_range=0,
                           ifhasvalue_seq=[[]],
                           colnames=[]):
        for colnr in range(begin_range, begin_range + len(colnames)):
            for linenr, elem in enumerate(ifhasvalue_seq):
                if colnames[colnr - begin_range] in elem:
                    self.csv_content[linenr][colnr] = 't'
                else:
                    self.csv_content[linenr][colnr] = 'f'

    def _flex_col_deref_(self, int_or_string):
        if isinstance(int_or_string, int):
            return int_or_string
        else:
            return self.colnr_by_name(int_or_string)

    def _flex_cols_deref_(self, seq):
        return [self._flex_col_deref_(elem) for elem in seq]

    def _soft_flex_col_deref_(self, int_or_string):
        try:
            return self._flex_col_deref_(int_or_string)
        except ValueError:
            print('Column',
                  int_or_string,
                  "doesn't exist, continue without renaming.",
                  file=sys.stderr
                  )
            return None  # sauberer Abbruch der Methode

    def split_multivalent_column(self,
                                 column,
                                 headerprefix='',
                                 headerpostfix=''):
        column_nr = self._flex_col_deref_(column)

        splitted_multivalents = self._extract_and_split_column_(
            column_nr,
            split_by=','
        )

        nodoubles = remove_duplicates(splitted_multivalents)

        self._extend_by_columns_(nodoubles,
                                 column_nr,
                                 headerprefix=headerprefix,
                                 headerpostfix=headerpostfix
                                 )

        self._dichotomous_fill_(begin_range=column_nr,
                                ifhasvalue_seq=splitted_multivalents,
                                colnames=nodoubles
                                )

    def delete_column(self, column):
        column_nr = self._flex_col_deref_(column)
        for i in range(len(self.csv_content)):
            self.csv_content[i].pop(column_nr)
        self.head.pop(column_nr)

    def _str_log_of_head_lenght_(self):
        return str(math.ceil(math.log(len(self.head), 10)))

    def print_entry(self, linenr):
        maxlen_head = max(len(elem) for elem in self.head)
        loglen = self._str_log_of_head_lenght_()
        outputstring = "%" + loglen + "d: %" + str(maxlen_head) + "s: %s"
        for i, (headelem, elem) in enumerate(
            zip(self.head,
                self.csv_content[linenr]
                )
        ):
            print(outputstring % (i, headelem, elem))

    def print_entries(self):
        for i in range(len(self.head) - 1):
            self.print_entry(i)
            print('\n--------------------\n')
        self.print_entry(-1)

    def print_head(self):
        loglen = self._str_log_of_head_lenght_()
        outputstring = "%" + loglen + "d: %s"
        for i, elem in enumerate(self.head):
            print(outputstring % (i, elem))

    def is_head_unique(self):
        return len(self.head) == len(set(self.head))

    def nonunique_head_elements(self):
        return [item
                for item, count in collections.Counter(self.head).items()
                if count > 1
                ]

    def colnr_by_name(self, name):
        if name in self.nonunique_head_elements():
            raise ValueError("'" + name + "'" +
                             ' is not a unique column specifier of this CSV'
                             )
        try:
            return self.head.index(name)
        except ValueError:
            raise ValueError("'" + name + "'" + ' is not a column of this CSV')

    def to_csv(self):
        def _semicolonprint_(seq):
            ret = ''
            for elem in seq:
                ret += str(elem) + ';'
            return ret[:-1] + '\n\n'

        ret = _semicolonprint_(self.head)
        for line in self.csv_content:
            ret += _semicolonprint_(line)
        return ret

    def order_by_column(self, column):
        column_nr = self._flex_col_deref_(column)
        newcsvcontent = []
        for elem in sorted(set(self.extract_column(column_nr))):
            for line in self.csv_content:
                if line[column_nr] == elem:
                    newcsvcontent.append(line)
        self.csv_content = newcsvcontent
