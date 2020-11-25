import os
from .svn_services import create_svn_repo, svn_check_out, svn_commit_all, svn_relocate
from zou.app.config import SVN_PARENT_PATH, SVN_PARENT_URL, PROJECTS_FOLDER, FILE_MAP
from configparser import ConfigParser
import shutil
file_map_parser = ConfigParser()
acl_parser = ConfigParser()

def write_config(file_directory, config_parser):
    '''
        write data from a configuration parser
        to file
    '''
    with open(file_directory, 'w') as f:
        config_parser.write(f)

def create_project_folder(project_name):
    project_svn_folder = os.path.join(SVN_PARENT_PATH, project_name)
    project_repo_url = os.path.join(SVN_PARENT_URL, project_name)
    project_folder = os.path.join(PROJECTS_FOLDER, project_name)
    svn_authz_path = os.path.join(SVN_PARENT_PATH, project_name, 'conf/authz')

    create_svn_repo(project_svn_folder)
    svn_check_out(project_repo_url, project_folder)
    base_directories = ['.conf','edit', 'lib', 'refs', 'scenes', 'tools']
    lib_directories = ['chars', 'envs', 'maps', 'nodes', 'props']
    for directory in base_directories:
        os.mkdir(os.path.join(project_folder, directory))
    for directory in lib_directories:
        os.mkdir(os.path.join(project_folder, 'lib', directory))
    file_map_dir = os.path.join(project_folder, '.conf/file_map')
    file_map_parser['file_map'] = FILE_MAP
    write_config(file_map_dir, file_map_parser)
    svn_commit_all(project_folder, 'event commit')
    acl_parser['groups'] = {
                'admin':'suser',
                'maps':'',
                'edit':'',
            }
    acl_parser['/'] = {
                '*':'r',
                '@admin':'rw',
            }
    write_config(svn_authz_path, acl_parser)

def rename_project(old_project_name, new_project_name):
    new_project_folder = os.path.join(PROJECTS_FOLDER, new_project_name)
    old_project_folder = os.path.join(PROJECTS_FOLDER, old_project_name)
    new_project_svn_folder = os.path.join(SVN_PARENT_PATH, new_project_name)
    old_project_svn_folder = os.path.join(SVN_PARENT_PATH, old_project_name)
    new_project_repo_url = os.path.join(SVN_PARENT_URL, new_project_name)
    # old_project_repo_url = os.path.join(svn_parent_url, old_project_name)
    shutil.move(old_project_svn_folder, new_project_svn_folder)
    shutil.move(old_project_folder, new_project_folder)
    svn_relocate(new_project_repo_url, new_project_folder)