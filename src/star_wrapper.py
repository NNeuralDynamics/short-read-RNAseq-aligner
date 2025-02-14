import os
import subprocess
import yaml
import argparse
from pathlib import Path

def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def run_star(fastq1=None, fastq2=None, **params):
    """
    Runs STAR for genome generation or alignment.

    Parameters:
        fastq1 (str, optional): Path to first FASTQ file (None for genome generation).
        fastq2 (str, optional): Path to second FASTQ file (if paired-end).
        **params: Additional STAR parameters from the config file.
    """
    mode = params.get("mode", "alignReads")
    genome_dir = params.get("genome_dir")
    out_dir = params.get("out_dir", ".")
    threads = params.get("threads", 8)
    log_file = params.get("log_file", "logs/star_run.log")

    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Base STAR command
    command = ["STAR", f"--runThreadN {threads}", f"--genomeDir {genome_dir}"]

    # Mode-specific commands
    if mode == "genomeGenerate":
        if "genomeFastaFiles" not in params or "sjdbGTFfile" not in params:
            raise ValueError("FASTA and GTF files are required for genome generation.")
        command += [f"--runMode genomeGenerate", f"--genomeFastaFiles {params['genomeFastaFiles']}", f"--sjdbGTFfile {params['sjdbGTFfile']}"]
    elif mode == "alignReads":
        if not fastq1:
            raise ValueError("At least one FASTQ file is required for alignment.")
        read_command = f"{fastq1} {fastq2}" if fastq2 else fastq1
        command += [f"--readFilesIn {read_command}", f"--outFileNamePrefix {out_dir}/"]
    else:
        raise ValueError("Invalid mode. Choose 'genomeGenerate' or 'alignReads'.")

    # Add additional parameters dynamically
    ignored_keys = {"mode", "genome_dir", "out_dir", "threads", "log_file"}
    command += [f"--{key} {value}" for key, value in params.items() if key not in ignored_keys]

    # Convert command list to a string
    command_str = " ".join(command)

    # Log and run command
    with open(log_file, "a") as log:
        log.write(f"\n{command_str}\n")
    
    try:
        print(f"Running STAR: {command_str}")
        subprocess.run(command_str, shell=True, check=True)
        print("STAR execution completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running STAR: {e}")
        with open(log_file, "a") as log:
            log.write(f"ERROR: {e}\n")
        exit(1)

def batch_process(input_folder, config):
    """Detects FASTQ files in a folder and runs STAR for each sample."""
    input_folder = Path(input_folder)
    if not input_folder.exists():
        raise FileNotFoundError(f"Input folder '{input_folder}' not found.")

    suffix = config.get("file_suffix", "_R1.fastq.gz")
    paired_end = config.get("paired_end", True)

    fastq_files = sorted(input_folder.glob(f"*{suffix}"))
    
    if not fastq_files:
        print(f"No FASTQ files found in {input_folder}.")
        return

    for fastq1 in fastq_files:
        sample_name = fastq1.stem.replace(suffix, "")
        fastq2 = input_folder / f"{sample_name}_R2.fastq.gz" if paired_end else None
        run_star(str(fastq1), str(fastq2) if paired_end else None, **config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrapper for STAR RNA-seq alignment.")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to YAML config file.")
    parser.add_argument("-i", "--input_folder", help="Folder containing FASTQ files (batch mode).")
    parser.add_argument("--fastq1", help="Path to single FASTQ file (manual mode).")
    parser.add_argument("--fastq2", help="Path to paired FASTQ file (if paired-end).")
    parser.add_argument("--mode", choices=["genomeGenerate", "alignReads"], help="Override mode.")
    parser.add_argument("--threads", type=int, help="Override thread count.")
    args = parser.parse_args()

    config = load_config(args.config)

    # override parameters in config if provided at CL
    overrides = {k: v for k, v in vars(args).items() if v is not None}
    config.update(overrides)

    if args.input_folder:
        batch_process(args.input_folder, config)
    elif args.fastq1:
        run_star(args.fastq1, args.fastq2, **config)
    else:
        print("Error: Please specify an input folder (-i) or FASTQ files (--fastq1).")
