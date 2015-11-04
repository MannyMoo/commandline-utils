# Utilities for working with git.

if [ -z "$GITKEYNAME" ] ; then
    export GITKEYNAME='~/.ssh/id_rsa.git'
fi

function git_start_ssh_agent() {
    if [ -z `eval "$(ssh-agent -s)"` ] ; then
	echo "ssh agent isn't running! Can't add git id."
    else
	ssh-add "$GITKEYNAME"
    fi
}

function git_gen_key() {
    if [ ! -e ~/.ssh ] ; then
	mkdir ~/.ssh
    fi
    ssh-keygen -t rsa -b 4096 -f "$GITKEYNAME" -C "$(git config --get user.email)"
    git_start_ssh_agent
    echo "Public key:"
    cat "${GITKEYNAME}.pub"
    set_git_ssh_config
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
