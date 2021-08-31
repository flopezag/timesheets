from googleapiclient.discovery import build
from datetime import datetime, timedelta
from pandas import DataFrame, Timedelta, to_timedelta


class Timesheet:
    def __init__(self, credentials):
        # The ID and range of a sample spreadsheet.
        self.SAMPLE_SPREADSHEET_ID = "1pacXhdQ8h_Is9kEM4rNm9raTHRQ8lBAAqQ4TZYQFBgo"
        self.SAMPLE_RANGE_NAME = "Template!B4:N"
        self.credentials = credentials
        self.values = list()
        self.data = list()

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

    def data_analysis_validation(self):
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

        self.data = aux

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

    def data_extraction(self):
        df = DataFrame(self.data)

        # Assign the correct name to the columns
        df.columns = ['day', 'code', 'project', 'wp', 'task', 'location', 'start', 'end', 'hours', 'a', 'b', 'c', 'd']

        # Extract a sub-dataframe of the data interested to manage ('project', 'wp', 'task', 'hours')
        df = df[["project", "wp", "task", "hours"]]

        # Convert column "hours" from string to timedelta
        df['hours'] = to_timedelta(df['hours'])

        # Get the unique list of values of the column project
        projects = df.project.unique().tolist()

        # Calculate the sum of hours per each WP and per each task
        for p in projects:
            mask = df['project'].values == p
            aux_df = df.loc[mask]
            aux_df.columns = ["project", "wp", "task", "hours"]

            # Need to check the column [1](wp) and column [2](task),
            # - if [1] is empty then we create an array of 12 values, each per month with the sum of column [3]
            # - if [1] has value but [2] is empty, create a list of wps in which each of them is the sum of [3]
            # - if [1] and [2] have values, create a list of wps with a list of tasks with the array of sums of [3]
            column1 = aux_df['wp'].values[1]
            column2 = aux_df['task'].values[1]

            if column1 == '':
                # array of sum values for project
                total = aux_df['hours'].sum()
                print(f'project "{p}" total hours "{total}"')
            elif column2 == '':
                # array of sum values for each wp
                wps = aux_df.wp.unique().tolist()
                total_wps = dict()
                for w in wps:
                    mask_wp = aux_df['wp'].values == w
                    aux_df_wp = aux_df.loc[mask_wp]
                    total_wps[w] = aux_df_wp['hours'].sum()
                    print(f'project "{p}", wp "{w}", total hours "{total_wps[w]}"')
            else:
                # array of sum values for each task
                print('tbd')

        print(projects)

