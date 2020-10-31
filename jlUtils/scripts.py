"""
Utility functions related to constructing scripts
"""

import inspect as _inspect

import argparse as _argparse


def construct_args_from_fxn(fxn, additional_args=None, build_parser=True):
    """
    construct a list of dictionaries based on the passed
    function which specify the required parameters 
    for an arparse.ArgumentParser().add_argument() function
    
    Args:
        fxn: a python function
        additional_args: None or list of dictionaries of 
        format [{'name': <name>, 'default': <default>}]
        build_parse: boolean. whether or not the build the
        argparse.ArgumentParser() object and add the arguments
            from the add_arguments_dicts automatically, or
            just return the add_arguments_dicts dictionary
            so you can add other arguments on your own to
            the parser
    
    Returns:
        If build_parse == True:
            args: vars(parser.parse_args()) dictionary
        Else:
            add_arguments_dicts: list of dictionaries
    """
    # TODO: add functionality so doc-string will be parsed
    # and added as help string

    # Fetch all the arguments from the function and form
    # them into add_argument-like dictionary
    params = _inspect.signature(fxn).parameters

    add_arguments_dicts = []
    for key in params:

        arg = params[key]

        add_arguments_dict = {"name": f"--{arg.name}"}
        add_arguments_dict["type"] = str

        if "_empty" in str(arg.default):
            add_arguments_dict["required"] = True
        else:
            if isinstance(arg.default, list):
                add_arguments_dict["default"] = arg.default
            else:
                add_arguments_dict["default"] = str(arg.default)

            # We assume all inputs are of string type and
            # transform those inputs back to their original
            # type after receiving them
            add_arguments_dict["original_type"] = type(arg.default)

        add_arguments_dicts.append(add_arguments_dict)

    if additional_args is not None:
        for arg in additional_args:
            add_arguments_dict = {"name": f'--{arg["name"]}'}
            add_arguments_dict["type"] = str
            add_arguments_dict["default"] = str(arg["default"])
            add_arguments_dict["original_type"] = type(arg["default"])

            add_arguments_dicts.append(add_arguments_dict)

    if build_parser is False:
        return add_arguments_dicts

    # construct the parser
    parser = _argparse.ArgumentParser()

    for add_arg_dict in add_arguments_dicts:

        if "default" in add_arg_dict:
            parser.add_argument(
                add_arg_dict["name"],
                type=add_arg_dict["type"],
                default=add_arg_dict["default"],
            )
        else:
            parser.add_argument(
                add_arg_dict["name"],
                type=add_arg_dict["type"],
                required=add_arg_dict["required"],
            )

    args = parser.parse_args()

    args = vars(args)

    for i, key in enumerate(args):
        if "original_type" in add_arguments_dicts[i].keys():
            if add_arguments_dicts[i]["original_type"] == type(None):
                if args[key] == "None":
                    args[key] = None
            elif add_arguments_dicts[i]["original_type"] == type(bool()):
                if args[key] == "True":
                    args[key] = True
                elif args[key] == "False":
                    args[key] = False
                elif args[key] == "0":
                    args[key] = False
                elif args[key] == "1":
                    args[key] = True
            else:
                args[key] = add_arguments_dicts[i]["original_type"](args[key])
    return args
