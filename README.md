# commandline-utils

A set of useful functions and aliases for commandline work.

To install by default you can do:
```shell
sh -c "$(curl -fsSL https://raw.githubusercontent.com/MannyMoo/commandline-utils/master/setup.sh)"
```

or

```shell
sh -c "$(wget https://raw.githubusercontent.com/MannyMoo/commandline-utils/master/setup.sh -O -)"
```

Alternatively, if you want to specify the install directory (default is ~/lib/bash/) or configure git ssh access automatically (eg, for a new machine) you can do

```shell
curl -fsSL https://raw.githubusercontent.com/MannyMoo/commandline-utils/master/setup.sh > setup.sh
```

or

```shell
wget https://raw.githubusercontent.com/MannyMoo/commandline-utils/master/setup.sh
```

then

```shell
sh setup.sh
```

with optional arguments

```
-d : Set the install directory.
-g : Configure git for ssh access.
-u : User name for git.
-e : User email for git.
```