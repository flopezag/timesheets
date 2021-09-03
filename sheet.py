from googleapiclient.discovery import build
from datetime import datetime, timedelta
from pandas import DataFrame, Timedelta, to_timedelta
from structures import Structure
from networkdays import networkdays
from calendar import monthrange


class Timesheet:
    def __init__(self, credentials, sheetid):
        # The ID and range of a sample spreadsheet.
        self.SAMPLE_SPREADSHEET_ID = sheetid
        self.service = build('sheets', 'v4', credentials=credentials)

        # Call the Sheets API
        self.sheet = self.service.spreadsheets()

        # Get the Sheet name
        sheet_metadata = self.sheet.get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID).execute()
        sheetname = sheet_metadata['sheets'][0]['properties']['title']

        # Get sheet version

        self.SAMPLE_RANGE_NAME = sheetname + "!" + "B2:N"

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

        # Calculate correction last row data
        self.row_correction = 0
        correction = {
            "v. 20210427": 1,
            "v. 20210114": 2,
            "v. 20201217": 2,

            "v. 20201130": 0,
            "v. 20200527": 0,
            "v. 20190725": 0
        }

        sheet_range = {
            "v. 20210427": "!B2:N",
            "v. 20210114": "!B2:N",
            "v. 20201217": "!B2:N",

            "v. 20201130": "!A1:N",
            "v. 20200527": "!A1:N",
            "v. 20190725": "!A1:N"
        }

        result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                         range=sheetname + "!A:N").execute()
        version = result.get('values', [])
        if len(version[0]) == 0:
            version = version[1][1]
        else:
            version = version[0][13]

        self.SAMPLE_RANGE_NAME = sheetname + sheet_range[version]
        self.row_correction = correction[version]
        self.lastday = int()

        position_project_description = {
            "v. 20210427": 2,
            "v. 20210114": 2,
            "v. 20201217": 2,

            "v. 20201130": 3,
            "v. 20200527": 3,
            "v. 20190725": 3
        }

        position_start_hours = {
            "v. 20210427": 6,
            "v. 20210114": 6,
            "v. 20201217": 6,

            "v. 20201130": 7,
            "v. 20200527": 7,
            "v. 20190725": 7
        }

        self.position_project_description = position_project_description[version]
        self.position_start_hours = position_start_hours[version]
        self.position_end_hours = self.position_start_hours + 1
        self.position_total_hours = self.position_end_hours + 1

    def get_data_from_timesheet(self):
        """Shows basic usage of the Sheets API.
        Prints values from a sample spreadsheet.
        """
        # Request the data
        result = self.sheet.values().get(spreadsheetId=self.SAMPLE_SPREADSHEET_ID,
                                         range=self.SAMPLE_RANGE_NAME).execute()

        values = result.get('values', [])

        self.service.close()
        self.values = values

    def data_analysis_validation(self):
        df = DataFrame(self.values)
        # last_data_row = df.index[df[6] == 'max working hours'].tolist()[0]
        last_data_row = max(df.index[df[0] == str(self.lastday)].tolist())
        first_data_row = min(df.index[df[0] == '1'].tolist()) + 1

        # We substrate 2 lines to this due the the max working hours and the sum
        # TODO: This only applies to the last versions of the template...
        # last_data_row -= self.row_correction
        aux = self.values[first_data_row:last_data_row + 1]
        # last_day = int(aux[len(aux) - 1][0])

        # Get the days that are weekends
        weekend = list(filter(lambda x: x[self.position_project_description] == 'WeekEnd Day', aux))
        weekend = list(map(lambda x: int(x[0]), weekend))

        for i in range(1, self.lastday):
            # Filter list for day and extract only the corresponding columns of hours
            # and the day is not weekend
            temp1 = list(
                filter(
                    lambda x: x[0] in [str(i)] and x[self.position_project_description] not in
                              ['WeekEnd Day', 'Bank Holiday', 'NOT APPLICABLE']
                    , aux
                )
            )

            # Check if the temp1 is empty, it means that we have a WeekEnd Day or Bank Holiday
            # Therefore we do not need to validate the data
            if len(temp1) != 0:
                temp1 = list(map(lambda x: [x[self.position_start_hours], x[self.position_end_hours], x[self.position_total_hours]], temp1))

                # Check difference between "End h" and "Start h"
                list(map(lambda x: self.__validate_diff_hours__(day=i, hours=x), temp1))

                # Check number hours per day equal to 8
                temp1 = list(map(lambda x: x[2], temp1))
                self.__validate_sum_hours_day__(day=i, hours=temp1, weekend=weekend)

        self.data = aux

    @staticmethod
    def __validate_diff_hours__(day, hours):
        # we specify the input and the format...
        t = datetime.strptime(hours[2], "%H:%M:%S")
        # ...and use datetime's hour, min and sec properties to build a timedelta
        delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)

        diff = datetime.strptime(hours[1], '%H:%M') - datetime.strptime(hours[0], '%H:%M')

        if diff != delta:
            if diff - delta == timedelta(minutes=45):
                print(f'WARNING, the difference is not correct on day {day}, hours {hours}, diff {diff - delta}')
            else:
                print(f'ERROR, the difference is not correct on day {day}, hours {hours}, diff {diff - delta}')

    @staticmethod
    def __validate_sum_hours_day__(day, hours, weekend):
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
        if self.position_project_description == 2:
            df.columns = ['day', 'code', 'project', 'wp', 'task', 'location', 'start', 'end', 'hours', 'a', 'b', 'c', 'd']
        elif self.position_project_description == 3:
            df.columns = ['day', 'code', 'e', 'project', 'wp', 'task', 'location', 'start', 'end', 'hours', 'a', 'b', 'c', 'd']

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
            # aux_df.columns = ["project", "wp", "task", "hours"]

            # Need to check the column [1](wp) and column [2](task),
            # - Case 1: if [1] is empty then we create an array of 12 values, each per month
            #           with the sum of column [3]
            # - Case 2: if [1] has value but [2] is empty, create a list of wps in which each
            #           of them is the sum of [3]
            # - Case 3: if [1] and [2] have values, create a list of wps with a list of tasks
            #           with the array of sums of [3]
            column1 = aux_df['wp'].values[0]
            column2 = aux_df['task'].values[0]

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

                struct = Structure(data=self)
                c2 = struct.project_with_wps_without_tasks(project=p, workpackages=wps, total=total_wps)
                final_data.update(c2)
            else:
                # Case 3: array of sum values for each task
                wps = aux_df.wp.unique().tolist()
                total_wps = dict()
                total_tasks = dict()
                tasks = list()
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

                struct = Structure(data=self)
                c3 = struct.project_with_wps_with_tasks(project=p, workpackages=wps, tasks=tasks, total=total_tasks)
                final_data.update(c3)

        # Need to check the hours with the expected hours
        if self.total_hours != self.max_working_hours:
            print(f'Error the number of Total Hours "{self.total_hours}" '
                  f'is different from Max Working Hours "{self.max_working_hours}"')

            return {}
        else:
            print(f'\nTotal hours "{self.total_hours}"')
            print(f'\nData generated: \n{final_data}')

            return final_data

    def metadata_extraction(self):
        """
        Extract the metadata information of the google sheet: Name[0,4], Family Name[1,4], Month[0,8],
        Year[1,8], and Max Working Hours[x,9]
        :return:
        """
        df = DataFrame(self.values)
        max_working_hours = df.index[df[6] == 'max working hours'].tolist()

        if len(max_working_hours) != 0:
            max_working_hours = max_working_hours[0]

            self.person = self.values[3][3] + " " + self.values[2][3]
            self.month = self.values[2][7]
            self.year = self.values[3][7]
            #self.max_working_hours = to_timedelta(self.values[max_working_hours][8])
        else:
            # TODO: Files from 2020 and before, have no max working hours
            self.person = self.values[2][4] + " " + self.values[1][4]
            self.month = self.values[1][8]
            self.year = self.values[2][8]

        self.calculate_max_hours_worked()

    def calculate_max_hours_worked(self):
        # CALCULATE MAX WORKING HOURS
        s = Structure(data=dict())
        month = s.get_month_number(string_month=self.month) + 1

        start_date = datetime(int(self.year), month, 1)
        _, self.lastday = monthrange(int(self.year), month)
        end_date = datetime(int(self.year), month, self.lastday)

        days = networkdays.Networkdays(start_date, end_date)

        hours = str(len(days.networkdays()) * 8) + ":00:00"
        print(hours)
        self.max_working_hours = to_timedelta(hours)
        print(self.max_working_hours)
