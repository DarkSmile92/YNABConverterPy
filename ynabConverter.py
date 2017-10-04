#!/usr/bin/env python
#title           :ynabConverter.py
#description     :This script converts german bank statement formats into a CSV file format ready to import into YNAB.
#author          :Robin Kretzschmar <dev@rkmail.email>
#date            :20171004
#version         :0.1
#usage           :python ynabConverter.py
#notes           :
#python_version  :3.6.2
#==============================================================================

import csv
import re
from datetime import datetime

from collections import namedtuple


# abstract superclass
class YNABConverter:
    def __init__(self):
        self.filename = ''
        self.input_format = 0
        self.date_format = '%d.%m.%Y'
        self.output_date_format = '%d.%m.%Y'
        self.input_delimiter = ';'

    def convert(self, filepath):
        if not filepath:
            return

    def parse_string_value(self, val):
        prep = str(val).strip()
        prep = prep.replace(',', '.')
        prep = prep.replace('\r', '')
        prep = prep.replace('\n', ' ')
        # remove multiple blank spaces
        prep = re.sub(' +', ' ', prep)
        return prep

# converting statements from N26 Bank GmbH
class N26Converter(YNABConverter):
    def __init__(self):
        super(N26Converter, self).__init__()
        self.date_format = '%Y-%m-%d'
        self.skip_first_row = True
        self.parsed_records = []
        self.input_delimiter = ','

    def convert(self, filepath):
        # construct named tuple to access it by field names
        TransferRecord = namedtuple('TransferRecord', 'date payee category memo outflow inflow')
        self.parsed_records = []

        with open(filepath, 'r', encoding='ISO-8859-1') as spkrecords:
            for row_idx, record in enumerate(csv.reader(spkrecords, delimiter=self.input_delimiter, quotechar='"')):
                if (self.skip_first_row and row_idx > 0) or (not self.skip_first_row):
                    # print(record)
                    values = [datetime.now(), '', '', '', float(0), float(0)]
                    for idx, field in enumerate(record):
                        # print('Field: {0} IDX: {1}'.format(field, idx))
                        # Datum
                        if idx == 0:
                            values[0] = datetime.strptime(field, self.date_format)
                        # Verwendungszweck
                        elif idx == 4:
                            values[3] = self.parse_string_value(field)
                        # Empfaenger
                        elif idx == 1:
                            values[1] = self.parse_string_value(field)
                        # Betrag
                        elif idx == 6:
                            # decide if positive or negative
                            parsed = float(str(field).replace(',', '.'))
                            if parsed < 0:
                                values[4] = float(abs(parsed))
                                values[5] = ''
                            else:
                                values[4] = ''
                                values[5] = float(abs(parsed))
                    self.parsed_records.append(TransferRecord(*values))
        return self.parsed_records

    def write_out(self, outfile='converted_n26.csv'):
        if not self.parsed_records:
            return

        with open(outfile, 'w', newline='', encoding='utf-8') as converted_file:
            outwrtier = csv.writer(converted_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # write header line
            outwrtier.writerow(['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow'])
            for line in self.parsed_records:
                outwrtier.writerow([line.date.strftime(self.output_date_format), line.payee, line.category, line.memo, line.outflow, line.inflow])


# converting statements from Sparkasse
class SPKConverter(YNABConverter):
    def __init__(self):
        super(SPKConverter, self).__init__()
        self.date_format = '%d.%m.%y'
        self.skip_first_row = True
        self.parsed_records = []


    def convert(self, filepath):
        # construct named tuple to access it by field names
        TransferRecord = namedtuple('TransferRecord', 'date payee category memo outflow inflow')
        self.parsed_records = []

        with open(filepath, 'r', encoding='ISO-8859-1') as spkrecords:
            for row_idx, record in enumerate(csv.reader(spkrecords, delimiter=self.input_delimiter, quotechar='"')):
                if (self.skip_first_row and row_idx > 0) or (not self.skip_first_row):
                    # print(record)
                    values = [datetime.now(), '', '', '', float(0), float(0)]
                    for idx, field in enumerate(record):
                        # print('Field: {0} IDX: {1}'.format(field, idx))
                        # Buchungstag
                        if idx == 1:
                            values[0] = datetime.strptime(field, self.date_format)
                        # Verwendungszweck
                        elif idx == 4:
                            values[3] = self.parse_string_value(field)
                        # Beguenstigter/Zahlungspflichtiger
                        elif idx == 11:
                            values[1] = self.parse_string_value(field)
                        # Betrag
                        elif idx == 14:
                            # decide if positive or negative
                            parsed = float(str(field).replace(',', '.'))
                            if parsed < 0:
                                values[4] = float(abs(parsed))
                                values[5] = ''
                            else:
                                values[4] = ''
                                values[5] = float(abs(parsed))
                    self.parsed_records.append(TransferRecord(*values))
        return self.parsed_records

    def write_out(self, outfile='converted_spk.csv'):
        if not self.parsed_records:
            return

        with open(outfile, 'w', newline='', encoding='utf-8') as converted_file:
            outwrtier = csv.writer(converted_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            # write header line
            outwrtier.writerow(['Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow'])
            for line in self.parsed_records:
                outwrtier.writerow([line.date.strftime(self.output_date_format), line.payee, line.category, line.memo, line.outflow, line.inflow])


# Usage: change converter initialization to wanted converter and call convert() with the input filename

converter = SPKConverter()
records = converter.convert('spk_jan17bisokt2.CSV')
# print(records)
converter.write_out()
