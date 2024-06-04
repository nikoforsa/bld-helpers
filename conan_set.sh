#!/usr/bin/bash

#conan remote remove conancenter
#conan remote remove braintwister

conan remote add conan_repository https://git.com/api/v4/projects/140/packages/conan
conan remote update conan_repository https://git.com/api/v4/projects/140/packages/conan false
conan user ${CONAN_LOGIN_USERNAME} -r conan_repository -p ${CONAN_PASSWORD}

conan profile new default --detect
conan profile update settings.compiler.libcxx=libstdc++11 default

if [ ! -z "${TYPE_BUILD}" ]; then
    conan profile update settings.build_type=${TYPE_BUILD} default
fi

#mkdir -p /home/$(whoami)/storage
git config --global http.sslVerify "false"
