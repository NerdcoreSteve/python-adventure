import re
import json
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)

#TODO should only pass functions parts of the model that they actually need

#TODO feels like actions should be in a separate module, which is kinda packaged
#     with the game file. Maybe a base module loaded by all games too.
#TODO actions should be a dict of dicts, each sub_dict has view and update functions
#     maybe update looks to see what state it's in and calls the appropriate update function.
#     same for view
#     this is a lot like the enum thing in Elm.
###Actions
def name_entity(model, options):
    #TODO should not be top level?
    model["game"][options["label"]] = raw_input(options["prompt"] + " ")

def add_to_inventory(model, options):
    #TODO if statement should be in module's initialize function,
    #     called by main game's initialize method
    if "inventory" not in model["game"]:
        model["game"]["inventory"] = {}
    if options["item"] not in model["game"]["inventory"]:
        model["game"]["inventory"][options["item"]] = 1
    else:
        model["game"]["inventory"][options["item"]] += 1
    print options["item"] + " added to inventory!\n"

    print "press enter/return \n"
    raw_input()

def view_inventory(model, options):
    if "inventory" in model["game"] and len(model["game"]["inventory"].keys()):
        for item in model["game"]["inventory"].items():
            print str(item[0]) + " x " + str(item[1]) + "\n"
    else:
        print model["game_data"]["messages"]["inventory_empty"] + "\n"

    print "press enter/return \n"
    raw_input()

#TODO I'd like some way of automating this registering
actions = {
    "name_entity" : name_entity,
    "add_to_inventory" : add_to_inventory,
    "view_inventory": view_inventory
}
### end of actions

#TODO tail-call optimize
def replace_string_placeholders(model, string):
    matches = re.search("\{\{(.*?)\}\}", string)
    if(matches):
        default = matches.group(1)
        return replace_string_placeholders(
            model,
            re.sub(
                matches.group(0),
                model["game"][default] if default in model["game"] else default,
                string))
    else:
        return string

def test_condition(model, condition):
    if (re.search("^!", condition)):
        return condition[1:] not in model["game"]
    else:
        return condition in model["game"]

#TODO tail-call optimize
def apply_conditions(model, string):
    conditional_statement = "\(\((.*?) \? (.*?) \| (.*?)\)\)"
    matches = re.search(conditional_statement, string)

    if(matches):
        conditional_test = matches.group(1)
        if_true_string = matches.group(2)
        if_false_string = matches.group(3)

        replacement_substring = ""
        #TODO should not be in top level
        if conditional_test in model["game"]:
            replacement_substring = if_true_string
        else:
            replacement_substring = if_false_string

        return apply_conditions(
            model,
            re.sub(conditional_statement, replacement_substring, string))
    else:
        return string

def process_string(model, string):
    return apply_conditions(model, replace_string_placeholders(model, string))

#TODO refactor using dictionary.get() ?
def filter_choices(model, choices):
    def apply_choice_condition(choice):
        if ("condition" in choice):
            return test_condition(model, choice["condition"])
        else:
            return True
    return filter(apply_choice_condition, choices)

def update(player_input, model):
    if player_input == "q":
        model["game"]["quitting"] = True
    else:
        model["game"]["last_choice_was_valid"] = False
        #TODO shouldn't save the whole room in model["game"]
        #TODO filter_choices takes only model as argument? seems like it should be less
        for choice in filter_choices(model, model["game"]["current_room"]["choices"]):
            if player_input == choice["input"]:
                model["game"]["last_choice_was_valid"] = True
                if "action" in choice and choice["action"]["name"] in actions:
                    #TODO Should be in view functions
                    os.system("clear")
                    actions[choice["action"]["name"]](
                        model,
                        choice["action"]["options"])
                model["game"]["current_room"] = model["game_data"]["scenes"][choice["destination"]]
    return model

def view(model):
    os.system("clear")

    if model.get("game").get("quitting"):
        print "\n" + model["game_data"]["messages"]["quit"]
    else:
        print "\n" + process_string(model, model["game"]["current_room"]["description"]) + "\n"

        for choice in filter_choices(model, model["game"]["current_room"]["choices"]):
            print choice["input"] + ") " + process_string(model, choice["description"])

        #TODO maybe this shouldn't be here, maybe the game should check the json for validity
        #     One test being that there is always a quit option
        print "q) quit game\n"

        pp.pprint(model["game"].get("last_choice_was_valid"))
        if not model["game"].get("last_choice_was_valid"):
            print model["game_data"]["messages"]["invalid_choice"]

def player_input(model):
    return raw_input(model["game_data"]["messages"]["prompt"] + " ")

def initialize(game_data):
    scenes = game_data["scenes"]
    return {
        "game_data": game_data,
        "game": {
            "current_room": scenes[scenes["first scene name"]],
            "last_choice_was_valid": True
        }
    }

def game_loop(model):
    view(model)
    return update(player_input(model), model)

with open("python-adventure.game") as game_file:
    model = initialize(json.load(game_file))
    while not model["game"].get("quitting"):
        model = game_loop(model)
