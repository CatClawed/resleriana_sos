import UnityPy
import os, json, re, struct, csv

def unpack_text(source_folder : str, destination_folder : str):
    # iterate over all files in source folder
    events = {}
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            # generate file_path
            file_path = os.path.join(root, file_name)
            # load that file via UnityPy.load
            env = UnityPy.load(file_path)

            for obj in env.objects:
                if obj.type.name in ["TextAsset"]:
                    data = obj.read()


                    if ("TalkEvent" in data.m_Name or "Date_" in data.m_Name or "SeasonalTalkEvent" in data.m_Name or "Atelier_Talk" in data.m_Name) and data.m_Script != '':
                        thing = data.m_Script.encode('utf-8', 'surrogateescape')
                        index = thing.find(b'\x30\xd2\xb1\x17')
                        key = 'jp'
                        event_name = data.m_Name
                        if "_en" == data.m_Name[-3:]:
                            key = 'en'
                            event_name = data.m_Name[:-3]
                        elif "-TW" == data.m_Name[-3:]:
                            key = 'zh-TW'
                            event_name = data.m_Name[:-6]
                        elif "-CN" == data.m_Name[-3:]:
                            key = 'zh-CN'
                            event_name = data.m_Name[:-6]

                        while index < len(thing) - 4 and index > -1:
                            index += 4
                            id = struct.unpack('<I', thing[index:index+4])[0]
                            try:
                                event = events[event_name]
                            except:
                                event = {}
                                events[event_name] = event
                            try:
                                dialog = event[id]
                            except:
                                dialog = {}
                                event[id] = dialog
                            index += 4
                            length1 = struct.unpack('<I', thing[index:index+4])[0]
                            index += 4
                            dialog[f'name_{key}'] = thing[index:index+length1].decode('utf8')
                            index += length1
                            length2 = struct.unpack('<I', thing[index:index+4])[0]
                            index += 4
                            if length2 > 0:
                                dialog['romanized'] = thing[index:index+length2].decode('utf8')
                            index += length2 + 8
                            line_length= struct.unpack('<I', thing[index:index+4])[0]
                            index += 4
                            dialog[f'text_{key}'] = thing[index:index+line_length].decode('utf8')
                            if dialog[f'text_{key}'] == '':
                                print('Warning!', data.m_Name)
                            index += line_length

                            # idk this crap prolly don't do much
                            if "CityTalkEvent" in data.m_Name and "main" not in data.m_Name:
                                index = thing.find(b'\x3F\x50\x3F\x2E', index)
                            if "CityTalkEvent" in data.m_Name and "main" in data.m_Name:
                                index = thing.find(b'\x3F\x4F\x3F\x18', index)
                            else:
                                index = thing.find(b'\x9E\x50\x82\x2E', index)

                        try:
                            assert(events[event_name] != {})
                        except:
                            print("Error", data.m_Name)
                            path = os.path.join(destination_folder, f"{data.m_Name}.txt")
                            with open(path, "w") as f:
                                f.write(data.m_Script.encode('utf-8', 'replace').decode('utf8'))

    for k, v in events.items():
        path = os.path.join(destination_folder, f"{k}.json")
        with open(path, "w") as f:
            f.write(json.dumps(v, ensure_ascii=False))
        path = os.path.join(destination_folder, f"{k}.csv")
        with open(path, 'w') as csvfile:
            fieldnames = ['romanized', 'name_jp', 'text_jp', 'name_en', 'text_en', 'name_zh-CN', 'text_zh-CN', 'name_zh-TW', 'text_zh-TW']
            writer = csv.DictWriter(csvfile, delimiter="\t", fieldnames=fieldnames)
            writer.writeheader()
            for k2, v2 in v.items():
                writer.writerow(v2)

unpack_text('gbl','gbl_text')
