
from dataclasses import dataclass
from argwraps.cli.guards import Arg
from argwraps.guards.abstract import AbstractGuard
from typing import Any, Dict, List, Tuple, Union
from types import FunctionType
from argwraps.models.abstract import AbstractMatcher
import argparse
import inspect


@dataclass
class ArgGroup():
    group_name: str


class ArgMatcher(AbstractMatcher):
    '''
    A matcher for generating argparse subgroups which
    capable for further usage.
    Override the group annotation to set the ArgGroup name.
    '''

    group: ArgGroup(group_name='Placeholder')

    @classmethod
    def inspect(cls, args: dict):
        raw: ArgMatcher = super().inspect({k: v for k, v in args.items() if v is not None})
        if raw is None:
            return None

        raw.__dict__ |= {
            k: v.__default__
            for k, v in cls.__annotations__.items()
            if isinstance(v, Arg) and k not in raw.__dict__}
        return raw

    @classmethod
    def parser(cls):
        if not hasattr(cls, '__annotations__'):
            return None

        if hasattr(cls, '__parser__'):
            return cls.__parser__

        args: Dict[str, Arg] = {k: v for k, v in cls.__annotations__.items() if isinstance(v, Arg)}
        parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        group = parser.add_argument_group(cls.__annotations__['group'].group_name)
        for name, arg in args.items():
            if arg.__long__ is None and arg.__short__ is None:
                names_tuple = []
            else:
                names_tuple = []
                if arg.__short__ is not None:
                    names_tuple.append('-' + arg.__short__)
                if arg.__long__ is not None:
                    names_tuple.append('--' + arg.__long__)

            arg_dict = {
                'dest': name
            }

            if arg.__default__ is not None:
                arg_dict['default'] = arg.__default__

            if arg.__flag__ is not None:
                if arg.__flag__ == True:
                    arg_dict['action'] = 'store_true'
                elif arg.__flag__ == False:
                    arg_dict['action'] = 'store_false'
                else:
                    arg_dict['action'] = 'store_const'
                    arg_dict['const'] = arg.__flag__

            if arg.__choices__ is not None:
                arg_dict['choices'] = arg.__choices__

            if arg.__required__:
                arg_dict['required'] = arg.__required__

            if arg.__meta__ is not None:
                arg_dict['metavar'] = arg.__meta__
            else:
                guard = arg.__type__
                orig_type = guard.__orig_bases__[0].__args__[0]
                if orig_type is int or orig_type is float:
                    arg_dict['metavar'] = str(orig_type.__name__).upper()
                else:
                    arg_dict['metavar'] = "STR"

            if arg.__argtype__ is not None:
                arg_dict['type'] = arg.__argtype__

            if arg.__help__ is not None:
                arg_dict['help'] = arg.__help__

            group.add_argument(*names_tuple, **arg_dict)

        cls.__parser__ = parser
        return parser


class SelfMatcher():
    '''
    A matcher build through @arg decorator to represent some temp args
    added in specific command.
    '''

    def __init__(self) -> None:
        self.args: Dict[str, Arg] = {}

    def append(self, **kwargs):
        args: Dict[str, Arg] = {k: v for k, v in kwargs.items() if isinstance(v, Arg)}
        self.args |= args

    def inspect(self, args: Dict[str, Any]):
        for name, value in args.items():
            if name in self.args and self.args[name].test(value):
                self.__dict__[name] = self.args[name].transform(value)
        for k, v in self.args.items():
            if k not in self.__dict__:
                self.__dict__[k] = v.__default__

    def set_args(self, subparser: argparse.ArgumentParser):
        args: Dict[str, Arg] = {k: v for k, v in self.args.items() if isinstance(v, Arg)}

        for name, arg in args.items():
            if arg.__long__ is None and arg.__short__ is None:
                names_tuple = []
            else:
                names_tuple = []
                if arg.__short__ is not None:
                    names_tuple.append('-' + arg.__short__)
                if arg.__long__ is not None:
                    names_tuple.append('--' + arg.__long__)

            arg_dict = {
                'dest': name
            }

            if arg.__default__ is not None:
                arg_dict['default'] = arg.__default__

            if arg.__flag__ is not None:
                if arg.__flag__ == True:
                    arg_dict['action'] = 'store_true'
                elif arg.__flag__ == False:
                    arg_dict['action'] = 'store_false'
                else:
                    arg_dict['action'] = 'store_const'
                    arg_dict['const'] = arg.__flag__

            if arg.__choices__ is not None:
                arg_dict['choices'] = arg.__choices__

            if arg.__required__:
                arg_dict['required'] = arg.__required__

            if arg.__meta__ is not None:
                arg_dict['metavar'] = arg.__meta__
            else:
                guard = arg.__type__
                orig_type = guard.__orig_bases__[0].__args__[0]
                if orig_type is int or orig_type is float:
                    arg_dict['metavar'] = str(orig_type.__name__).upper()
                else:
                    arg_dict['metavar'] = "STR"

            if arg.__argtype__ is not None:
                arg_dict['type'] = arg.__argtype__

            if arg.__help__ is not None:
                arg_dict['help'] = arg.__help__

            subparser.add_argument(*names_tuple, **arg_dict)

    def wraps(self, fn: FunctionType) -> Dict[str, Any]:
        argspec = inspect.getfullargspec(fn)
        parameter_list = argspec.args + argspec.kwonlyargs
        return {x: self.__dict__[x] for x in parameter_list}

    def call(self, fn: FunctionType) -> Any:
        return fn(**self.wraps(fn))


class ArgMatches():
    '''
    A matcher combines submatchers and selfmatcher, represent a general
    matching result in a command call.

    It's used if the function call involves too much arguments, otherwise
    single matcher will be better for IDEs' auto-completion.
    '''

    def __init__(self, submatchers: List[AbstractMatcher], selfmatcher: SelfMatcher) -> None:
        self.submatchers = submatchers
        self.selfmatcher = selfmatcher

    def wraps(self, fn: FunctionType) -> Dict[str, Any]:
        w = self.selfmatcher.wraps(fn)
        for sm in self.submatchers:
            w |= sm.wraps(fn)
        return w

    def call(self, fn: FunctionType) -> Any:
        return fn(**self.wraps(fn))


@dataclass
class SubCommand():
    '''
    A class used in @subcommand decorator to describe a subcommand
    along with its function, subparsers and many more
    '''

    command: str
    fn: FunctionType
    help: str
    selfmatcher: Union[Tuple[str, SelfMatcher], None]
    submatchers: Dict[str, ArgMatcher]

    def call(self):
        matchers = self.submatchers
        if self.selfmatcher is not None:
            matchers |= {self.selfmatcher[0]: ArgMatches(self.submatchers, self.selfmatcher[1])}
        return self.fn(**self.submatchers)

    def parse_args(self, args: Dict[str, Any]):
        for k in self.submatchers:
            self.submatchers[k] = self.submatchers[k].inspect(args)
            if self.submatchers[k] is None:
                raise Exception()
        if self.selfmatcher is not None and self.selfmatcher[1] is not None:
            self.selfmatcher[1].inspect(args)

    def subparser(self, subparsers: argparse._SubParsersAction):
        arggroups = list(filter(lambda x: x is not None, map(lambda x: x.parser(), self.submatchers.values())))
        parser = subparsers.add_parser(self.command, parents=arggroups, help=self.help)
        if self.selfmatcher is not None and self.selfmatcher[1] is not None:
            self.selfmatcher[1].set_args(parser)
