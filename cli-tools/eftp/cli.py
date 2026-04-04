"""FTP/SFTP client — EoS CLI Tool"""
import click

@click.group()
@click.version_option(version="1.0.0")
def main():
    """FTP/SFTP client — EoS CLI Tool"""
    pass

@main.command()
def status():
    """Show current status"""
    click.echo("FTP/SFTP client — EoS CLI Tool v1.0.0")

if __name__ == "__main__":
    main()
