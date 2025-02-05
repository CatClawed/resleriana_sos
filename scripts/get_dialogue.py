# fetches text from resleriana-db
import json, csv, os, re

A25_DB = '/shared/Projects/resleriana-db/resources'
dialog = "TextAsset/Dialogue"

events = {}
folders = ["SeasonalTalkEvent", "LegendEvent", "Date", "TalkEvent"]
folders_jp = ["CharacterEvent", "SeasonalEvent"]
folders_gbl = ["Atelier_Talk", "CityTalkEvent"]

for folder in folders + folders_jp:
    for file in os.listdir(f'{A25_DB}/Japan/{dialog}/{folder}'):
        with open(f'{A25_DB}/Japan/{dialog}/{folder}/{file}') as f:
            events[file[:-5]] = json.load(f)
            for line in events[file[:-5]]:
                line["file"]=file[:-5]
                line["text"]=line["text"].replace('\n', '\\n')

for folder in folders_gbl:
    for file in os.listdir(f'{A25_DB}/Global/{dialog}/{folder}'):
        with open(f'{A25_DB}/Global/{dialog}/{folder}/{file}') as f:
            if '_en' in file or '_zh-CN' in file or '_zh-TW' in file:
                lang_index = file.rfind('_')
                lang = file[lang_index+1:-5]
                file = file[:lang_index]
            else:
                continue
            data = json.load(f)
            for line in data:
                for key in ["localized_name", "text"]:
                    line[f"{key}_{lang}"] = line[key].replace('\n', '\\n')
                    del line[key]
                line["file"]=file
            try:
                event = events[file]
            except:
                events[file] = data
                continue
            if len(data) == len(event) or len(data) > len(event):
                for i in range(0,len(event)):
                    event[i] = event[i] | data[i]
                if len(data) > len(event):
                    for i in range(len(event), len(data)):
                        event.append(data[i])
            elif len(data) < len(event):
                for i in range(0,len(data)):
                    event[i] = event[i] | data[i]

for folder in folders:
    for file in os.listdir(f'{A25_DB}/Global/{dialog}/{folder}'):
        with open(f'{A25_DB}/Global/{dialog}/{folder}/{file}') as f:
            if '_en' in file or '_zh-CN' in file or '_zh-TW' in file:
                lang_index = file.rfind('_')
                lang = file[lang_index+1:-5]
                file = file[:lang_index]
            else:
                continue
            data = json.load(f)
            event = events[file]
            for line in data:
                for key in ["localized_name", "text"]:
                    line[f"{key}_{lang}"] = line[key].replace('\n', '\\n')
                    del line[key]
            if len(data) == len(event) or len(data) > len(event):
                for i in range(0,len(event)):
                    event[i] = event[i] | data[i]
                if len(data) > len(event):
                    for i in range(len(event), len(data)):
                        event.append(data[i])
            elif len(data) < len(event):
                for i in range(0,len(data)):
                    event[i] = event[i] | data[i]

merged = {}
for folder in folders_gbl + folders_jp + folders:
    merged[folder] = {}


for k, v in sorted(events.items()):
    merged_name = None
    if re.search("^Atelier_Talk", k):
        merged_name = "Atelier_Talk"
        folder = "Atelier_Talk"
    elif re.search("^CityTalkEvent", k):
        merged_name = "CityTalkEvent"
        folder = "CityTalkEvent"
    elif re.search("^CharacterEvent", k):
        split = k.split('_')
        merged_name = f'{split[0]}_{split[1]}_{split[2]}'
        folder = "CharacterEvent"
    elif re.search("^SeasonalEvent", k):
        split = k.split('_')
        merged_name = f'{split[0]}_{split[1]}'
        folder = "SeasonalEvent"
    elif re.search("^SeasonalTalkEvent", k):
        split = k.split('_')
        merged_name = f'{split[0]}_{split[1]}_{split[2]}' if len(split[2]) == 2 else f'{split[0]}_{split[1]}'
        folder = "SeasonalTalkEvent"
    elif re.search("^LegendEvent", k):
        split = k.split('_')
        merged_name = f'{split[0]}_{split[1]}'
        folder = "LegendEvent"
    elif re.search("^TalkEvent", k):
        split = k.split('_')
        merged_name = f'{split[0]}_{split[1]}'
        folder = "TalkEvent"
    elif re.search("^Date", k): #ugh
        split = k.split('_')
        if 'MCHARA' in k or 'VILLAIN' in k:
            merged_name = f'{split[1]}_{split[2]}' if len(split) == 4 else f'{split[1]}_{split[2]}_{split[3]}'
        else:
            merged_name = f'{split[1]}' if len(split) == 3 else f'{split[1]}_{split[2]}'
        folder = "Date"

    if merged_name:
        try:
            event = merged[folder][merged_name]
        except:
            event = []
            merged[folder][merged_name] = event
        event += v

for k, v in merged.items():
    for k2, v2 in v.items():
        with open(f'{os.path.dirname(os.getcwd())}/csv/{k}/{k2}.csv', 'w', newline='', encoding='utf-8') as f:
            keys = ['file', 'id', 'romanized_name', 'localized_name', 'text', 'localized_name_en', 'text_en', 'localized_name_zh-CN', 'text_zh-CN', 'localized_name_zh-TW', 'text_zh-TW']
            # model_path_hash,voice_file,still_path_hash,speech_balloon_type_id
            w = csv.DictWriter(f, fieldnames=keys, delimiter='\t', extrasaction='ignore')
            w.writeheader()
            for line in v2:
                w.writerow(line)

