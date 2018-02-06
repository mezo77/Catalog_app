# Catalog App
## overview
This website implements CRUD operations, it's a catalog that contains categories and their elements.

## What is needed to run this app
# Installing the Vagrant VM
you will need the Vagrant software to configure and manage the VM. Here are the tools you'll need to install to get it running:
# Git
If you don't already have Git installed, download Git from [here](https://git-scm.com/downloads), Install the version for your operating system.
On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash). (On Mac or Linux systems you can use the regular terminal program).
You will need Git to install the configuration for the VM. If you'd like to learn more about Git, take a look at [this](https://try.github.io/levels/1/challenges/1) or [this](https://www.atlassian.com/git/tutorials)

# VirtualBox
VirtualBox is the software that actually runs the VM. you can download it from [here](https://www.virtualbox.org/wiki/Downloads).
Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

_Ubuntu 14.04 Note_: If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the `virtualbox.org` web site. Due to a [reported bug](https://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

# Vagrant
Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem, you can download it from [here](https://www.vagrantup.com/downloads.html). Install the version for your operating system.

`windows OS note:` The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

# Fetch the Source Code and VM Configuration
`Windows:`  Use the Git Bash program (installed with Git) to get a Unix-style terminal.

`other systems:` Use your favorite terminal program.

# How to run this app
# Clone this Repo to your local machine
From the terminal, run the following command (be sure to replace `<username>` with your GitHub username):
git clone http://github.com/ `<username>`/https://github.com/mezo77/Catalog_app catalog
this will make a directory named catalog

#Run the virtual machine
you can find the virtual machine to run this app [here](https://github.com/udacity/fullstack-nanodegree-vm)
after cloning the vm, move the catalog app that you have just cloned to the vagrant folder,
open a terminal window and type `vagrant up` and when it's done type `vagrant ssh` This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type `exit` at the shell prompt. To turn the virtual machine off (without deleting anything), type `vagrant halt`. If you do this, you'll need to run vagrant up again before you can log into it.

# Running the Restaurant Menu App
Now after running the virtual machine and log into the VM by typing `vagrant ssh`, change the directory to /vagrant  directory by typing `cd /vagrant`. This will take you to the shared folder between your virtual machine and host machine.
you will find the catalog directory that you have moved to vagrant directory(there is a catalog directory already in the vagrant directory so, when you move the cloned catalog replace it with the already-was-existed one). Type `ls` short for list to list all the files and directories in the current directory.
you should find `application.py`, `database_config.py`, `data_inserter.py` and two directories `templates` and `static`

Now type `python database_config.py` to initialize the database.
type `python database_inserter.py` to insert some data in the database (optional)
type `python application.py` to run the flask web server. In your browser visit `http://localhost:8000` to show the catalog app.
If you ran database_inserter.py you should now see three categories in the nav menu on the left, and to be able to add, edit, and delete, you have to login with your google or facebook account
