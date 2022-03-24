import click
import os


@click.group()
def cli():
    pass


@click.command(
    help="Set parameters. Pass the JSON directly or via a file path. Only a subset of the required parameters has to be passed. The non-occuring values will be reused from the current config."
)
@click.option("--path", default="", help="Path to JSON file")
@click.option("--content", default="", help="Content of JSON file")
def set_parameters(path, content):
    if path == "" and content == "":
        click.echo("You have to pass either a path or the file content.")
    elif path != "" and content != "":
        click.echo("You cannot pass both a path and the file content.")
    else:
        if path != "":
            # TODO: validate_file
            pass
        else:
            # TODO: validate content
            pass


cli.add_command(set_parameters)

if __name__ == "__main__":
    cli.main(prog_name="pyra-cli")
