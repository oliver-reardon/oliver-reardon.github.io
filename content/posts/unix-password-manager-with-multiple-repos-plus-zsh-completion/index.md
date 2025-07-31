---
title: Unix Password Manager with Multiple Repos + zsh Completion
date: 2022-12-15 02:36:49-04:00
author: Oliver Reardon
tags:
  - unix
  - password-manager
  - zsh-completion
  - cli
  - git-repo
keywords:
  - multiple repos
  - environment variable
  - password store
  - auto-completion
description: How to use the pass CLI password manager with multiple repositories and enable zsh completion for each.
showFullContent: false
readingTime: true
hideComments: false
---
[**Pass**](https://www.passwordstore.org/) is a brutally simple and effective CLI password manager for *nix systems. There are multiple front ends if you prefer not to rely on the CLI, and also a great iOS app that can sync your pass git repo – [passforios](https://mssun.github.io/passforios/).

I prefer to separate various project password stores into multiple repos, but pass does not cater for this natively. By default, it creates a single password store at `~/.password-store`. To change that behavior and use an alternate location, you must modify an environment variable and define your new preferred location.

---

## Defining a New Password Store

Set a new environment variable:

```sh
export PASSWORD_STORE_DIR=~/.password_store_one
```

Now, when you call `/usr/local/bin/pass`, it will use the location you defined as the password store.

---

## Multiple Password Stores with Functions

To define multiple separate password stores, create a function for each store you wish to define. These can be stored in your `~/.zshrc` file so they are ready to use in each session.

```sh
function pass_one() {
  PASSWORD_STORE_DIR=$HOME/.password_store_one pass "$@"
}

function pass_two() {
  PASSWORD_STORE_DIR=$HOME/.password_store_two pass "$@"
}
```

---

## Enabling zsh Completion for Each Store

If you require auto-completion using pass, the completion definition will need to be available and defined in `$fpath` with the definition name `_pass`.  
Modify your `~/.zshrc` to include your preferred completions functions path and add the zstyle completion rules for each password store.

```sh
# Define completion definition functions
fpath=( ~/completions $fpath )

# Required to activate autocomplete in zsh
autoload -Uz compinit && compinit

compdef _pass pass_one
zstyle ':completion::complete:pass_one::' prefix "$HOME/.password_store_one"
pass_one() {
  PASSWORD_STORE_DIR=$HOME/.password_store_one pass "$@"
}

compdef _pass pass_two
zstyle ':completion::complete:pass_two::' prefix "$HOME/.password_store_two"
pass_two() {
  PASSWORD_STORE_DIR=$HOME/.password_store_two pass "$@"
}
```

---

## Initializing and Using Your Password Stores

Now you can initialize your pass repos using the GPG ID and start creating encrypted data.

```sh
$ pass_one init "Password Storage Key"
Password store initialized for Password Storage Key

$ pass_one generate secrets/blob 15                     
/Users/user/.password_store_one/secrets
The generated password for secrets/blob is:
^E5^^Em16AykW9R

$ pass_one 
Password Store
└── secrets
    └── blob

$ pass_two init "Password Storage Key"
Password store initialized for Password Storage Key

$ pass_two generate secrets/blob 15                     
/Users/user/.password_store_two/secrets
The generated password for secrets/blob is:
TA`[{1sp{E6f-|q

$ pass_two 
Password Store
```