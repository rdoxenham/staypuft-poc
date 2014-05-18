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
	


**Disclaimer**: I take no responsibility for any losses incurred whilst using this code. This is not a supported or accredited package from Red Hat, it's a "pet project" - usage is at your **own risk**! ;-)
	