import re
import json
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)

def name_entity(saved_data, options):
    saved_data[options['label']] = raw_input(options['prompt'] + " ")

def add_to_inventory(saved_data, options):
    if 'inventory' not in saved_data:
        saved_data['inventory'] = {}
    if options['item'] not in saved_data['inventory']:
        saved_data['inventory'][options['item']] = 1
    else:
        saved_data['inventory'][options['item']] += 1

actions = {'name_entity' : name_entity, 'add_to_inventory' : add_to_inventory}

def add_saved_data(saved_data, string):
    matches = re.search("\{\{(.*?)\}\}", string)
    if(matches):
        default = matches.group(1)
        return add_saved_data(
            saved_data,
            re.sub(
                matches.group(0),
                saved_data[default] if default in saved_data else default,
                string))
    else:
        return string

def test_condition(saved_data, condition):
    if (re.search('^!', condition)):
        return condition[1:] not in saved_data
    else:
        return condition in saved_data

def apply_conditions(saved_data, string):
    conditional_statement = "\(\((.*?) \? (.*?) \| (.*?)\)\)"
    matches = re.search(conditional_statement, string)

    if(matches):
        conditional_test = matches.group(1)
        if_true_string = matches.group(2)
        if_false_string = matches.group(3)

        replacement_substring = ''
        if conditional_test in saved_data:
            replacement_substring = if_true_string
        else:
            replacement_substring = if_false_string

        return apply_conditions(
            saved_data,
            re.sub(conditional_statement, replacement_substring, string))
    else:
        return string

def process_string(saved_data, string):
    return apply_conditions(saved_data, add_saved_data(saved_data, string))

def filter_choices(saved_data, choices):
    def apply_choice_condition(choice):
        if ('condition' in choice):
            return test_condition(saved_data, choice['condition'])
        else:
            return True
    return filter(apply_choice_condition, choices)

def process_player_input(player_input, saved_data, game_data):
    if player_input == "q":
        print "Hope you had fun!"
        return False
    else:
        valid_choice = False

        for choice in filter_choices(saved_data, saved_data["current_room"]["choices"]):
            if player_input == choice["input"]:
                if "action" in choice and choice["action"]["name"] in actions:
                    actions[choice["action"]["name"]](saved_data, choice["action"]["options"])
                saved_data["current_room"] = game_data['scenes'][choice["destination"]]
                valid_choice = True

        if not valid_choice:
            print "I have no idea what you're talking about."
    return True

def display(saved_data, game_data):
    print "\n" + process_string(saved_data, saved_data["current_room"]["description"]) + "\n"

    for choice in filter_choices(saved_data, saved_data["current_room"]["choices"]):
        print choice["input"] + ") " + process_string(saved_data, choice["description"])

    print "q) quit game\n"

def game_loop(saved_data, game_data):
    os.system('clear')

    if "current_room" not in saved_data:
        saved_data["current_room"] = game_data['scenes'][game_data['scenes']['first scene name']]

    display(saved_data, game_data)

    return process_player_input(raw_input("What will you do? "), saved_data, game_data)

with open('python-adventure.game') as game_file:
    game_data = json.load(game_file)
    saved_data = {}
    while game_loop(saved_data, game_data): pass
