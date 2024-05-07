import click

from .lint_lists import lint_lists


@click.group()
def cli():
    """Test Lists management command line tool."""
    pass


@cli.command("lint-lists")
@click.argument("lists_path", type=click.Path())
@click.option("--fix-duplicates", is_flag=True, help="Fix duplicates in the test list")
@click.option("--fix-slash", is_flag=True, help="Fix slashes in the test list")
def cli_lint_lists(lists_path, fix_duplicates, fix_slash):
    """
    Check that the test lists are OK.

    Args:
        lists_path (str): Path to the test list.
        fix_duplicates (bool): Option to fix duplicates in the test list.
        fix_slash (bool): Option to fix slashes in the test list.
    """
    lint_lists(lists_path, fix_duplicates=fix_duplicates, fix_slash=fix_slash)


if __name__ == "__main__":
    cli()
