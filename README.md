staypuft-poc: Provisioning Node Config Tool
============

This tool was designed to help you get started with Red Hat's new Foreman-based OpenStack deployment tool, codenamed Staypuft. To get started very quickly and to enable bare-metal provisioning of OpenStack nodes, this script automates the configuration of the following-

* Configuration of Foreman/Staypuft host pre-requisites
* Configuration of bare-metal boot images (based on RHEL 6.5)
* Configuration of package repositories for build server
* Configuration of package repositories for booting clients
* Installation of StayPuft, Foreman, and all required dependencies

To get started, you need only prepare a RHEL 6.5 machine that's going to be your target deployment node. Then follow these steps:

Install **git** so that you can clone this repository:

	# yum install git -y
	# git clone https://github.com/rdoxenham/staypuft-poc.git
	Initialized empty Git repository in /root/staypuft-poc/.git/
	...
	
Before you can dive into the deployment tool, we require some additional components, namely:

* A RHEL 6.5 DVD iso (**rhel-server-6.5-x86_64-dvd.iso**)
* The following synchronised channels:
	* **rhel-x86_64-server-6**
	* **rhel-x86_64-server-6-ost-4**
	* **rhel-x86_64-server-6-rhscl-1**
	* **rhel-x86_64-server-ha-6**
	* **rhel-x86_64-server-lb-6**
	* **rhel-x86_64-server-6-mrg-messaging-2**
	* **rhel-x86_64-server-rh-common-6**

It's expected that these requirements will already be available, if not you'll find a file named "make-repos.py" within the repository which can be used to automatically pull down the latest packages from an available **Red Hat Network Satellite** and create repositories based on the required channels.
	
The script will ask you a number of questions regarding the location of the Satellite, a username, password, and output directory. Ensure that your output directory relates to the cloned git repository, and place the repositories into the 'repos/' directory:

	# cd /root/staypuft-poc
	# ./make-repos.py
	INFO: No configuration file found.
	Satellite FQDN: satellite.london.redhat.com
	Satellite Username: rhn-admin
	Password: 
	Output Directory: /root/staypuft-poc/repos

	Connecting to: http://satellite.london.redhat.com/rpc/api...
	[output omitted]
	
**Note**: This will likely take some time to download, especially over a slow link. For repeated usage, clone this repository to a USB disk and persist the content on-disk so make-repos.py isn't continually used.

Next, place the RHEL DVD iso into the iso/ directory:

	# cp /path/to/rhel-server-6.5-x86_64-dvd.iso /root/staypuft-poc/iso/.
	# sync
	
Next, you're ready to start using the deployment tool. Simply run the script and it will ask you a few questions before it does the heavy lifting. Also note that all of this should be done as 'root':

	# ./staypuft_poc.py

	StayPuft OpenStack PoC Configuration Script v0.1
	Rhys Oxenham <roxenham@redhat.com>
	INFO: Configuring system...

	Enter provisioning FQDN of this host:
	[output omitted]

Once complete, you can move onto the final step, actually running the StayPuft configuration tool:

	# staypuft-installer
	[output omitted]
	
Ensure that you configure StayPuft/Foreman to use the correct provisioning interface and that you configure the correct DHCP ranges. Leave it to install and it should eventually be ready for usage.

Finally, you can use the auto-generated bare-metal kickstart file for provisioning new hosts. The file located in **/root/staypuft_files**, and you'll need to override the default **"Kickstart default"** entry by taking these steps in the Foreman UI:

1. Login to the WebUI for Foreman
2. Select **Hosts** from the top-menu
3. Select **Provisioning Templates**
4. In the **Filter** box enter  **'Kickstart default'**
5. Select the top entry, which should be the **'Kickstart default'** template
6. Copy and paste the file from **/root/staypuft_files/** into this box
7. Select **Submit**

The installer should have configured the **Foreman Discovery** image for you, so any unknown nodes that attempt to PXE boot inside of the environment should go into an pre-provisioned state and you can control what happens to them. The exercise above and the steps taken by the configuration script enabled you to boot RHEL 6.5 machines and have them automatically connect to (and use) the package repositories provided, enabling OpenStack to be deployed from bare-metal at the click of a few buttons.

Any problems, please let me know. This is very much **pre-alpha**, and I've done very little testing.


**Disclaimer**: I take no responsibility for any losses incurred whilst using this code. This is not a supported or accredited package from Red Hat, it's a "pet project" - usage is at your **own risk**! ;-)
	