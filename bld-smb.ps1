cd $Env:HOME_DIRECTORY

if (![string]::IsNullOrEmpty($Env:GITSSHKEY)){
    git config --global core.sshCommand "ssh -i c:$Env:HOME_DIRECTORY/.ssh/id_rsa -F /dev/null -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no"
    git clone  git@git.com:project1/bld-smb.git
}
else{
    $creds="$Env:GIT_USERNAME`:$Env:GIT_PASSWORD"
    git clone "https://$creds@git.com:project1/bld-smb.git"
}

#Copy-Item "$Env:HOME_DIRECTORY$Env:NAME_PROJECT/storagedata.yml" -Destination ./bld-smb/ -Recurse
Copy-Item "$Env:HOME_DIRECTORY$Env:NAME_PROJECT/conandata.yml" -Destination ./bld-smb/ -Recurse

cd ./bld-smb/
python.exe ./public.py
