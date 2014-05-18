#!/usr/bin/env python
# RHEL OSP StayPuft PoC Tool
# Rhys Oxenham <roxenham@redhat.com>

# Run this on the designated Foreman node
# Ensure that it's ran from repo directory

import os
import sys
import getpass
import subprocess

def check_root():
    if not os.geteuid() == 0:
        print "FATAL: Root privileges are required."
        sys.exit(1)

def die(last_point):
	print "FATAL: Stopped at %s" % last_point
	sys.exit(1)

def ask_question(question, hidden):
    answer = None
    if not hidden:
        while answer == "" or answer is None:
            answer = raw_input(question)
    else:
        while answer is None:
            answer = getpass.getpass(question)
    return answer

def yesno_question(question):
    is_valid = None
    while is_valid is None:
        answer = ask_question(question, False)
        if answer.upper() == "Y" or answer.upper() == "YES":
            return True
        elif answer.upper() == "N" or answer.upper() == "NO":
            return False
        else:
            is_valid = None

def configure_system():
	print "INFO: Configuring system..."
	happy = False
	while not happy:
		fqdn = ask_question("\nEnter provisioning FQDN of this host: ", False)
		happy = yesno_question("\nIs '%s' the correct FQDN for provisioning?: " % fqdn)
	happy = False
	while not happy:
		ip_address = ask_question("\nEnter IP address of provisioning adapter: ", False)
		happy = yesno_question("\nIs '%s' the correct IP address?: " % ip_address)

	try:
		line = "\n" + ip_address + " " + fqdn + "\n"
		with open('/etc/hosts', 'a') as file:
			file.write(line)
			file.close()
		subprocess.check_call(
			['setenforce', '0'], stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['sed', '-i', 's/SELINUX=.*/SELINUX=disabled/g', '/etc/sysconfig/selinux'],
				stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['mkdir', '-p', '/root/staypuft_files/'], stdout=devnull, stderr=devnull)
		with open("/root/staypuft_files/kickstart-rhel65.ks", "wt") as fout:
			with open("provisioning/original.ks", "rt") as fin:
				for line in fin:
					fout.write(line.replace('fqdn_location', fqdn + ":8080"))
	except: die("PRE-CONFIG")
	return fqdn

def create_ext_repos(fqdn):
	print "INFO: Creating ISO and package repositories..."
	try:
		subprocess.check_call(
			['mkdir', '-p', '/mnt/el6'],
			   stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['mount', '-o', 'loop', 'iso/rhel-server-6.5-x86_64-dvd.iso', '/mnt/el6'],
			   stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['mkdir', '-p', '/var/www/html/repos/rheldvd-el6'],
			   stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['cp', '-rf', '/mnt/el6/*', '/var/www/html/repos/rheldvd-el6/.'],
			   stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['umount', '/mnt/el6'],
			   stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['mkdir', '-p', '/var/www/html/repos/latest'],
			   stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['cp', '-rf', 'repos/*', '/var/www/html/repos/latest'],
			   stdout=devnull, stderr=devnull)
		with open("/var/www/html/repos/latest/openstack.repo", "wt") as fout:
			with open("repofiles/openstack.repo", "rt") as fin:
				for line in fin:
					fout.write(line.replace('fqdn', fqdn))
		subprocess.check_call(
			['chown', '-R', 'apache:apache', '/var/www/html'],
			   stdout=devnull, stderr=devnull)
	except: die("CREATING ISO REPOS")

def create_int_repos():
	print "INFO: Setting up local repositories..."
	try:
		subprocess.check_call(
			['cp', '/var/www/html/repos/latest/foreman.repo', '/etc/yum.repos.d/'],
			   stdout=devnull, stderr=devnull)
	except: die("INTERNAL REPOS")

def configure_vhost(fqdn):
	print "INFO: Configuring http repo vhost..."
	try:
		subprocess.check_call(
			['yum', '-t', '-y', '-e', '0', 'install', 'httpd'],
			   stdout=devnull, stderr=devnull)

		with open("/etc/httpd/conf.d/repos.conf", "wt") as fout:
			with open("config/repos.conf", "rt") as fin:
				for line in fin:
					fout.write(line.replace('fqdn', fqdn))

		subprocess.check_call(
			['service', 'httpd', 'start'],
			   stdout=devnull, stderr=devnull)
		subprocess.check_call(
			['chkconfig', 'httpd', 'on'],
			   stdout=devnull, stderr=devnull)
	except: die("CREATING VHOST")
	
def begin_install(fqdn):
	print "INFO: Attempting to install Staypuft..."
	try:
		subprocess.check_call(
			['yum', '-t', '-y', '-e', '0', 'install', 'foreman-installer-staypuft'],
			   stdout=devnull, stderr=devnull)
	except: die("STAYPUFT INSTALL")
	print "\nINFO: Configuration complete. See files in /root/staypuft_files/"
	print "INFO: Installation media can be found at: https://%s:8080/repos/rheldvd-el6" % fqdn
	print "INFO: Repositories are available at: http://%s:8080/repos" % fqdn
	print "SUCCESS: Staypuft is ready to be configured, run 'staypuft-installer'"

if __name__ == "__main__":
	check_root()
	devnull = open('/dev/null', 'w')
	print "\nStayPuft OpenStack PoC Configuration Script v0.1"
	fqdn = configure_system()
	create_ext_repos(fqdn)
	create_int_repos(fqdn)
	configure_vhost(fqdn)
	begin_install(fqdn)