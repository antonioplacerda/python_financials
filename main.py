import json

from googleapiclient.discovery import build
from operator import itemgetter

import config
import auth


class Movements():
    ids = {}
    movs = {}

    def __repr__(self):
        for m in self.movs:
            print(m)
        return ""

    def next_id(self, period):
        if period not in self.ids:
            first_mov = int(period.replace('-', '')) * 1000
            self.ids.setdefault(period, first_mov)

        self.ids[period] += 1
        return self.ids[period]

    def add(self, date: str, account: str, payee: str, amount: float,
            memo: str, comment: str):

        new_id = self.next_id(date[:7])

        new_mov = Movement(new_id, date, account, payee, amount, memo, comment)

        self.movs[new_id] = new_mov

        return new_mov


class Movement():
    def __init__(self, id: int, date: str, account: str, payee: str,
                 amount: float, memo: str, comment: str):
        self.id = id
        self.date = date
        self.account = account
        self.payee = payee
        self.amount = amount
        self.memo = memo
        self.comment = comment

        self.items = []

    def __repr__(self):
        return f'{self.id}: {self.date}'

    def add_item(self, item):
        self.items.append(item)


class Item():
    def __init__(self, amount, project, sub_category, comment):
        self.amount = amount
        self.project = project
        self.sub_category = sub_category
        self.comment = comment


def main():
    """
    """
    creds = auth.get_creds()

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=config.SPREADSHEET_ID,
                                range=config.MOVEMENTS_RANGE).execute()
    values = [x for x in result.get('values', []) if x[0] != '']

    if not values:
        print('No data found.')
        return

    matches = dict()
    movements = Movements()

    values.sort()
    for row in values:
        if row[8] != '':
            id1 = matches.get(row[7])
            if id1 is None:
                matches.setdefault(row[8], row[7])
            else:
                # add this movement as an item for that one
                continue

        movements.add(row[0], row[1], row[2], float(row[3]), row[4], row[5])

    print(json.dumps(movements.__dict__))


if __name__ == '__main__':
    main()
