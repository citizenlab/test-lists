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
@click.option(
    "--fix-notes", is_flag=True, help="Fix notes field by converting it to JSON"
)
@click.option(
    "--force-update", is_flag=True, help="Forces updating of the tests list formats"
)
def cli_lint_lists(lists_path, fix_duplicates, fix_slash, fix_notes, force_update):
    """
    Check that the test lists are OK.

    Args:
        lists_path (str): Path to the test list.
        fix_duplicates (bool): Option to fix duplicates in the test list.
        fix_slash (bool): Option to fix slashes in the test list.
        fix_notes (bool): Option to fix notes in the test list.
        force_update (bool): Option to force update of the test list. Useful to change quoting.
    """
    lint_lists(
        lists_path,
        fix_duplicates=fix_duplicates,
        fix_slash=fix_slash,
        fix_notes=fix_notes,
        force_update=force_update,
    )


if __name__ == "__main__":
    cli()
