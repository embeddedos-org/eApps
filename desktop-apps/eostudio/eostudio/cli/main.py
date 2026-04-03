"""EoStudio CLI — Command-line interface for EoStudio."""

import click

from eostudio import __version__


@click.group()
@click.version_option(version=__version__, prog_name="EoStudio")
def cli():
    """EoStudio — Cross-Platform Design Suite with LLM Integration."""


@cli.command()
@click.option(
    "--editor",
    type=click.Choice([
        "3d", "cad", "paint", "game", "ui", "product",
        "interior", "uml", "simulation", "database", "ide", "all",
    ]),
    default="all",
    help="Editor to launch.",
)
@click.option("--theme", type=click.Choice(["dark", "light"]), default="dark")
def launch(editor: str, theme: str):
    """Launch the EoStudio GUI application."""
    from eostudio.gui.app import EoStudioApp

    app = EoStudioApp(editor=editor, theme=theme)
    app.run()


@cli.command()
@click.argument("project_file")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["stl", "obj", "svg", "gltf", "dxf", "png"]),
    required=True,
)
@click.option("--output", "-o", required=True, help="Output file path.")
def export(project_file: str, fmt: str, output: str):
    """Export a design project to a specific format."""
    from eostudio.formats.project import EoStudioProject

    project = EoStudioProject.load(project_file)
    project.export(fmt, output)
    click.echo(f"Exported {project_file} -> {output} ({fmt})")


@cli.command()
@click.argument("project_file")
@click.option(
    "--framework",
    type=click.Choice([
        "html", "flutter", "compose", "react", "openscad",
        "mobile-flutter", "mobile-react-native", "mobile-kotlin", "mobile-swift",
        "desktop-electron", "desktop-tauri", "desktop-tkinter", "desktop-qt",
        "webapp-react-fastapi", "webapp-vue-flask", "webapp-angular-express",
        "database-sql", "database-sqlalchemy", "database-prisma", "database-django",
    ]),
    required=True,
)
@click.option("--output", "-o", required=True, help="Output directory.")
def codegen(project_file: str, framework: str, output: str):
    """Generate code from a UI/3D design project."""
    from eostudio.codegen import generate_code

    generate_code(project_file, framework, output)
    click.echo(f"Generated {framework} code -> {output}")


@cli.command()
@click.option(
    "--lesson",
    type=click.Choice([
        "shapes", "colors", "3d-basics", "simple-game",
        "build-robot", "design-house",
    ]),
    default="shapes",
)
@click.option(
    "--difficulty",
    type=click.Choice(["beginner", "intermediate", "advanced"]),
    default="beginner",
)
def teach(lesson: str, difficulty: str):
    """Launch LLM-powered kids learning mode."""
    from eostudio.core.ai.tutor import KidsTutor

    tutor = KidsTutor(lesson=lesson, difficulty=difficulty)
    tutor.start_interactive()


@cli.command()
@click.option("--endpoint", default="http://localhost:11434", help="LLM API endpoint.")
@click.option("--model", default="llama3", help="LLM model name.")
@click.option(
    "--provider",
    type=click.Choice(["ollama", "openai"]),
    default="ollama",
    help="LLM provider backend.",
)
@click.option("--api-key", default="", help="API key (required for OpenAI).")
@click.option(
    "--domain",
    type=click.Choice([
        "general", "cad", "ui", "3d", "game",
        "hardware", "simulation", "database", "uml",
    ]),
    default="general",
    help="Design domain for context-aware prompts.",
)
@click.argument("prompt")
def ask(endpoint: str, model: str, provider: str, api_key: str, domain: str, prompt: str):
    """Ask the AI design agent a question."""
    from eostudio.core.ai.agent import DesignAgent

    agent = DesignAgent(
        endpoint=endpoint, model=model,
        provider=provider, api_key=api_key, domain=domain,
    )
    response = agent.ask(prompt)
    click.echo(response)


@cli.command()
@click.argument("diagram_file")
@click.option(
    "--language",
    type=click.Choice(["python", "java", "kotlin", "typescript", "cpp", "csharp"]),
    required=True,
)
@click.option("--output", "-o", required=True, help="Output directory.")
def uml_codegen(diagram_file: str, language: str, output: str):
    """Generate code from a UML class diagram."""
    import json
    import os
    from eostudio.core.uml.diagrams import ClassDiagram
    from eostudio.core.uml.code_gen import UMLCodeGen

    with open(diagram_file) as f:
        data = json.load(f)
    diagram = ClassDiagram.from_dict(data)
    gen = UMLCodeGen()
    generators = {
        "python": gen.generate_python,
        "java": gen.generate_java,
        "kotlin": gen.generate_kotlin,
        "typescript": gen.generate_typescript,
        "cpp": gen.generate_cpp,
        "csharp": gen.generate_csharp,
    }
    files = generators[language](diagram)
    os.makedirs(output, exist_ok=True)
    for filename, content in files.items():
        filepath = os.path.join(output, filename)
        with open(filepath, "w") as f:
            f.write(content)
    click.echo(f"Generated {language} code from UML -> {output} ({len(files)} files)")


@cli.command()
@click.option("--dt", default=0.01, help="Simulation time step.")
@click.option("--duration", default=10.0, help="Simulation duration in seconds.")
@click.argument("model_file")
def simulate(model_file: str, dt: float, duration: float):
    """Run a MATLAB-style simulation model."""
    import json
    from eostudio.core.simulation.engine import SimulationModel

    with open(model_file) as f:
        data = json.load(f)
    model = SimulationModel.from_dict(data)
    model.dt = dt
    model.duration = duration
    results = model.run()
    click.echo(f"Simulation complete: {len(results)} signals captured over {duration}s")
    for name, signal in results.items():
        click.echo(f"  {name}: {signal.num_samples()} samples, "
                    f"mean={signal.mean():.4f}, rms={signal.rms():.4f}")


@cli.command()
@click.argument("schema_file")
@click.option(
    "--dialect",
    type=click.Choice(["sqlite", "postgresql", "mysql", "sqlalchemy", "prisma", "django"]),
    default="sqlite",
)
@click.option("--output", "-o", required=True, help="Output file path.")
def dbgen(schema_file: str, dialect: str, output: str):
    """Generate database code from a schema design."""
    import json
    from eostudio.codegen.database import (
        DatabaseSchema, generate_sql, generate_sqlalchemy,
        generate_prisma, generate_django_models,
    )

    with open(schema_file) as f:
        data = json.load(f)
    schema = DatabaseSchema.from_dict(data)
    generators = {
        "sqlite": lambda s: generate_sql(s, "sqlite"),
        "postgresql": lambda s: generate_sql(s, "postgresql"),
        "mysql": lambda s: generate_sql(s, "mysql"),
        "sqlalchemy": generate_sqlalchemy,
        "prisma": generate_prisma,
        "django": generate_django_models,
    }
    result = generators[dialect](schema)
    with open(output, "w") as f:
        f.write(result)
    click.echo(f"Generated {dialect} schema -> {output}")


@cli.command()
@click.argument("path", default=".")
@click.option("--theme", type=click.Choice(["dark", "light"]), default="dark")
def ide(path: str, theme: str):
    """Launch the EoStudio IDE (code editor with Git, extensions, terminal)."""
    from eostudio.gui.app import EoStudioApp

    app = EoStudioApp(editor="ide", theme=theme)
    app.run()


@cli.command()
@click.option(
    "--template",
    type=click.Choice([
        "todo-app", "mechanical-part", "game-platformer",
        "iot-dashboard", "simulation-pid",
    ]),
    required=True,
    help="Project template to use.",
)
@click.option("--output", "-o", required=True, help="Output directory.")
@click.option("--list-templates", "show_list", is_flag=True, help="List available templates.")
def new(template: str, output: str, show_list: bool):
    """Create a new project from a template."""
    from eostudio.templates.samples import list_templates, create_project_from_template

    if show_list:
        for tmpl in list_templates():
            click.echo(f"  {tmpl.name:20s} — {tmpl.description}")
        return

    project_path = create_project_from_template(template, output)
    click.echo(f"Created project from '{template}' template -> {project_path}")


def main():
    cli()


if __name__ == "__main__":
    main()
