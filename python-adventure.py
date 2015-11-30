import re
import json
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)

###Actions
def name_entity(player_data, game_data, options):
    player_data[options["label"]] = raw_input(options["prompt"] + " ")

def add_to_inventory(player_data, game_data, options):
    if "inventory" not in player_data:
        player_data["inventory"] = {}
    if options["item"] not in player_data["inventory"]:
        player_data["inventory"][options["item"]] = 1
    else:
        player_data["inventory"][options["item"]] += 1
    print options["item"] + " added to inventory!\n"

    print "press enter/return \n"
    raw_input()

def view_inventory(player_data, game_data, options):
    if "inventory" in player_data and len(player_data["inventory"].keys()):
        for item in player_data["inventory"].items():
            print str(item[0]) + " x " + str(item[1]) + "\n"
    else:
        print game_data["display"]["inventory_empty"] + "\n"

    print "press enter/return \n"
    raw_input()

actions = {
    "name_entity" : name_entity,
    "add_to_inventory" : add_to_inventory,
    "view_inventory": view_inventory
}
### end of actions

def add_player_data(player_data, string):
    matches = re.search("\{\{(.*?)\}\}", string)
    if(matches):
        default = matches.group(1)
        return add_player_data(
            player_data,
            re.sub(
                matches.group(0),
                player_data[default] if default in player_data else default,
                string))
    else:
        return string

def test_condition(player_data, condition):
    if (re.search("^!", condition)):
        return condition[1:] not in player_data
    else:
        return condition in player_data

def apply_conditions(player_data, string):
    conditional_statement = "\(\((.*?) \? (.*?) \| (.*?)\)\)"
    matches = re.search(conditional_statement, string)

    if(matches):
        conditional_test = matches.group(1)
        if_true_string = matches.group(2)
        if_false_string = matches.group(3)

        replacement_substring = ""
        if conditional_test in player_data:
            replacement_substring = if_true_string
        else:
            replacement_substring = if_false_string

        return apply_conditions(
            player_data,
            re.sub(conditional_statement, replacement_substring, string))
    else:
        return string

def process_string(player_data, string):
    return apply_conditions(player_data, add_player_data(player_data, string))

def filter_choices(player_data, choices):
    def apply_choice_condition(choice):
        if ("condition" in choice):
            return test_condition(player_data, choice["condition"])
        else:
            return True
    return filter(apply_choice_condition, choices)

def process_player_input(player_input, player_data, game_data):
    if player_input == "q":
        print "\n" + game_data["display"]["quit_message"]
        player_data["quitting"] = True
    else:
        player_data["last_choice_was_valid"] = False
        for choice in filter_choices(player_data, player_data["current_room"]["choices"]):
            if player_input == choice["input"]:
                if "action" in choice and choice["action"]["name"] in actions:
                    os.system("clear")
                    actions[choice["action"]["name"]](player_data, game_data, choice["action"]["options"])
                player_data["current_room"] = game_data["scenes"][choice["destination"]]
                player_data["last_choice_was_valid"] = True

def display(player_data, game_data):
    print "\n" + process_string(player_data, player_data["current_room"]["description"]) + "\n"

    for choice in filter_choices(player_data, player_data["current_room"]["choices"]):
        print choice["input"] + ") " + process_string(player_data, choice["description"])

    print "q) quit game\n"

    if player_data.get("last_choice_was_valid"):
        print game_data["display"]["invalid_choice"]

def game_loop(player_data, game_data):
    os.system("clear")

    if "current_room" not in player_data:
        player_data["current_room"] = game_data["scenes"][game_data["scenes"]["first scene name"]]

    display(player_data, game_data)

    process_player_input(raw_input(game_data["display"]["prompt"] + " "), player_data, game_data)

    return not player_data.get("quitting")

with open("python-adventure.game") as game_file:
    game_data = json.load(game_file)
    player_data = {}
    while game_loop(player_data, game_data): pass
