import argparse
from argparse import HelpFormatter
from argparse import ArgumentParser

class DiscordArgparseParseError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DiscordArgParse(ArgumentParser):
    def __init__(
            self,
            prog=None,
            usage=None,
            description=None,
            epilog=None,
            parents=[],
            formatter_class=HelpFormatter,
            prefix_chars='-',
            fromfile_prefix_chars=None,
            argument_default=None,
            conflict_handler='error',
            add_help=True,
            allow_abbrev=True):
        self.exit_message = ""
        super(DiscordArgParse, self).__init__(
            prog, usage, description, epilog, parents, formatter_class, prefix_chars, fromfile_prefix_chars,
            argument_default, conflict_handler, add_help, allow_abbrev)

    def exit(self, status=0, message=None):
        raise (DiscordArgparseParseError(message))

    def print_usage(self, file=None):
        self.exit_message = self.format_usage()

    def print_help(self, file=None):
        self.exit_message = self.format_help()