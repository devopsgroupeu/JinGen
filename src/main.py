#!/usr/bin/env python3

import logging
import argparse
import shutil
import sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, exceptions
import copy
import json

from logs import logger, setLoggingLevel, green, yellow, red, greenBack
from templating import load_and_merge_data, process_templates, process_non_template_files
from git import clone_repository


# --- Configuration ---
DEFAULT_TEMPLATE_SUFFIX = ".j2"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = logging.INFO  # Change to logging.DEBUG for more verbose output

BANNER_ART = r"""

████████╗███████╗██████╗ ██████╗  █████╗ ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
   ██║   █████╗  ██████╔╝██████╔╝███████║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗
   ██║   ██╔══╝  ██╔══██╗██╔══██╗██╔══██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
   ██║   ███████╗██║  ██║██║  ██║██║  ██║██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝

                                      __          ___           ____           _____
                                     / /  __ __  / _ \___ _  __/ __ \___  ___ / ___/______  __ _____
                                    / _ \/ // / / // / -_) |/ / /_/ / _ \(_-</ (_ / __/ _ \/ // / _ \
                                   /_.__/\_, / /____/\__/|___/\____/ .__/___/\___/_/  \___/\_,_/ .__/
                                        /___/                     /_/                         /_/

"""

def display_banner():
    """Prints the ASCII art banner."""
    print(BANNER_ART)
    print("-" * 105)  # Add a separator line


def print_section_header(title):
    """Prints a section header with a title."""
    print("=" * 105)
    print(f"=> {title.upper()}")
    print("=" * 105)

def cleanup_temp_files(temp_path):
    """Cleans up temporary files and directories. (also hidden files)"""
    if temp_path.exists():
        try:
            for item in temp_path.iterdir():
                if item.is_file() or item.is_symlink():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            temp_path.rmdir()  # Remove the temp directory itself
            logger.info(green("Temporary files cleaned up successfully."))
        except Exception as e:
            logger.error(red(f"Error cleaning up temporary files: {e}"))
    else:
        logger.info(yellow("No temporary files to clean up."))


# --- Argument Parsing and Main Execution ---
def main():
    display_banner()
    parser = argparse.ArgumentParser(
        description="Render Jinja2 templates and copy files (e.g., for Terraform, ArgoCD, ...) using data from a YAML file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        choices=["local", "git"],
        default="local",
        help="Choose the source of files.\n"
        "  local:   local source \n"
        "  git:     from git repository",
    )
    parser.add_argument(
        "-r",
        "--repo-url",
        type=str,
        help="Git repository URL in HTTPS format (required if source is 'git').",
    )
    parser.add_argument(
        "-b",
        "--branch",
        type=str,
        help="Branch to clone from the repository (default: default branch).",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing the Jinja2 template files (e.g., *.tf.j2).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where the rendered Terraform files (*.tf) will be saved.",
    )
    parser.add_argument(
        "-d", "--data-files",
        type=Path,
        required=True,
        nargs='+',            # Accept one or more values
        metavar='DATA_FILE',  # Display nicer variable name in help
        help="One or more paths to YAML data files. Values from later files override earlier ones during merge."
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")

    args = parser.parse_args()

    # --- Argument Validation ---
    if args.source == "git" and not args.repo_url:
        parser.error("When using 'git' as source, --repo-url is required.")

    # Adjust log level if debug flag is set
    if args.debug:
        setLoggingLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")

    print(f"  Source: {args.source}")
    if args.source == "git":
        print(f"  Repository URL: {args.repo_url}")
        if args.branch:
            print(f"  Branch: {args.branch}")
    print(f"  Input directory: {args.input_dir}")
    print(f"  Output directory: {args.output_dir}")
    print("  Data files:")
    for file in args.data_files:
        print(f"    - {file}")
    print(f"  Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    print("-" * 105)

    try:
        if args.source == "git":
            print_section_header("Cloning Git Repository")
            clone_repository(
                repo_url=args.repo_url,
                clone_path="temp/",
                branch=args.branch
            )
            INPUT_DIR = Path(f"temp/{args.input_dir}")
        else:
            INPUT_DIR = args.input_dir

        # 1. Load and Merge Data (pass the list of files)
        print_section_header("Data files merging")
        template_data = load_and_merge_data(args.data_files)

        # 2. Process Templates (uses the merged data)
        print_section_header("Template processing")
        process_templates(INPUT_DIR, args.output_dir, template_data)

        # 3. Process Non-Template Files
        print_section_header("Non-template files processing")
        process_non_template_files(INPUT_DIR, args.output_dir)

        logger.info(greenBack("TerraForge finished successfully."))
        sys.exit(0)

    except (FileNotFoundError, ValueError, OSError, Exception) as e:
        # Errors logged within functions, just exit cleanly
        logger.critical(red(f"Script terminated due to an error: {e}"))
        sys.exit(1)

    finally:
        # Cleanup temporary files if they were created
        print_section_header("Cleaning up temporary files")
        temp_path = Path("temp/")
        cleanup_temp_files(temp_path)


if __name__ == "__main__":
    main()
