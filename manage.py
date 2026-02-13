#!/usr/bin/env python3
import os
import sys
import subprocess
import click

# Ensure project root is in PYTHONPATH
sys.path.append(os.getcwd())


@click.group()
def cli():
    """WoW Datamine Toolkit Management Utility"""
    pass


@cli.command()
def init():
    """Initialize project folders and databases."""
    from Tools.core.project_init import init_all

    init_all()
    click.echo("✅ Project initialized successfully.")


@cli.command()
@click.option("--host", default="127.0.0.1", help="API Host")
@click.option("--port", default=8002, help="API Port")
def serve(host, port):
    """Start the FastAPI Database Service."""
    click.echo(f"🚀 Starting DB Service on {host}:{port}...")
    subprocess.run(["uv", "run", "python", "Tools/core/db_service.py"])


@cli.command()
@click.argument("test_path", default="Tools/tests")
def test(test_path):
    """Run tests using pytest."""
    click.echo(f"🧪 Running tests in {test_path}...")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    subprocess.run(["uv", "run", "pytest", test_path], env=env)


@cli.command()
@click.option("--limit", default=100, help="Max builds to process")
@click.option("--workers", default=4, help="Parallel workers")
def ingest(limit, workers):
    """Start the Master Ingester."""
    click.echo(f"📥 Starting ingestion (limit={limit}, workers={workers})...")
    env = os.environ.copy()
    env["MAX_BUILDS"] = str(limit)
    env["MAX_WORKERS"] = str(workers)
    env["PYTHONPATH"] = os.getcwd()
    subprocess.run(["uv", "run", "python", "Tools/ingestion/master_ingester.py"], env=env)


@cli.command()
def lint():
    """Run linting checks with ruff."""
    click.echo("🔍 Running ruff check...")
    subprocess.run(["uv", "run", "ruff", "check", "."])


@cli.command()
def format():
    """Format code with ruff."""
    click.echo("🎨 Formatting code...")
    subprocess.run(["uv", "run", "ruff", "format", "."])


if __name__ == "__main__":
    cli()
