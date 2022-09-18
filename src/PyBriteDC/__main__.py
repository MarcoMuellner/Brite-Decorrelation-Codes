"""Command-line interface."""
import click


@click.command()
@click.version_option()
def main() -> None:
    """Py-Brite-Decorrelation Codes."""


if __name__ == "__main__":
    main(prog_name="PyBriteDC")  # pragma: no cover
