####!/usr/bin/env python
import os
import re
import sys
import subprocess
import argparse
import traceback

#pip install pyyaml
#import pyaml
import yaml

VERBOSE = False

VERSION_MAJOR_INCREMENT = ""
VERSION_MINOR_INCREMENT = ""
VERSION_PATCH_INCREMENT = ""
NEW_TAG = ""

__repo_dir = None
ignore_missing_git = False
on_tag = False
tag_name = ""
storageConfig = {}

def GetLabelTemplate():
    '''
        получение шаблона тега 
    '''
    global storageConfig
    with open(os.path.realpath('conandata.yml')) as file:
        try:
            storageConfig = yaml.safe_load(file) 
            #print(storageConfig)
        except yaml.YAMLError as exc:
            print(exc)
    return list(storageConfig["project_tag_version"].split('.'))

def SaveLabelTemplate():
    try:
        with open(os.path.realpath('conandata.yml'), 'w') as yaml_file:
            storageConfig["project_tag_version"] = str(VERSION_MAJOR_INCREMENT) +"."+ str(VERSION_MINOR_INCREMENT) +"."+ str(VERSION_PATCH_INCREMENT)
            if storageConfig["pkgs"]:
                  storageConfig["pkgs"]["control"]["Version"] = str(VERSION_MAJOR_INCREMENT) +"."+ str(VERSION_MINOR_INCREMENT) +"."+ str(VERSION_PATCH_INCREMENT)
            #print("SaveLabelTemplate")
            #storageConfig["project_tag_version"] = 'str(VERSION_MAJOR_INCREMENT) +"."+ str(VERSION_MINOR_INCREMENT) +"."+ str(VERSION_PATCH_INCREMENT)'
            dump = yaml.safe_dump(storageConfig, default_flow_style=False,
                          allow_unicode=False,
                          encoding=None,
                          sort_keys=False,
                          line_break=10)
            yaml_file.write(dump)
    except yaml.YAMLError as exc:
        print(exc)

def repo_dir():
    global __repo_dir
    if __repo_dir is not None:
        return __repo_dir

    #__repo_dir = os.environ.get('NAME_PROJECT', None)

    if not __repo_dir:
        if not ignore_missing_git:
            try:
                __repo_dir = (
                    subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True)
                    .stdout.strip()
                    .decode()
                )
            except:
                pass
    if not __repo_dir:
        #__repo_dir = "."
        __repo_dir = os.getcwd().strip()
    
    return __repo_dir

def get_version_from_git():
    global VERSION_MAJOR_INCREMENT, VERSION_MINOR_INCREMENT, VERSION_PATCH_INCREMENT, NEW_TAG, tag_name, on_tag
    fail_ret = None
    current_commit = ""
    git_describe = ''
    #print(repo_dir())
    try:
        current_commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_dir(),
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).strip()
        git_describe = subprocess.check_output(
            ["git", "describe", "--abbrev=0", "--tags"],
            cwd=repo_dir(),
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        ).strip()
        #print(f"git describe max tag = {git_describe}")
        on_tag = True
    except subprocess.CalledProcessError as er:
        if VERBOSE:
            traceback.print_exc()
        if er.returncode == 128:
            # git exit code of 128 means no repository found
            on_tag = False
            #tag_name = storageConfig["name_project"]
            #print(tag_name)
            #git_describe = tag_name+'.0.0.0'
            #print(git_describe)
            #print(repo_dir().split("/")[-1])
            #tag_name = repo_dir().split("/")[-1]
            #return list(git_tag_parts), tag_name, on_tag
            #return fail_ret
    except OSError:
        if VERBOSE:
            traceback.print_exc()
        return fail_ret

    if git_describe:        
        git_tag_parts = vers_split(git_describe)
        tag_name = name_split(git_describe)
        #print(tag_name)
        #tag_name = re.match(r"([-\w]*)\.(\d+\.\d+(\.\d+))", git_describe).group(1).split(".")
        try:
            # Find all tags on the commit and if there are multiple get the largest version 
            tag_sha = subprocess.check_output(
                ["git", "rev-list", "-n", "1", git_describe],
                cwd=repo_dir(),
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            ).strip()
            sha_tags = subprocess.check_output(
                ["git", "tag", "--points-at", tag_sha],
                cwd=repo_dir(),
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            ).strip()
            sha_tags = {tuple(vers_split(t)): t for t in sha_tags.split("\n")}
            git_tag_parts = max(sha_tags)
            #tag_name = name_split(git_tag_parts)
            #git_tag_parts = vers_split(git_tag_parts)

            #print(git_tag_parts)
            if not sha_tags:
                sha_tags = subprocess.check_output(
                    ["git", "tag", "--list", "--sort=v:refname"],
                    cwd=repo_dir(),
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                ).strip()
                sha_tags = [t for t in sha_tags.split("\n")]
                #print(sha_tags)
                #inverse = [(value, key) for key, value in sha_tags.items()]
                #git_tag_parts = sha_tags[-1]
                git_tag_parts = vers_split(sha_tags[-1])
                tag_name = name_split(sha_tags[-1])
            #print(sha_tags)
            #sha_tags = {tuple(vers_split(t)): t for t in sha_tags.split("\n")}
            
            #print(git_tag_parts)

        except subprocess.CalledProcessError:
            tag_sha = ""
            if VERBOSE:
                traceback.print_exc()
        except OSError:
            if VERBOSE:
                traceback.print_exc()
            return fail_ret
    else:
        #tag_name = 
        git_describe = storageConfig["name_project"]+'.0.0.0'
        tag_name = name_split(git_describe)
        git_tag_parts = vers_split(git_describe)
        on_tag = False

    return list(git_tag_parts), tag_name, on_tag

def vers_split(vers):
    try:
        #print (re.search(r"(\S)*\.(\d+\.\d+(\.\d+))", vers))
        return list(re.search(r"([-\w]*)\.(\d+\.\d+(\.\d+))", vers).group(2).split("."))
    except:
        print("Could not parse version from:", vers, file=sys.stderr)
        raise

def name_split(vers):
    try:
        return list(re.search(r"([-\w]*)\.(\d+\.\d+(\.\d+))", vers).group(1).split("."))
    except:
        print("Could not parse version from:", vers, file=sys.stderr)
        raise

def git_version():
    global VERSION_MAJOR_INCREMENT, VERSION_MINOR_INCREMENT, VERSION_PATCH_INCREMENT, NEW_TAG, tag_name
    parts_label = GetLabelTemplate()
    parts, tag_name, on_tag = get_version_from_git()
    # print("===get_version_from_git===",parts, tag_name, on_tag)
    if not parts:
        # No git repo or first commit not yet made
        raise ResourceWarning()
    
    if on_tag:
        if parts[0] < parts_label[0]:
            #print("Update major version")
            VERSION_MAJOR_INCREMENT = parts_label[0]
            VERSION_MINOR_INCREMENT = parts_label[1]
            VERSION_PATCH_INCREMENT = int(parts_label[2])+1
        elif parts[1] < parts_label[1]:
            #print("Update minor version")
            VERSION_MAJOR_INCREMENT = parts[0]
            VERSION_MINOR_INCREMENT = parts_label[1]
            VERSION_PATCH_INCREMENT = parts_label[2]
        elif parts[2] < parts_label[2]:
            #print("Update patch version")
            VERSION_MAJOR_INCREMENT = parts[0]
            VERSION_MINOR_INCREMENT = parts[1]
            VERSION_PATCH_INCREMENT = parts_label[2]
        else:
            #print("Update only patch version")
            VERSION_MAJOR_INCREMENT = parts[0]
            VERSION_MINOR_INCREMENT = parts[1]
            VERSION_PATCH_INCREMENT = int(parts[2])+1
    else:
        VERSION_MAJOR_INCREMENT = parts_label[0]
        VERSION_MINOR_INCREMENT = parts_label[1]
        VERSION_PATCH_INCREMENT = parts_label[2]
        
    #create new tag
    NEW_TAG = tag_name[0] + '.' + str(VERSION_MAJOR_INCREMENT) +"."+ str(VERSION_MINOR_INCREMENT) +"."+ str(VERSION_PATCH_INCREMENT)
    return NEW_TAG

def save_version_to_git(parse=False):
    global VERSION_MAJOR_INCREMENT, VERSION_MINOR_INCREMENT, VERSION_PATCH_INCREMENT, tag_name
    fail_ret = None
    NEW_TAG = git_version()
    # print("===save_version_to_git===", NEW_TAG)
    # NEW_TAG = tag_name[0] + '.' + str(VERSION_MAJOR_INCREMENT) +"."+ str(VERSION_MINOR_INCREMENT) +"."+ str(VERSION_PATCH_INCREMENT)
    try:
        #print(f"Tagged with1")
       
        if not parse:
            # git_tag_set = subprocess.check_output(
            #     ["git", "tag", NEW_TAG],
            #     cwd=repo_dir(),
            #     stderr=subprocess.STDOUT
            # )
            # print(f"Tagged with1 {git_tag_set}")
            # git_tag_set = subprocess.check_output(
            #     ["git", "push", "origin", NEW_TAG]
            # )
            # print(f"Tagged with2 {git_tag_set}")
            SaveLabelTemplate()
            # print(f"not parse tag1 = {parse}", repo_dir())
            subprocess.check_output(
                ["git", "tag", NEW_TAG],
                cwd=repo_dir(),
                stderr=subprocess.STDOUT
            )
            # print(f"not parse tag2 = {parse}")
            subprocess.check_output(
                ["git", "push", "origin", NEW_TAG],
                cwd=repo_dir(),
                stderr=subprocess.STDOUT
            )
            on_tag = True
            # print(f"not parse tag = {parse}")
        else:
            SaveLabelTemplate()
            on_tag = True
            # print(f"save to file parse = {parse}")

    except subprocess.CalledProcessError as er:
        if VERBOSE:
            traceback.print_exc()
            print(f"EXCEPTION1")
        if er.returncode == 128:
            # git exit code of 128 means no repository found
            print(f"EXCEPTION2")
            return fail_ret
        
    # return VERSION_MAJOR_INCREMENT, VERSION_MINOR_INCREMENT, VERSION_PATCH_INCREMENT, tag_name, NEW_TAG
    # print("===save_version_to_git2===", NEW_TAG)
    return NEW_TAG

def get_fetch_tag_from_git():
    fail_ret = None
    try:
        git_fetch = subprocess.check_output(
            ["git", "fetch", "--tags", "-f"]
        ).strip()
        on_tag = True
    except subprocess.CalledProcessError as er:
        if VERBOSE:
            traceback.print_exc()
        if er.returncode == 128:
            # git exit code of 128 means no repository found
            return fail_ret

def main():
    help_text = f"""\
        The tag version increment to a git commit:
        tag_name, major, minor, patch"
    """
    parser = argparse.ArgumentParser(description="Manage version.", 
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=help_text )
    
    parser.add_argument("--parse", action="store_true", help="only parse out tag")
    parser.add_argument("--tag", action="store_true", help="calculate next MR tag")
    parser.add_argument("--save", action="store_true", help="Add version tag to conandata.yml and commit git")
    parser.add_argument("--git", action="store_true", help="Creates git tag to release the current commit")
    args = parser.parse_args()

    if args.parse:
        #if true only parse method tag
        print(save_version_to_git(True))

    if args.save:
        print(save_version_to_git(False))

    if args.tag:
        print(git_version())

    if args.git:
        print(save_version_to_git(True))
        
if __name__ == "__main__":
    main()
