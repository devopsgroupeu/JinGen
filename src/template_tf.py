#!/usr/bin/env python3

import argparse
import logging
import sys
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, exceptions
import copy
import json

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


# --- Helper Functions ---
def deep_merge(target: dict, source: dict) -> dict:
    """
    Recursively merges source dictionary into target dictionary.
    If keys conflict, the value from the source dictionary takes precedence.
    Handles nested dictionaries. Modifies target in place.
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # Get node or create one
            node = target.setdefault(key, {})
            if isinstance(node, dict):
                # Recurse for nested dictionaries
                deep_merge(node, value)
            else:
                # If target's value for the key isn't a dict, overwrite it
                # This handles cases where structure differs (e.g., dict overwriting a string)
                target[key] = copy.deepcopy(
                    value
                )  # Use deepcopy for nested dicts from source
        else:
            # Overwrite value in target with value from source
            target[key] = value  # Simple assignment works for non-dict values
    return target


# --- Logging Setup ---
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT, stream=sys.stdout)
file_handler = logging.FileHandler("template_tf.log")
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)  # Use __name__ for logger identification


# --- Core Functions ---
def load_and_merge_data(data_file_paths: list[Path]) -> dict:
    """Loads data from multiple YAML files and merges them. Last file wins."""
    merged_data = {}
    logger.info(f"Loading and merging data from files (in order): {[str(p) for p in data_file_paths]}")

    for data_file_path in data_file_paths:
        logger.info(f"Attempting to load data from: {data_file_path}")
        if not data_file_path.is_file():
            logger.error(f"Data file not found: {data_file_path}")
            raise FileNotFoundError(f"Data file not found: {data_file_path}")

        try:
            with open(data_file_path, 'r') as f:
                # Use safe_load which is recommended over load
                current_data = yaml.safe_load(f)

                # Handle empty YAML files gracefully (safe_load returns None)
                if current_data is None:
                    logger.warning(f"Data file is empty, skipping merge: {data_file_path}")
                    continue # Skip to the next file

                # Ensure the loaded data is a dictionary for merging
                if not isinstance(current_data, dict):
                    logger.error(f"Data file content is not a valid YAML dictionary (key-value map): {data_file_path}")
                    raise ValueError(f"YAML content in {data_file_path} must be a dictionary")

                logger.debug(f"Successfully loaded data from {data_file_path}, performing deep merge...")
                # Perform the deep merge - modifies merged_data in place
                deep_merge(merged_data, current_data)
                logger.debug(f"Merge completed for {data_file_path}")

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML data file {data_file_path}: {e}", exc_info=True)
            raise ValueError(f"Invalid YAML format in {data_file_path}") from e
        except IOError as e:
            logger.error(f"Error reading data file {data_file_path}: {e}", exc_info=True)
            raise IOError(f"Could not read data file {data_file_path}") from e
        except Exception as e:
             logger.error(f"An unexpected error occurred loading {data_file_path}: {e}", exc_info=True)
             raise # Re-raise unexpected errors

    logger.info("Finished loading and merging all data files.")
    # Optionally log the final merged data structure at DEBUG level for verification
    if logger.isEnabledFor(logging.DEBUG):
         logger.debug(f"Final merged data:\n{json.dumps(merged_data, indent=2)}")
    return merged_data


def process_templates(input_dir: Path, output_dir: Path, template_data: dict):
    """Finds, renders, and writes Jinja templates."""
    logger.info(f"Starting template processing...")
    logger.info(f"Input directory: {input_dir.resolve()}")
    logger.info(f"Output directory: {output_dir.resolve()}")

    # --- Input Validation ---
    if not input_dir.is_dir():
        logger.error(
            f"Input directory does not exist or is not a directory: {input_dir}"
        )
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # --- Prepare Output Directory ---
    try:
        logger.debug(f"Ensuring output directory exists: {output_dir}")
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory ensured: {output_dir}")
    except OSError as e:
        logger.error(
            f"Could not create output directory {output_dir}: {e}", exc_info=True
        )
        raise OSError(f"Failed to create output directory {output_dir}") from e

    # --- Setup Jinja Environment ---
    # Use FileSystemLoader pointing to the input directory
    env = Environment(
        loader=FileSystemLoader(str(input_dir)),
        trim_blocks=True,  # Good practice for Terraform files
        lstrip_blocks=True,  # Good practice for Terraform files
        keep_trailing_newline=True,  # Often desired for config files
    )
    logger.debug("Jinja2 Environment initialized.")

    # --- Find and Process Templates ---
    template_files_found = 0
    templates_processed_successfully = 0
    templates_skipped = 0

    # Iterate through files matching the suffix in the input directory
    for template_path in input_dir.glob(f"**/*{DEFAULT_TEMPLATE_SUFFIX}"):
        if template_path.is_file():
            template_files_found += 1
            relative_path = template_path.relative_to(input_dir)
            output_filename = relative_path.with_suffix("")  # Remove the suffix
            output_path = output_dir / output_filename

            logger.info(
                f"Processing template: {relative_path} -> {output_path.relative_to(output_dir)}"
            )

            # Ensure subdirectory exists in output
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                logger.error(
                    f"Could not create subdirectory {output_path.parent} for {output_filename}: {e}",
                    exc_info=True,
                )
                continue  # Skip this file

            try:
                # Load template using its path relative to the input_dir
                template = env.get_template(str(relative_path))

                # Render the template with the provided data
                rendered_content = template.render(template_data)

                if not rendered_content.strip():
                    logger.warning(f"Rendered content for {relative_path} is empty. Skipping file.")
                    templates_skipped += 1
                    continue

                # Write the rendered content to the output file
                with open(output_path, "w") as f_out:
                    f_out.write(rendered_content)

                logger.debug(f"Successfully rendered and wrote {output_path}")
                templates_processed_successfully += 1

            except exceptions.TemplateNotFound:
                logger.error(
                    f"Template not found by Jinja (check path/permissions): {relative_path}"
                )
            except exceptions.TemplateSyntaxError as e:
                logger.error(
                    f"Syntax error in template {relative_path} at line {e.lineno}: {e.message}",
                    exc_info=True,
                )
            except exceptions.UndefinedError as e:
                logger.error(
                    f"Undefined variable used in template {relative_path}: {e.message}",
                    exc_info=True,
                )
            except IOError as e:
                logger.error(
                    f"Could not write output file {output_path}: {e}", exc_info=True
                )
            except (
                Exception
            ) as e:  # Catch any other unexpected errors during rendering/writing
                logger.error(
                    f"An unexpected error occurred processing {relative_path}: {e}",
                    exc_info=True,
                )

    logger.info(
        f"Template processing finished. Found {template_files_found} files matching '*{DEFAULT_TEMPLATE_SUFFIX}'."
    )
    if template_files_found > 0:
        logger.info(
            f"Successfully processed {templates_processed_successfully} templates."
        )
        logger.info(
            f"Skipped {templates_skipped} templates."
        )
        if (templates_processed_successfully + templates_skipped) < template_files_found:
            logger.warning(
                f"{template_files_found - templates_processed_successfully} templates failed to process."
            )
    else:
        logger.warning(
            f"No template files matching '*{DEFAULT_TEMPLATE_SUFFIX}' found in {input_dir}."
        )


def display_banner():
    """Prints the ASCII art banner."""
    print(BANNER_ART)
    print("-" * 105)  # Add a separator line


# --- Argument Parsing and Main Execution ---
def main():
    display_banner()
    parser = argparse.ArgumentParser(
        description="Render Jinja2 templates (e.g., for Terraform) using data from a YAML file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
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

    # Adjust log level if debug flag is set
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled.")

    try:
        # 1. Load and Merge Data (pass the list of files)
        template_data = load_and_merge_data(args.data_files)

        # 2. Process Templates (uses the merged data)
        process_templates(args.input_dir, args.output_dir, template_data)

        logger.info("TerraForge finished successfully.")
        sys.exit(0)

    except (FileNotFoundError, ValueError, OSError, Exception) as e:
        # Errors logged within functions, just exit cleanly
        logger.critical(f"Script terminated due to an error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
