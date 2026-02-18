import click
import os
import sys
import json
import platform
import subprocess
from typing import Optional

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import config

@click.group()
@click.version_option(version="5.1.0")
@click.option('--verbose', '-v', is_flag=True, help="Enable verbose logging.")
@click.option('--config-file', type=click.Path(exists=True), help="Path to custom config file.")
@click.option('--blender-path', type=click.Path(exists=True), help="Custom path to Blender executable.")
def cli(verbose, config_file, blender_path):
    """BlenPC v5.1 - Procedural Building Generator for Blender 5.0.1"""
    if verbose:
        os.environ["MF_LOG_LEVEL"] = "DEBUG"
    if blender_path:
        os.environ["BLENDER_PATH"] = blender_path

@cli.command()
@click.option('--width', '-w', type=float, default=20.0, help="Building width in meters.")
@click.option('--depth', '-d', type=float, default=16.0, help="Building depth in meters.")
@click.option('--floors', '-f', type=int, default=1, help="Number of floors.")
@click.option('--seed', '-s', type=int, default=0, help="Random seed for deterministic generation.")
@click.option('--roof', '-r', type=click.Choice(['flat', 'gabled', 'hip', 'shed'], case_sensitive=False), default='flat', help="Roof type.")
@click.option('--output', '-o', type=click.Path(), default='./output', help="Output directory.")
@click.option('--format', multiple=True, type=click.Choice(['glb', 'blend', 'fbx', 'obj'], case_sensitive=False), default=['glb'], help="Export formats.")
@click.option('--preview', is_flag=True, help="Open in Blender GUI after generation.")
def generate(width, depth, floors, seed, roof, output, format, preview):
    """Generate a procedural building based on parameters."""
    click.echo(f"Generating building: {width}x{depth}, {floors} floors, Seed: {seed}, Roof: {roof}")
    # Implementation will be added in Phase 2
    click.echo("Warning: Generation logic integration is planned for Phase 2.")

@cli.command()
@click.argument('asset_type', type=click.Choice(['wall', 'door', 'window'], case_sensitive=False))
@click.option('--name', '-n', required=True, help="Asset name.")
@click.option('--length', '-l', type=float, help="Length (for walls).")
@click.option('--seed', '-s', type=int, default=0, help="Random seed.")
@click.option('--tags', '-t', help="Comma-separated tags.")
def create(asset_type, name, length, seed, tags):
    """Create a specific building asset (e.g., a wall)."""
    click.echo(f"Creating {asset_type}: {name}, Seed: {seed}")
    
    if asset_type == 'wall':
        if not length:
            click.echo("Error: --length is required for wall creation.", err=True)
            return
            
        input_data = {
            "command": "create_wall",
            "seed": seed,
            "asset": {
                "name": name,
                "dimensions": {"width": length},
                "tags": tags.split(',') if tags else ["arch_wall"]
            }
        }
        
        input_file = "cli_input.json"
        output_file = "cli_output.json"
        
        with open(input_file, 'w') as f:
            json.dump(input_data, f)
            
        cmd = [config.BLENDER_PATH, "--background", "--python", "run_command.py", "--", input_file, output_file]
        
        try:
            click.echo(f"Running Blender: {config.BLENDER_PATH}")
            subprocess.run(cmd, check=True)
            
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    res = json.load(f)
                    if res.get("status") == "success":
                        click.secho(f"Successfully created asset: {name}", fg="green")
                    else:
                        click.secho(f"Error: {res.get('message')}", fg="red")
        except Exception as e:
            click.secho(f"Execution failed: {e}", fg="red")
        finally:
            if os.path.exists(input_file): os.remove(input_file)
            if os.path.exists(output_file): os.remove(output_file)

@cli.command()
def version():
    """Display version information."""
    click.echo(f"blenpc v5.1.0")
    click.echo(f"Blender: {config.BLENDER_PATH}")
    click.echo(f"Python: {platform.python_version()}")
    click.echo(f"Platform: {platform.system()} {platform.release()}")

if __name__ == '__main__':
    cli()
