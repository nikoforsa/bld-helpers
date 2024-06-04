
Param (
[string]$name,
[string]$pass,
[string]$build
)

$env:PATH = $env:PATH + ';C:\Program Files\Conan\conan\'
$env:PATH = $env:PATH + ';C:\BuildTools\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\'
$env:PATH = $env:PATH + ';C:\vcpkg\vcpkg-master\downloads\tools\powershell-core-7.2.11-windows\'

$env:PATH -split ';'

conan remote add conan_repository https://git.com/api/v4/projects/140/packages/conan
conan remote update conan_repository https://git.com/api/v4/projects/140/packages/conan false
conan user $name -r conan_repository -p $pass

conan profile new default --detect

if (![string]::IsNullOrEmpty($build)){
    conan profile update settings.build_type=$build default
}

git config --global http.sslVerify "false"
