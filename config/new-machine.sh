#!/bin/bash

# setup a new linux server

sudo apt install tmux emacs python3 zsh git

curl https://pyenv.run | bash

export GITKEYNAME="${HOME}/.ssh/keys/id_rsa.git"
if [ ! -d ~/.ssh/keys ] ; then
    mkdir ~/.ssh/keys
fi

wget https://raw.githubusercontent.com/MannyMoo/commandline-utils/master/setup.sh
echo "Enter username for git:"
read un
echo "Enter email for git:"
read em
bash setup.sh -g -u "$un" -e "em"
rm setup.sh

bash ~/lib/bash/commandline-utils/shell-tools/setup-zsh.sh

git clone git@github.com:MannyMoo/config.git lib/config
bash ~/lib/config/default-linux/setup.sh
python3 ~/lib/config/ssh/setup.py
bash ~/lib/config/tmux/setup.sh
bash ~/lib/config/emacs/setup.sh
