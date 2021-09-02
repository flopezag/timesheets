from pandas import Timedelta


class PrettyPrint:
    def __init__(self):
        pass

    @staticmethod
    def pretty_print(mylist, project):
        """
        Pretty print the PMs of a specific project
        :param mylist: The dictionary data with the information of all projects
        :param project: The specific project to show data
        :return:
        """
        print(project)

        data = mylist[project]
        for year in data:
            print(f'    {year}')
            aux1 = data[year]
            for person in aux1:
                print(f'        {person}')
                aux2 = aux1[person]
                if isinstance(aux2, dict):
                    PrettyPrint.__pprint_dict__(data=aux2)
                elif isinstance(aux2, list):
                    PrettyPrint.__pprint_list__(data=aux2)

    @staticmethod
    def __pprint_dict__(data):
        # Get the first element of the following level to see if it is a list or a dict
        aux = data[list(data.keys())[0]]

        if isinstance(aux, list):
            # We have WPs without tasks
            for wp in data:
                aux3 = ''
                for i in data[wp]:
                    aux3 = PrettyPrint.__get_string__(data=i, content=aux3)

                print(f'            {wp}    {aux3}')
        elif isinstance(aux, dict):
            # The WPs have also tasks...
            aux3 = ''
            t = dict()
            for wp in data:
                print(f'            {wp}')
                for t in data[wp]:
                    aux3 = ''
                    for i in data[wp][t]:
                        aux3 = PrettyPrint.__get_string__(data=i, content=aux3)

                print(f'                {t}    {aux3}')

    @staticmethod
    def __pprint_list__(data):
        # We print the PMs of projects without WPs
        result = ''
        for i in data:
            result = PrettyPrint.__get_string__(data=i, content=result)

        print(f'            {result}')

    @staticmethod
    def __get_string__(data, content):
        if isinstance(data, int):
            content += '0 '
        else:
            # the data is a Timedelta
            h = data.total_seconds() / 3600
            content += f'{h:.3f} '

        return content


if __name__ == '__main__':
    uno = {
        'Maintenance of email lists': {
            '2021': {
                'Fernando López Aguilar': [0, 0, 0, 0, 0, Timedelta('0 days 07:04:00'), 0, 0, 0, 0, 0, 0]
            }
        },
        'Orion in CEF - 3': {
            '2021': {
                'Fernando López Aguilar': {
                    'T04': {
                        'A01': [0, 0, 0, 0, 0, Timedelta('2 days 20:00:00'), 0, 0, 0, 0, 0, 0]
                    }
                }
            }
        },
        'FIWARE4Water': {
            '2021': {
                'Fernando López Aguilar': {
                    'WP2': [0, 0, 0, 0, 0, Timedelta('1 days 06:31:00'), 0, 0, 0, 0, 0, 0],
                    'WP6': [0, 0, 0, 0, 0, Timedelta('0 days 17:21:00'), 0, 0, 0, 0, 0, 0],
                    'WP7': [0, 0, 0, 0, 0, Timedelta('0 days 03:45:00'), 0, 0, 0, 0, 0, 0]
                }
            }
        },
        'INTERSTAT': {
            '2021': {
                'Fernando López Aguilar': {
                    'WP2': {
                        'T2.2': [0, 0, 0, 0, 0, Timedelta('1 days 01:48:00'), 0, 0, 0, 0, 0, 0]
                    }
                }
            }
        },
        'fiware.org support': {
            '2021': {
                'Fernando López Aguilar': [0, 0, 0, 0, 0, Timedelta('0 days 11:03:00'), 0, 0, 0, 0, 0, 0]
            }
        },
        'CEFAT4Cities': {
            '2021': {
                'Fernando López Aguilar': {
                    'WP3': {
                        'T3.5': [0, 0, 0, 0, 0, Timedelta('0 days 06:19:00'), 0, 0, 0, 0, 0, 0]
                    }
                }
            }
        },
        'WeekEnd Day': {
            '2021': {
                'Fernando López Aguilar': [0, 0, 0, 0, 0, Timedelta('0 days 00:00:00'), 0, 0, 0, 0, 0, 0]
            }
        },
        'Quality Assurance': {
            '2021': {
                'Fernando López Aguilar': [0, 0, 0, 0, 0, Timedelta('0 days 06:09:00'), 0, 0, 0, 0, 0, 0]
            }
        },
        'NOT APPLICABLE': {
            '2021': {
                'Fernando López Aguilar': [0, 0, 0, 0, 0, Timedelta('0 days 00:00:00'), 0, 0, 0, 0, 0, 0]
            }
        }
    }

    PrettyPrint.pretty_print(mylist=uno, project='FIWARE4Water')
    PrettyPrint.pretty_print(mylist=uno, project='Maintenance of email lists')
    PrettyPrint.pretty_print(mylist=uno, project='CEFAT4Cities')
