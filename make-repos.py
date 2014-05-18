#!/usr/bin/env python

import xmlrpclib
import os
import getpass
import subprocess
import sys


def dump_channel(label):
    print "Dumping Channel: " + label
    print "Output Directory: " + OUTPUT_DIR + "/" + label
    outdir = OUTPUT_DIR + '/' + label
    subprocess.call(['mkdir', '-p', outdir])

    for pkg in client.channel.software.listLatestPackages(key, label):
        id = pkg.get('id')
        filename = client.packages.getDetails(key, pkg.get('id')).get('file')
        if local:
            path = client.packages.getDetails(key, pkg.get('id')).get('path')
            infile = '/var/satellite/' + path
            outfile = outdir + '/' + filename
            subprocess.call(['/bin/cp', infile, outdir])
        else:
            url = client.packages.getPackageUrl(key, pkg.get('id'))
            location = outdir + '/' + filename
            subprocess.call(
                ['wget', '-O', location, url], stdout=devnull, stderr=devnull)


def check_createrepo():
    try:
        subprocess.check_call(
            ['/usr/bin/createrepo', '--version'], stdout=devnull, stderr=devnull)
    except:
        return False
    return True


def parse_config(conf):
    SATELLITE_FQDN = None
    SATELLITE_USERNAME = None
    SATELLITE_PASSWORD = None
    OUTPUT_DIR = None

    try:
        for line in conf.readlines():
            if not "#" in line:
                if "SATELLITE_FQDN" in line:
                    line = line.strip()
                    value = line.split('=')
                    if len(value[1]) > 0:
                        SATELLITE_FQDN = value[1]
                if "SATELLITE_USERNAME" in line:
                    line = line.strip()
                    value = line.split('=')
                    if len(value[1]) > 0:
                        SATELLITE_USERNAME = value[1]
                if "SATELLITE_PASSWORD" in line:
                    line = line.strip()
                    value = line.split('=')
                    if len(value[1]) > 0:
                        SATELLITE_PASSWORD = value[1]
                if "OUTPUT_DIR" in line:
                    line = line.strip()
                    value = line.split('=')
                    if len(value[1]) > 0:
                        OUTPUT_DIR = value[1]

    except:
        print "FATAL: Invalid repo_rc file. Please fix."
        sys.exit(1)

    return SATELLITE_FQDN, SATELLITE_USERNAME, SATELLITE_PASSWORD, OUTPUT_DIR

if __name__ == "__main__":

    local = False
    devnull = open('/dev/null', 'w')

    try:
        conf = open(".repo_rc")
    except:
        conf = None

    if conf:
        print "INFO: Configuration file found."
        SATELLITE_FQDN, SATELLITE_USERNAME, SATELLITE_PASSWORD, OUTPUT_DIR = parse_config(
            conf)

        if not SATELLITE_FQDN or not SATELLITE_USERNAME or not SATELLITE_PASSWORD or not OUTPUT_DIR:
            print "FATAL: Invalid repo_rc file. Please fix."
            sys.exit(1)
    else:
        print "INFO: No configuration file found.\n"
        SATELLITE_FQDN = raw_input('Satellite FQDN: ')
        SATELLITE_USERNAME = raw_input('Satellite Username: ')
        SATELLITE_PASSWORD = getpass.getpass()
        OUTPUT_DIR = raw_input('Output Directory: ')

    SATELLITE_URL = "http://" + SATELLITE_FQDN + "/rpc/api"

    hostname_ps = subprocess.Popen(['hostname', '-f'], stdout=subprocess.PIPE)
    LOCAL_HOSTNAME, err = hostname_ps.communicate()

    if "localhost" in SATELLITE_FQDN or SATELLITE_FQDN == LOCAL_HOSTNAME.rstrip():
        local = True

    try:
        subprocess.check_call(['mkdir', '-p', OUTPUT_DIR])
    except:
        print "FATAL: Unable to create temporary directory (%s)" % OUTPUT_DIR
        sys.exit(1)

    print "\nConnecting to: %s..." % SATELLITE_URL
    client = xmlrpclib.Server(SATELLITE_URL, verbose=0)

    try:
        key = client.auth.login(SATELLITE_USERNAME, SATELLITE_PASSWORD)
    except:
        print "FATAL: Unable to login with provided credentials."
        sys.exit(1)

    print "SUCCESS: Dumping channels to %s:\n" % OUTPUT_DIR

    if not local:
        print "*** WARNING: Fetching files over the network, this may take some time! ***\n"
    else:
        print "*** INFO: Fetching files from the local Satellite server ***\n"

    for chan in client.channel.listSoftwareChannels(key):
        label = chan.get('label')
        if label == 'rhel-x86_64-server-6':
            dump_channel(label)
        if label == 'rhel-x86_64-server-ha-6':
            dump_channel(label)
        if label == 'rhel-x86_64-server-lb-6':
            dump_channel(label)
        if label == 'rhel-x86_64-server-6-mrg-messaging-2':
            dump_channel(label)
        if label == 'rhel-x86_64-server-6-ost-4':
            dump_channel(label)
        if label == 'rhel-x86_64-server-rh-common-6':
            dump_channel(label)
        if label == 'rhel-x86_64-server-6-rhscl-1':
            dump_channel(label)

    client.auth.logout(key)

    print "\nINFO: Now running createrepo..."
    if check_createrepo():
        devnull = open('/dev/null', 'w')
        for dir in os.listdir(OUTPUT_DIR):
            this_dir = OUTPUT_DIR + '/' + dir
            subprocess.call(
                ['/usr/bin/createrepo', '--workers=4', this_dir], stdout=devnull, stderr=devnull)

        print "FINISHED: Successfully created repositories."
        sys.exit(0)
    else:
        print "ERROR: Unable to find the createrepo package, please install and run manually."
        sys.exit(1)
