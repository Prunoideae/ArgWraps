from argwraps.cli.utils import subcommand
from argwraps.cli.guards import Arg
from argwraps.cli.models import ArgGroup, ArgMatcher, ArgMatches, SelfMatcher
from argwraps.util import _
from argwraps.guards.primitive import Int


# Declare the matcher we want
class TestMatcher(ArgMatcher):
    group: ArgGroup("Test Group")

    a: (Arg(Int)
        .short('a')
        .long('aa')
        .default(1)
        .help('rua')
        )

    b: (Arg(Int)
        .help('foo')
        .default(2)
        .required(False)
        )


class Test2Matcher(ArgMatcher):
    group: ArgGroup("Test2 Group")
    a: Int
    b: _

    @classmethod
    def inspect(cls, args: dict):
        matcher: Test2Matcher = super().inspect(args)
        if matcher is not None:
            matcher.b = matcher.a + 1
        return matcher


@subcommand(help="Hello world")
def command(self: ArgMatches, test: TestMatcher, test2: Test2Matcher):
    print(self.selfmatcher)
    print(test.a)
    print(test2.b)
