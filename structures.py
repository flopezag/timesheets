class Structure:
    def __init__(self, data):
        self.data = data
        self.month = {
            'JAN': 0,
            'FEB': 1,
            'MAR': 2,
            'APR': 3,
            'MAY': 4,
            'JUN': 5,
            'JUL': 6,
            'AUG': 7,
            'SEP': 8,
            'OCT': 9,
            'NOV': 10,
            'DEC': 11
        }

    def project_without_wp(self, project, total):
        """
        Generate the dictionary data corresponding to the Case 1
        :param project: The name of the corresponding Project in the Google Sheet
        :param total: The number of hours declared in the corresponding month
        :return:
        """
        temp = dict()
        array = [0] * 12
        ix = self.month[self.data.month]
        array[ix] = total

        temp[project] = {
            self.data.year: {
                self.data.person: array
            }
        }

        print(temp)
        print()
        return temp

    def project_with_wps_without_tasks(self, project, workpackages, total):
        """
        Generate the dictionary data corresponding to the Case 2
        :param project: The name of the corresponding Project in the Google Sheet
        :param total: The number of hours declared in the corresponding month
        :return:
        """
        temp_persona = dict()
        temp = dict()
        ix = self.month[self.data.month]

        for wp in workpackages:
            array = list()
            array = [0] * 12
            array[ix] = total[wp]
            temp_persona[wp] = array

        temp[project] = {
            self.data.year: {
                self.data.person: temp_persona
            }
        }

        print(temp)
        print()
        return temp

    def project_with_wps_with_tasks(self, project, workpackages, tasks, total):
        """
        Generate the dictionary data corresponding to the Case 3
        :param project: The name of the corresponding Project in the Google Sheet
        :param total: The number of hours declared in the corresponding month
        :return:
        """
        temp_persona = dict()
        temp_workpackage = dict()
        temp = dict()
        ix = self.month[self.data.month]

        for wp in workpackages:
            for t in tasks:
                array = list()
                array = [0] * 12
                array[ix] = total[t]
                temp_workpackage[t] = array

            temp_persona[wp] = temp_workpackage

        temp[project] = {
            self.data.year: {
                self.data.person: temp_persona
            }
        }

        print(temp)
        print()
        return temp