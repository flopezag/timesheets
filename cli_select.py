
def select_from_dict(options, name):
    index = 0
    index_valid_list = list()
    selected = 0
    print(f'Select a {name}:')

    for opt in options:
        index = index + 1
        index_valid_list.extend([options[opt]])
        print(str(index) + ') ' + opt)

    input_valid = False

    while not input_valid:
        input_raw = input(name + ': ')

        if input_raw.isdigit() is False:
            print(f'Please select a valid {name} number')
            continue

        input_number = int(input_raw) - 1

        if -1 < input_number < len(index_valid_list):
            selected = index_valid_list[input_number]
            print(f'Selected {name} selected')
            input_valid = True
            break
        else:
            print(f'Please select a valid {name} number')

    return selected


if __name__ == '__main__':
    options = dict()

    options['Yes'] = 'yes'
    options['No'] = 'no'

    # Let user select a month
    option = select_from_dict(options=options, name='option')
    print(option)
