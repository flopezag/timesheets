from googleapiclient.discovery import build
from datetime import datetime, timedelta
from pandas import DataFrame, Timedelta, to_timedelta
from structures import Structure


class Timesheet:
    def __init__(self, credentials):
        # The ID and range of a sample spreadsheet.
        self.SAMPLE_SPREADSHEET_ID = "1pacXhdQ8h_Is9kEM4rNm9raTHRQ8lBAAqQ4TZYQFBgo"
        self.SAMPLE_RANGE_NAME = "Template!B4:N"

        # Google Credentials
        self.credentials = credentials

        self.values = list()
        self.data = list()
        self.total_hours = Timedelta("00:00:00")

        # Metadata information of the sheet
        self.person = ''
        self.month = ''
        self.year = ''
        self.max_working_hours = Timedelta("00:00:00")

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
        final_data = dict()
        df = DataFrame(self.data)

        # Assign the correct name to the columns
        df.columns = ['day', 'code', 'project', 'wp', 'task', 'location', 'start', 'end', 'hours', 'a', 'b', 'c', 'd']

        # Extract a sub-dataframe of the data interested to manage ('project', 'wp', 'task', 'hours')
        df = df[["project", "wp", "task", "hours"]]

        # Convert column "hours" from string to timedelta
        df['hours'] = to_timedelta(df['hours'])

        # Get the unique list of values of the column project
        projects = df.project.unique().tolist()

        print()
        # Calculate the sum of hours per each WP and per each task
        for p in projects:
            mask = df['project'].values == p
            aux_df = df.loc[mask]
            aux_df.columns = ["project", "wp", "task", "hours"]

            # Need to check the column [1](wp) and column [2](task),
            # - Case 1: if [1] is empty then we create an array of 12 values, each per month with the sum of column [3]
            # - Case 2: if [1] has value but [2] is empty, create a list of wps in which each of them is the sum of [3]
            # - Case 3: if [1] and [2] have values, create a list of wps with a list of tasks with the array of sums of [3]
            column1 = aux_df['wp'].values[1]
            column2 = aux_df['task'].values[1]

            if column1 == '':
                # Case 1: array of sum values for project
                total = aux_df['hours'].sum()
                self.total_hours += total
                print(f'project "{p}" total hours "{total}"')
                struct = Structure(data=self)
                c1 = struct.project_without_wp(project=p, total=total)
                final_data.update(c1)

            elif column2 == '':
                # Case 2: array of sum values for each wp
                wps = aux_df.wp.unique().tolist()
                total_wps = dict()
                for w in wps:
                    mask_wp = aux_df['wp'].values == w
                    aux_df_wp = aux_df.loc[mask_wp]
                    total_wps[w] = aux_df_wp['hours'].sum()
                    self.total_hours += total_wps[w]
                    print(f'project "{p}", wp "{w}", total hours "{total_wps[w]}"')

                c2 = struct.project_with_wps_without_tasks(project=p, workpackages=wps, total=total_wps)
                final_data.update(c2)
            else:
                # Case 3: array of sum values for each task
                wps = aux_df.wp.unique().tolist()
                total_wps = dict()
                total_tasks = dict()
                for w in wps:
                    mask_wp = aux_df['wp'].values == w
                    aux_df_wp = aux_df.loc[mask_wp]

                    tasks = aux_df.task.unique().tolist()
                    total_tasks = dict()
                    for t in tasks:
                        mask_task = aux_df_wp['task'].values == t
                        aux_df_task = aux_df_wp.loc[mask_task]
                        total_tasks[t] = aux_df_task['hours'].sum()
                        self.total_hours += total_tasks[t]

                    total_wps[w] = total_tasks
                    print(f'project "{p}", wp "{w}", total hours "{total_wps[w]}"')

                c3 = struct.project_with_wps_with_tasks(project=p, workpackages=wps, tasks=tasks, total=total_tasks)
                final_data.update(c3)

        # Need to check the hours with the expected hours
        if self.total_hours != self.max_working_hours:
            print(f'Error the number of Total Hours "{self.total_hours}" '
                  f'is different from Max Working Hours "{self.max_working_hours}"')
        else:
            print(f'\nTotal hours "{self.total_hours}"')
            print(f'\nData generated: \n{final_data}')

    def metadata_extraction(self):
        """
        Extract the metadata information of the google sheet: Name[0,4], Family Name[1,4], Month[0,8],
        Year[1,8], and Max Working Hours[x,9]
        :return:
        """
        length = len(self.values)
        max_working_hours = length - 74 + 2

        self.person = self.values[1][3] + " " + self.values[0][3]
        self.month = self.values[0][7]
        self.year = self.values[1][7]
        self.max_working_hours = to_timedelta(self.values[max_working_hours][8])
