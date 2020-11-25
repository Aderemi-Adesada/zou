import subprocess
import os

def create_svn_repo(project_svn_repo_path):
    subprocess.run(['svnadmin', 'create', project_svn_repo_path])

def svn_check_out(project_repo_url, project_folder):
    subprocess.run(['svn', 'co', project_repo_url, project_folder])

def svn_commit_all(project_folder, svn_commit_message):
    subprocess.run(['svn', 'cleanup', project_folder])
    subprocess.run(['svn', 'add', os.path.join(project_folder, '*'), '--force'])
    subprocess.run(['svn', 'cleanup', project_folder])
    subprocess.run(['svn', 'commit', project_folder, '-m', svn_commit_message])

def svn_relocate(new_url, working_path):
    subprocess.run(['svn', 'relocate', new_url, working_path])

def svn_rename(old_path, new_path):
    subprocess.run(['svn', 'rename', old_path, new_path])
