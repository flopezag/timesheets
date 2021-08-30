from googleapiclient.discovery import build
from datetime import datetime, timedelta


class Timesheet:
    def __init__(self, credentials):
        # The ID and range of a sample spreadsheet.
        self.SAMPLE_SPREADSHEET_ID = <ID>
        self.SAMPLE_RANGE_NAME = <RANGE>
        self.credentials = credentials
        self.values = list()

    def get_data_from_timesheet(self):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        service = build('sheets', 'v4', credentials=self.credentials)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                    range=self.SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        #if not values:
        #    print('No data found.')
        #else:
        #    print('Name, Major:')
        #
        #    # Print all columns.
        #    list(map(lambda x: print(f'{x} '), values))

        service.close()
        self.values = values

    def data_analysis(self):
        length = len(self.values)
        last_data_row = length - 74
        aux = self.values[9:last_data_row]
        last_day = int(aux[len(aux) - 1][0])

        # Get the days that are weekends
        weekend = list(filter(lambda x: x[2] == 'WeekEnd Day', aux))
        weekend = list(map(lambda x: int(x[0]), weekend))

        for i in range(1, last_day):
            # Filter list for day and extract only the corresponding columns of hours
            # and the day is not weekend
            temp1 = list(filter(lambda x: x[0] in [str(i)] and x[2] != 'WeekEnd Day', aux))
            temp1 = list(map(lambda x: [x[6], x[7], x[8]], temp1))

            # Check difference between "End h" and "Start h"
            list(map(lambda x: self.__validate_diff_hours__(day=i, hours=x), temp1))

            # Check number hours per day equal to 8
            temp1 = list(map(lambda x: x[2], temp1))
            self.__validate_sum_hours_day__(day=i, hours=temp1, weekend=weekend)

    def __validate_diff_hours__(self, day, hours):
        format = '%H:%M'

        # we specify the input and the format...
        t = datetime.strptime(hours[2], "%H:%M:%S")
        # ...and use datetime's hour, min and sec properties to build a timedelta
        delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

        diff = datetime.strptime(hours[1], format) - datetime.strptime(hours[0], format)

        if diff != delta:
            if diff - delta == timedelta(minutes=45):
                print(f'WARNING, the difference is not correct on day {day}, hours {hours}, diff {diff - delta}')
            else:
                print(f'ERROR, the difference is not correct on day {day}, hours {hours}, diff {diff - delta}')

    def __validate_sum_hours_day__(self, day, hours, weekend):
        # print(day, hours)
        aux = list(map(lambda x: x[2], hours))

        for i in range(0, len(aux)):
            t = datetime.strptime(hours[i], "%H:%M:%S")
            delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
            aux[i] = delta

        result = sum(aux, timedelta())

        if result != timedelta(hours=8) and day not in weekend:
            print(f'Error: day {day} has a sum of hours different from 8, total: {result}')


