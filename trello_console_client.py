import requests, sys


# Fill the gaps
auth_params = {
    'key': '___YOUR_KEY___',
    'token': '___YOUR_TOKEN___'
}

base_url = 'https://api.trello.com/1/{}'
board_id = '___YOUR_BOARD_ID___' # for example UhfndmK in https://api.trello.com/1/boards/UhfndmK/lists


def read():
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    for column in column_data:
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(f"{column['name']}: number of tasks - {len(task_data)}")
        if not task_data:
            print('\t' + 'Empty\n')
            continue
        for task in task_data:
            print('\t' + task['name'] + '\n')


def create_column(name):
    name = name_handler(name)
    response = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
    board = response['id']
    requests.post(base_url.format('lists'), data={'name': name, 'idBoard': board, **auth_params})
    print('Сolumn has been created.')


def create_list(name, column_name):
    name = name_handler(name)
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    tasks_list = []

    for column in column_data:
        if column['name'] == column_name:
            tasks_list.append({
                'name': column['name'],
                'id': column['id']
            })

    if len(tasks_list) == 1:
        requests.post(base_url.format('cards'), data = {'name': name, 'idList': tasks_list[0]['id'], **auth_params})
        print('Task has been added.')
    elif len(tasks_list) > 1:
        counter = 0
        print('All lists with the same name:')
        
        for task in tasks_list:
            counter += 1
            print(f"{counter} - List: {task['name']} with ID: {task['id']}")
        user_input = int(input('Select the list number, where you want to add a new task:\n'))
        while user_input not in range(1, len(tasks_list) + 1):
            user_input = int(input('There is no list with this number, please select a correct number:\n'))
        requests.post(base_url.format('cards'), data = {'name': name, 'idList': tasks_list[user_input - 1]['id'], **auth_params})
        print('Task has been added.')
    else:
        create_list(column_name)
        column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
        
        for column in column_data:
            if column['name'] == column_name:
                requests.post(base_url.format('cards'), data = {'name': name, 'idList': column['id'], **auth_params})
        print('Task has been added.')


def name_handler(name, component='list'):
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    lists = []
    tasks = []

    for column in column_data:
        if column['name'] == name:
            lists.append({
                'name': column['name'],
                'id': column['id']
            })

        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()

        for task in task_data:
            if task['name'] == name:
                tasks.append({
                    'name': task['name'],
                    'id': task['id'],
                    'list': column['name']
                })

    if (component == 'list') and len(lists) >= 1:
        print('Lists with the same name already is:')
        counter = 0

        for list_ in lists:
            counter += 1
            print(f"\t{counter} - Name: {list_['name']}. ID: {list_['id']}")
        user_input = int(input('Enter number:\n1 - If you want create list with the same name.\n2 - If you want enter enother name.\n'))

        while user_input not in range(1, 3):
            user_input = int(input('Incorrect number, please try again!\n'))
        if user_input == 1:
            return name
        elif user_input == 2:
            name = input('Enter new name:\n')
            return name

    elif (component == 'task') and len(tasks) >= 1:
        print('Tasks with the same name already is:')
        counter = 0

        for task in tasks:
            counter += 1
            print(f"\t{counter} - Name: {task['name']}. List: {task['list']}. ID: {task['id']}.")
        user_input = int(input('Enter number:\n1 - If you want create task with the same name.\n2 - If you want enter enother name.\n'))

        while user_input not in range(1, 3):
            user_input = int(input('Incorrect number, please try again!\n'))
        if user_input == 1:
            return name
        elif user_input == 2:
            name = input('Enter new name:\n')
            return  name
    
    return name


def move(name, column_name):
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    
    tasks_list = []

    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                tasks_list.append({
                    'id': task['id'],
                    'name': task['name'],
                    'list_name': column['name']
                })

    if len(tasks_list) > 1:
        task_id = select_task(tasks_list)
    else:
        task_id = tasks_list[0]['id']
    column_list = []
    
    for column in column_data:
        if column['name'] == column_name:
            column_list.append({
                'name': column['name'],
                'id': column['id']
            })
    
    if len(column_list) > 1:
        print('The lists with the same name:')
        counter = 0

        for column in column_list:
            counter += 1
            print(f"{counter} - Name: {column['name']}. ID: {column['id']}")
        user_input = int(input('Select number of list, where do you want move the task:\n'))

        while user_input not in range(1, len(column_list) + 1):
            user_input = int(input('Incorrect list number. Try again:\n'))
        requests.put(base_url.format('cards') + '/' + task_id + '/idList', data = {'value': column_list[user_input -1]['id'], **auth_params})
        print('Task has been moved.')
    elif len(column_list) == 1:
        requests.put(base_url.format('cards') + '/' + task_id + '/idList', data = {'value': column_list[0]['id'], **auth_params})
        print('Task has been moved.')
    else:
        print('List with this name is not exist.')


def select_task(data):
    counter = 0
    for task in data:
        counter += 1
        print(f"{counter} - Task {task['name']}\n   from the {task['list_name']} list\n   with id - {task['id']}")
    number_of_task = int(input('Select the number of task, that you want to move:\n '))
    return data[number_of_task - 1]['id']
    

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create_column':
        create_column(sys.argv[2])
    elif sys.argv[1] == 'create_list':
        create_list(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
