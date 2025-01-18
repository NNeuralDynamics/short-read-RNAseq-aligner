import os
import requests


def download_file(url, local_filename):
    """
    Download a file from a URL to a local directory.
    """
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)


def main():
    # Create the GRCh38 directory in the parent directory
    grch38_dir = "../GRCh38"
    if not os.path.exists(grch38_dir):
        os.makedirs(grch38_dir)

    # URLs for the FASTA and GTF files
    fasta_url = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_29/GRCh38.primary_assembly.genome.fa.gz"
    gtf_url = "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_29/gencode.v45.primary_assembly.annotation.gtf.gz"

    # Filenames for the downloaded files (saving to the GRCh38 directory)
    fasta_file = os.path.join(grch38_dir, "GRCh38.primary_assembly.genome.fa.gz")
    gtf_file = os.path.join(grch38_dir, "gencode.v29.primary_assembly.annotation.gtf.gz")

    # Downloading files
    print("Downloading FASTA file...")
    download_file(fasta_url, fasta_file)
    print("FASTA file downloaded: " + fasta_file)

    print("Downloading GTF file...")
    download_file(gtf_url, gtf_file)
    print("GTF file downloaded: " + gtf_file)


if __name__ == "__main__":
    main()
