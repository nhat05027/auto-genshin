#%% setup

import genshinstats as gs
import os
import re


#%% login into genshin

GAME_UID = int(os.environ.get("GAME_UID"))
hoyolab_uid = int(os.environ.get("LTUID"))
token = (os.environ.get("LTOKEN"))
gs.set_cookie(ltuid=hoyolab_uid, ltoken=token)

#%% Claim daily rewards

print("[Daily Reward] ", end="")
daily_reward = gs.claim_daily_reward()
if daily_reward is not None:
    print(f"Claimed: {daily_reward['cnt']} x {daily_reward['name']}")
else:
    if bool(os.environ.get("DAILY_OR_ERR")):
        print("Could not claim daily reward")


#%% get data

user_info = gs.get_user_stats(GAME_UID)
characters = gs.get_characters(GAME_UID)
spiral_abyss = gs.get_spiral_abyss(GAME_UID)
(daily_reward_info_is_sign, daily_reward_info_total_sign_day) = gs.get_daily_reward_info()

record_card = gs.get_record_card(hoyolab_uid)
(user_nickname, user_level) = (record_card["nickname"], record_card["level"])

if daily_reward is None:
    monthly_reward = gs.get_monthly_rewards()
    daily_reward = monthly_reward[daily_reward_info_total_sign_day - 1]


#%% create readme from template

import io
import pathlib

root = pathlib.Path(__file__).parent.resolve()
readme_template = root / "README_template.md"
data = readme_template.open().read()



#%% other stats

import datetime
data = data.replace("replace_this_with_check_time", datetime.datetime.utcnow().strftime("%d.%m.%Y %H:%M:%S UTC"))

# daily reward
data = data.replace(f"replace_this_with_daily_reward_name", str(daily_reward['name']))
data = data.replace(f"replace_this_with_daily_reward_icon", str(daily_reward['icon']))
data = data.replace(f"replace_this_with_daily_reward_count", str(daily_reward['cnt']))

# stats filling
data = data.replace(f"replace_this_with_nickname", str(user_nickname))
data = data.replace(f"replace_this_with_ar", str(user_level))
data = data.replace(f"replace_this_with_reward_info_total_sign_day", str(daily_reward_info_total_sign_day))
data = data.replace(f"replace_this_with_reward_info_is_sign", str(daily_reward_info_is_sign))

# exploration filling
offset = 0
while True:
    try:
        template_start_str = "replace_this_with_explorations_template_string$$$"
        start_index = data.index(template_start_str, offset)
    except ValueError as e:
        break

    try:
        end_index = data.index("$$$", start_index + len(template_start_str))
    except ValueError as e:
        print("[ERROR] You forgot to enclose explorations template string!")
        raise

    template_string = data[start_index + len(template_start_str): end_index]

    filled_templates = ""

    for location in user_info["explorations"]:
        filled_template = template_string
        for key, value in location.items():
            filled_template = filled_template.replace(f"replace_this_with_exploration_{key}", str(value))
        filled_templates += filled_template

    data = data.replace(template_start_str + template_string + "$$$", filled_templates)

    offset = start_index


# abyss stats filling
for key, value in spiral_abyss["stats"].items():
    data = data.replace(f"replace_this_with_abyss_{key}", str(value))

# abyss strongest strike
if len(spiral_abyss["character_ranks"].get("strongest_strike")) != 0:
    for key, value in spiral_abyss["character_ranks"].get("strongest_strike")[0].items():
        data = data.replace(f"replace_this_with_abyss_strongest_strike_{key}", str(value))
else:
    data = re.sub(r"replace_this_with_abyss_strongest_strike_[a-z]+", "no strongest strike this seasson", data)

# abyss most kills
if len(spiral_abyss["character_ranks"].get("most_kills")) != 0:
    for key, value in spiral_abyss["character_ranks"].get("most_kills")[0].items():
        data = data.replace(f"replace_this_with_abyss_most_kills_{key}", str(value))
else:
    data = re.sub(r"replace_this_with_abyss_most_kills_[a-z]+", "no most kills this seasson", data)

# abyss most bursts used
if len(spiral_abyss["character_ranks"].get("most_bursts_used")) != 0:
    for key, value in spiral_abyss["character_ranks"].get("most_bursts_used")[0].items():
        data = data.replace(f"replace_this_with_abyss_most_bursts_used_{key}", str(value))
else:
    data = re.sub(r"replace_this_with_abyss_most_bursts_used_[a-z]+", "no most bursts used this seasson", data)

# abyss most damage taken
if len(spiral_abyss["character_ranks"].get("most_damage_taken")) != 0:
    for key, value in spiral_abyss["character_ranks"].get("most_damage_taken")[0].items():
        data = data.replace(f"replace_this_with_abyss_most_damage_taken_{key}", str(value))
else:
    data = re.sub(r"replace_this_with_abyss_most_damage_taken_[a-z]+", "no most damage taken this seasson", data)

# abyss most skills used
if len(spiral_abyss["character_ranks"].get("most_skills_used")) != 0:
    for key, value in spiral_abyss["character_ranks"].get("most_skills_used")[0].items():
        data = data.replace(f"replace_this_with_abyss_most_skills_used_{key}", str(value))
else:
    data = re.sub(r"replace_this_with_abyss_most_skills_used_[a-z]+", "no most skills used this seasson", data)


# characters
offset = 0
while True:
    try:
        template_start_str = "replace_this_with_characters_template_string$$$"
        start_index = data.index(template_start_str, offset)
    except ValueError as e:
        break

    try:
        end_index = data.index("$$$", start_index + len(template_start_str))
    except ValueError as e:
        print("[ERROR] You forgot to enclose characters template string!")
        raise

    template_string = data[start_index + len(template_start_str): end_index]

    filled_templates = ""

    characters.sort(key=lambda x: (int(x["rarity"]), int(x["level"]), int(x["constellation"]) ,int(x["friendship"])), reverse=True)

    for character in characters:
        filled_template = template_string
        for key, value in character.items():
            if key == "weapon":
                for key, value in value.items():
                    filled_template = filled_template.replace(f"replace_this_with_character_weapon_{key}", str(value))
            elif key == "artifacts":
                sets = [set_piece.get("set").get("name") for set_piece in value]
                sets = [f"{sets.count(x)} x {x}" for x in set(sets)]
                sets.sort(reverse=True)
                sets = "<br>".join(sets)
                filled_template = filled_template.replace("replace_this_with_character_artifact_sets", sets)
            elif key == "constellations":
                continue
            elif key == "outfits":
                outfits = [outfit.get("name") for outfit in value]
                outfits.sort()
                outfits = "<br>".join(outfits)
                filled_template = filled_template.replace("replace_this_with_character_outfits", outfits)
            else:
                filled_template = filled_template.replace(f"replace_this_with_character_{key}", str(value))
        filled_templates += filled_template

    data = data.replace(template_start_str + template_string + "$$$", filled_templates)

    offset = start_index

# stats filling
for key, value in user_info["stats"].items():
    data = data.replace(f"replace_this_with_{key}", str(value))

readme = root / "README.md"
io.open(readme, "w", newline="\n").write(data)


#%% Check for new codes

import requests
from bs4 import BeautifulSoup

res = requests.get("https://www.pockettactics.com/genshin-impact/codes")
soup = BeautifulSoup(res.text, 'html.parser')

active_codes = [code.text.strip() for code in soup.find("div", {"class":"entry-content"}).find("ul").findAll("strong")]

codes_file = root / "codes.txt"
used_codes = codes_file.open().read().split("\n")
new_codes = list(filter(lambda x: x not in used_codes and x != "", active_codes))


#%% Redeem new codes

import time

print("[Code redeem] ", end="")
failed_codes = []
for code in new_codes[:-1]:
    try:
        gs.redeem_code(code, GAME_UID)
    except Exception as e:
        failed_codes.append(code)
    time.sleep(5.2)
if len(new_codes) != 0:
    try:
        gs.redeem_code(new_codes[-1], GAME_UID)
    except Exception as e:
        failed_codes.append(new_codes[-1])

redeemed_codes = list(filter(lambda x: x not in failed_codes, new_codes))
if len(redeemed_codes) != 0:
    print("Redeemed " + str(len(redeemed_codes)) + " new codes: " + ", ".join(redeemed_codes))
else:
    print("No new codes found")


#%% Add new codes to used codes

used_codes.extend(new_codes)
io.open(codes_file, "w", newline="\n").write("\n".join(used_codes))

#%%
