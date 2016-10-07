#!/bin/sh

# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

installdir="$HOME/lib/bash/"
setupgit=0
un=""
email=""

while getopts "d:gu:e:" opt; do
    case "$opt" in
    d)
	installdir="$OPTARG"
        ;;
    g)  setupgit=1
        ;;
    u)
	un="$OPTARG"
	;;
    e)
	email="$OPTARG"
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

if [ ! -e "$installdir" ] ; then
    mkdir -p "$installdir"
fi

cd "$installdir"

url="://github.com/MannyMoo/commandline-utils.git"
git clone "https${url}" || git clone "git${url}"

utilsdir="${installdir}/commandline-utils/"

echo "Installed in ${utilsdir}
To use everything do:
source ${utilsdir}/source-all.sh ${utilsdir}
"

if [ $setupgit != 0 ] ; then
    echo "Configuring git."
    source ${utilsdir}/git-tools/git-tools.sh
    git_setup_new_machine "${un}" "${email}"
    git_set_ssh_remote "${utilsdir}"
fi
