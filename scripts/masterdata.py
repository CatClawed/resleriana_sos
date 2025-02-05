import csv, json, os
from datetime import datetime

A25_DB = '/shared/Projects/resleriana-db/'

names =     ['ability', 'base_enemy', 'base_character', 'battle_hint', 'battle_mission', 'battle_tool', 'battle_tool_trait', 'character',
             'character_tag', 'dialog', 'effect', 'effect_motion', 'emblem', 'emblem_group', 'emblem_rarity', 'enemy', 'episode', 'equipment_tool',
             'equipment_tool_trait', 'event', 'event_album', 'field_effect', 'gacha', 'illustrator', 'item', 'memoria', 'mission', 'original_title', "photo_background",
             'quest', 'recipe', 'recipe_plan', 'recipe_plan_category', 'recollection_episode', 'recollection_scene', 'research', 'research_effect',
             'research_effect_level', 'research_group', 'reward_set', 'series', 'shop', 'shop_category', 'skill', 'species', 'state_change', 'street_phase', 'timeline_panel', 'trait_color', 'voice_actor']

jsons = {}
languages = ['en', 'zh_cn', 'zh_tw']
languages2 = ['en', 'zh-CN', 'zh-TW']
translated_keys = ['name', 'fullname', 'abbreviation', 'another_name', 'description', 'effect_name', 'acquisition_text', 'popup_text', 'text'] #, 'leader_skill', 'requirements', 'requirement']
# dive deeper and fix: requirement (emblem rarity), requirements (recipe+research ugh), leader_skill (character)

def search(query, ls, field='id'):
    return [element for element in ls if element[field] == query]


def replace_newline(data):
    for entry in data:
        for key in translated_keys:
            if key in entry:
                if isinstance(entry[key], str):
                    entry[key] = entry[key].replace('\n', '\\n')


with open(f'{A25_DB}/resources/Japan/TextAsset/SystemText/SystemText.json') as url:
    data = json.load(url)
    jsons["SystemText"] = data
    replace_newline(data)
for i in range(0, len(languages)):
    with open(f'{A25_DB}/resources/Global/TextAsset/SystemText/SystemText_{languages2[i]}.json') as url:
        data = json.load(url)
        replace_newline(data)
        for entry in jsons["SystemText"]:
            found = search(entry['id'], data)
            if found:
                for key in translated_keys:
                    if key in found[0]:
                        entry[f'{key}_{languages2[i]}'] = found[0][key]

for name in names:
    with open(f'{A25_DB}/data/master/jp/{name}.json') as url:
        data = json.load(url)
        jsons[name] = data
        replace_newline(data)
    for i in range(0, len(languages)):
        with open(f'{A25_DB}/data/master/{languages[i]}/{name}.json') as url:
            data = json.load(url)
            replace_newline(data)
            for entry in jsons[name]:
                found = search(entry['id'], data)
                if found:
                    for key in translated_keys:
                        if key in found[0]:
                            entry[f'{key}_{languages2[i]}'] = found[0][key]

for k, v in jsons.items():
    path = f'{os.path.dirname(os.getcwd())}/csv/masterdata/{k}.csv' if k != "SystemText" else f'{os.path.dirname(os.getcwd())}/csv/{k}.csv'
    with open(path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id']
        for key in translated_keys:
            if key != 'text' or k == 'SystemText':
                if key in v[0]:
                    fieldnames += [key, f'{key}_en', f'{key}_zh-CN', f'{key}_zh-TW']
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
        w.writeheader()
        for line in v:
            w.writerow(line)
