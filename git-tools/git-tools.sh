
# Utilities for working with git.

if [ -z "$GITKEYNAME" ] ; then
    export GITKEYNAME="${HOME}/.ssh/id_rsa.git"
fi

function git_start_ssh_agent() {
    # Requires ssh-tools/ssh-tools.sh
    if [ -z `which ssh-agent` ] ; then
	echo "Can't find ssh-agent! Can't add git id."
    else
	start_ssh_agent
	ssh-add "$GITKEYNAME"
    fi
}

function git_setup_user_info() {
    if [ ! -z "$1" ] ; then
	un="$1"
    else
	echo "Enter your name for git:"
	read un
    fi
    if [ ! -z "$2" ] ; then
	email="$2"
    else
	echo "Enter email address for git:"
	read email
    fi
    git config --global user.name "${un}"
    git config --global user.email "${email}"
}

function git_gen_ssh_key() {
    echo "Generating ssh private/public key pair."
    if [ ! -e ~/.ssh ] ; then
	mkdir ~/.ssh
    fi
    ssh-keygen -t rsa -b 4096 -f "$GITKEYNAME" -C "$(git config --get user.email)"
    git_start_ssh_agent
    echo "Public key (on github.com copy to Settings -> SSH Keys -> Add SSH Key):"
    cat "${GITKEYNAME}.pub"
    echo "Editing ~/.ssh/config to add git config."
    git_set_ssh_config
    echo "Testing ssh settings."
    git_test_ssh 
}

function git_set_ssh_config() {
    if [ ! -e ~/.ssh/config ] ; then 
	touch ~/.ssh/config
    else
	cp ~/.ssh/config ~/.ssh/config.bkup
    fi
    # Could use sed -i but requires sed -i "" on MacOS.
    sed "1 i\\
Host github.com\\
\   PubkeyAuthentication yes\\
\   IdentityFile ${GITKEYNAME}\\
" ~/.ssh/config > ~/.ssh/config.tmp && mv ~/.ssh/config.tmp ~/.ssh/config
}

function git_test_ssh() {
    ssh -T git@github.com
}

function git_setup_new_machine() {
    git_setup_user_info $@
    git_gen_ssh_key
}

function git_init_repo() {
    local repo="$1"
    if [ $# = 2 ] ; then
	local repodir="$2"
    else
	local repodir="."
    fi
    cd "$repodir"
    git init
    git add .
    git commit -m "First commit"
    git remote add origin "$repo"
    git remote -v
    git push origin master
    cd "$OLDPWD"
}

function git_commit() {
    local msg="$1"
    if [ ! -z "$2" ] ; then
	local branch="$2"
    else
	local branch=`git_get_working_branch`
    fi
    git commit -a -m "$msg"
    git push origin "$branch"
}

function git_repo_name() {
    if [ -z "$1" ] ; then
	local d='.'
    else
	local d="$1"
    fi
    cd "$d"
    git remote -v | head -n 1 | sed 's#.*/\([^/]*/.*\.git\) .*#\1#'
    cd $OLDPWD
}

function git_set_ssh_remote() {
    if [ -z "$1" ] ; then
	local d='.'
    else
	local d="$1"
    fi
    cd "$d"
    local repo=`git_repo_name`
    git remote set-url origin "git@github.com:${repo}"
}

function git_get_working_branch() {
    git branch | grep '*' | sed 's/\* //'
}
