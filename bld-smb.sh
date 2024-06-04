#!/bin/bash

cd ${HOME_DIRECTORY}

if [ ! -z "${GITSSHKEY}" ]; then
    git config --global core.sshCommand "ssh -i ${HOME_DIRECTORY}/.ssh/id_rsa -F /dev/null -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    git clone git@git.com:project1/bld-smb.git
else
    git clone https://${GIT_USERNAME}:${GIT_PASSWORD}@git.com:project1/bld-smb.git
fi

#yes | cp -i ${HOME_DIRECTORY}/${NAME_PROJECT}/storagedata.yml ./bld-smb/
yes | cp -i ${HOME_DIRECTORY}/${NAME_PROJECT}/conandata.yml ./bld-smb/
cd ./bld-smb/
python3 ./public.py
 