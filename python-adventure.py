import re
import json

def name_entity(saved_data, options):
    saved_data[options['label']] = raw_input(options['prompt'] + " ")

def add_to_inventory(saved_data, options):
    if options['item'] in saved_data['inventory']:
        saved_data['inventory'][options['item']] += 1
    else:
        saved_data['inventory'][options['item']] = 1

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

#TODO should grab this from a .save file
saved_data = {}

actions['name_entity'](saved_data, {"prompt" : "What's your name?", "label" : "player name"})

with open('python-adventure.game') as game_file:    
    game_data = json.load(game_file)

scenes = game_data['scenes']

current_room = scenes["one-room house"]

player_input = ""
while player_input != "q":
    print "\n" + apply_conditions(saved_data, add_saved_data(saved_data, current_room["description"])) + "\n"

    for choice in current_room["choices"]:
        print choice["input"] + ") " + add_saved_data(saved_data, choice["description"])
    print "q) quit game\n"

    player_input = raw_input("What will you do? ")

    if player_input == "q":
        print "Hope you had fun!"
    else:
        valid_choice = False

        for choice in current_room["choices"]:
            if player_input == choice["input"]:
                if "action" in choice and choice["action"]["name"] in actions:
                    actions[choice["action"]["name"]](saved_data, choice["action"]["options"])
                current_room = scenes[choice["destination"]]
                valid_choice = True

        if not valid_choice:
            print "I have no idea what you're talking about."
