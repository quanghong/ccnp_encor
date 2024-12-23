import os, json

def backup_json(data, file_path):                                                  
    with open(file_path, "w") as ObjFile:
        ObjFile.write(json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True))
        ObjFile.close()

def restore_json(file_path):
    data = {}
    if os.path.isfile(file_path):
        with open(file_path, 'r') as ObjFile:
            dataform = ObjFile.read()
            if dataform:
                data = json.loads(dataform)
            ObjFile.close()
    return data

def create_file(nameFile, pathFile, config):
    x_file = pathFile + nameFile + '.txt'
    fl = open(x_file, 'w')
    fl.write(config)
    fl.close()

def get_list_device_configure(devices_inv, list_configure_order):
    list_configure = []
    for name in list_configure_order:
        for dev in devices_inv:
            if dev['name'] == name:
                list_configure.append(dev)
    return list_configure