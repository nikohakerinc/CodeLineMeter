import os
import gitlab
import logging
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
GIT_URL = os.getenv('GIT_URL')
GIT_TOKEN = os.getenv('GIT_TOKEN')

# Logging level
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
logging.basicConfig(filename=os.path.join(log_dir, 'get_projects.log'), level=logging.DEBUG,
                    format='%(levelname)s: %(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

# Connect to Git
gl = gitlab.Gitlab(GIT_URL, private_token=GIT_TOKEN)
try:
    # List all projects
    projects = gl.projects.list(all=True)

    # Define the path for the project list file
    project_list_file = Path(__file__).resolve().parent / "project.txt"

    # Write project URLs to the project list file
    with open(project_list_file, "w", encoding="utf8") as f:
        for project in projects:
            project_url = f"{project.web_url}.git\n"
            f.write(project_url)
            logging.info(f"Added project: {project_url.strip()}")

    # Log successful completion
    logging.info("Project list has been successfully generated.")

except Exception as e:
    # Log errors
    logging.error(f"An error occurred: {str(e)}")
