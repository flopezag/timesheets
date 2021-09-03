def check_for_subfolders(folder_id, service):
    new_sub_patterns = {}
    folders = service.files().list(q="mimeType='application/vnd.google-apps.folder' and parents in '"+folder_id+"' and trashed = false",fields="nextPageToken, files(id, name)",pageSize=400).execute()
    all_folders = folders.get('files', [])
    all_files = check_for_files(folder_id, service=service)
    n_files = len(all_files)
    n_folders = len(all_folders)
    old_folder_tree = folder_tree
    if n_folders != 0:
        for i, folder in enumerate(all_folders):
            folder_name = folder['name']
            subfolder_pattern = old_folder_tree + '/' + folder_name
            new_pattern = subfolder_pattern
            new_sub_patterns[subfolder_pattern] = folder['id']
            print('New Pattern:', new_pattern)
            all_files = check_for_files(folder['id'], service=service)
            n_files = len(all_files)
            new_folder_tree = new_pattern
            if n_files != 0:
                for file in all_files:
                    file_name = file['name']
                    new_file_tree_pattern = subfolder_pattern + "/" + file_name
                    new_sub_patterns[new_file_tree_pattern] = file['id']
                    print("Files added :", file_name)
            else:
                print('No Files Found')
    else:
        all_files = check_for_files(folder_id)
        n_files = len(all_files)
        if n_files != 0:
            for file in all_files:
                file_name = file['name']
                subfolders[folder_tree + '/'+file_name] = file['id']
                new_file_tree_pattern = subfolder_pattern + "/" + file_name
                new_sub_patterns[new_file_tree_pattern] = file['id']
                print("Files added :", file_name)
    return new_sub_patterns


def check_for_files(folder_id, service):
    other_files = service.files().list(q="mimeType!='application/vnd.google-apps.folder' and parents in '"+folder_id+"' and trashed = false",fields="nextPageToken, files(id, name)",pageSize=400).execute()
    all_other_files = other_files.get('files', [])
    return all_other_files


def get_folder_tree(folder_ids, service, folder_tree):
    sub_folders = check_for_subfolders(folder_ids, service)

    for i, sub_folder_id in enumerate(sub_folders.values()):
        folder_tree = list(sub_folders.keys())[i]
        print('Current Folder Tree : ', folder_tree)
        folder_ids.update(sub_folders)
        print('****************************************Recursive Search Begins**********************************************')
        try:
            get_folder_tree(sub_folder_id, service=service, folder_tree=folder_tree)
        except:
            print('---------------------------------No furtherance----------------------------------------------')
    return folder_ids
