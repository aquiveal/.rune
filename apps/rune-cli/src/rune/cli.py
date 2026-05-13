import typer

app = typer.Typer(
    name="rune",
    help="Rune: The shadow version control system for LLM context.",
    add_completion=False,
    no_args_is_help=True,
)

@app.callback()
def callback():
    pass

from rune.commands import init, config, remote, submodule, update, fetch, pull, status, diff, vendor, skill

app.command(name="init")(init.init_cmd)
app.command(name="config")(config.config_cmd)
app.command(name="update")(update.update_cmd)
app.command(name="fetch")(fetch.fetch_cmd)
app.command(name="pull")(pull.pull_cmd)
app.command(name="status")(status.status_cmd)
app.command(name="diff")(diff.diff_cmd)

remote_app = typer.Typer(no_args_is_help=True)
remote_app.command(name="add")(remote.add_cmd)
app.add_typer(remote_app, name="remote")

submodule_app = typer.Typer(no_args_is_help=True)
submodule_app.command(name="add")(submodule.add_cmd)
submodule_app.command(name="deinit")(submodule.deinit_cmd)
submodule_app.command(name="rm")(submodule.rm_cmd)
app.add_typer(submodule_app, name="submodule")

vendor_app = typer.Typer(no_args_is_help=True)
vendor_app.command(name="add")(vendor.add_cmd)
app.add_typer(vendor_app, name="vendor")

skill_app = typer.Typer(no_args_is_help=True)
skill_app.command(name="validate")(skill.validate_cmd)
app.add_typer(skill_app, name="skill")

def main():
    app()

if __name__ == "__main__":
    main()






