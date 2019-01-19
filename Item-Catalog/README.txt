Project PrerequisitesIn order to start implementation smoothly, take a moment to check that all below prerequisites are installed in your PC:Unix-Style Terminal ProgramVagrant: https://www.vagrantup.com/downloads.htmlVirtual Machine: https://www.virtualbox.org/wiki/DownloadsFSND Virtual Machine: https://github.com/udacity/fullstack-nanodegree-vmOnce you get the above installed, run below commands inside fullstack-nanodegree-vm:
vagrant up
vagrant ssh
cd / vagrant / Item-Catalog
Project StructureYour project should be structured as illustrated below, the project appears inside Item-Catalog folder:
project.py
lotsofmenus.py
client_secreats.json
database_setup_.py
static
tampates

Coding Style:
Use Python PEP8 style guide to test your code quality pycodestyle
In terminal run :
pycodestyle database_up.py

pycodestyle lotsofmenus.py

pycodestyle project.py
 
to check the style, you should get 0 errors

Then run the application:

python project.py

After the last command you are able to browse the application at this URL:

http://localhost:5000/