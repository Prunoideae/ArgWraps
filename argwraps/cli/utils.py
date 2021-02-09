import argparse
from typing import Dict, Tuple, Union
from .models import ArgMatcher, ArgMatches, SelfMatcher, SubCommand
from types import FunctionType
from functools import wraps

__registry__: Dict[str, SubCommand] = {}


def arg(**kwargs):

    def closure(fn: Union[FunctionType, Tuple[Union[SelfMatcher, None], FunctionType]]) -> Tuple[Union[SelfMatcher, None], FunctionType]:
        if isinstance(fn, tuple):
            self_matcher = fn[0]
            fn = fn[1]
        else:
            self_matcher = SelfMatcher()
            fn = fn

        self_matcher.append(**kwargs)
        return (self_matcher, fn)

    return closure


def subcommand(help: str = None):
    '''
    Wraps up function as subcommand of the cli.

    This will make subcommand automatically registered to the global registry.
    '''
    def closure(fn: Union[FunctionType, Tuple[SelfMatcher, FunctionType]]):
        if isinstance(fn, tuple):
            self_matcher = fn[0]
            fn = fn[1]
        else:
            self_matcher = None
            fn = fn
        name = fn.__name__
        submatchers = {k: v for k, v in fn.__annotations__.items() if issubclass(v, ArgMatcher)}

        self_name = None
        for k, v in fn.__annotations__.items():
            if v == ArgMatches:
                self_name = k
                break
        if self_name is None and self_matcher is not None:
            raise Exception()
        elif self_name is None:
            self_matcher = None
        else:
            self_matcher = (self_name, self_matcher)

        __registry__[name] = SubCommand(command=name, fn=fn, help=help, selfmatcher=self_matcher, submatchers=submatchers)
        return __registry__[name]
    return closure


def main(help: str = None):
    '''
        Wraps a function as main(), with arg parsing and processing.

        Later calls on this function will trigger the parsing.
    '''
    def closure(fn: FunctionType):
        @wraps(fn)
        def closure_wraps():
            pass

        return closure_wraps

    return closure


def cli_build(prog, help):
    main_parser = argparse.ArgumentParser(prog=prog, description=help, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = main_parser.add_subparsers(dest='argwraps_cli_command')
    for v in __registry__.values():
        v.subparser(subparsers)
    return main_parser


def cli(prog, help):
    parser = cli_build(prog=prog, help=help)
    parsed = vars(parser.parse_args())
    if parsed['argwraps_cli_command'] is not None:
        command = __registry__[parsed['argwraps_cli_command']]
        command.parse_args(parsed)
        command.call()
    else:
        parser.print_help()
