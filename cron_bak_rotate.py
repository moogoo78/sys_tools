#!/usr/bin/env python
# -.- coding: utf-8 -.-

# v0.2
# python cron_bak_rotate.py -uroot -p123456 -y /usr/local/mysql/bin/mysqldump -n qllweb -t /tmp/bak fooweb -d ~/fooweb/media

from optparse import OptionParser
import sys
import os, os.path
import time
import subprocess

"""
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWD = '123456'
DB_NAME = 'dbname'

BAK_DIR = '/tmp/bak_test'

CMD_MYSQL = '/usr/local/mysql/bin/mysql'
CMD_MYSQLDUMP = '/usr/local/mysql/bin/mysqldump'
"""

TIME_STR = time.strftime('%Y%m%d-%H%M%S')

def main(proj_name, opts):

    bak_dir = os.path.join(opts.target, proj_name)
    if not os.path.exists(bak_dir):
        os.mkdir(bak_dir)

    ### dump sql
    fname = '%s_%s.bz2' % (proj_name, TIME_STR)
    dir_first = os.path.join(bak_dir, 'bak_0')
    dir_last = os.path.join(bak_dir, 'bak_10')
    if not os.path.exists(dir_first):
        os.mkdir(dir_first)

    print '[%s]' % proj_name
    cmd = '%s -u%s -p%s -h%s %s | bzip2 -9 > %s' % (
        opts.cmd_mysqldump,
        opts.dbuser,
        opts.dbpasswd,
        opts.dbhost,
        opts.dbname,
        os.path.join(dir_first, fname))
    print 'dumping sql...'
    subprocess.call(cmd, shell=True)

    ### rsync dada
    if opts.data:
        print 'rsync data...'
        subprocess.call('rsync -av %s %s' % (opts.data, bak_dir), shell=True)
        data_name = opts.data.split('/')[-1]
        data_src = os.path.join(bak_dir, data_name)
        data_tgt = os.path.join(dir_first, data_name + '_' + TIME_STR)
        subprocess.call('cp -aR %s %s' % (data_src, data_tgt), shell=True)

    # purge oldest
    if os.path.exists(dir_last):
        subprocess.call('rm -rf %s' % dir_last, shell=True)

    ## rotate backup
    for i in range(9, -1, -1):
        tmp = os.path.join(bak_dir, 'bak_' + str(i))
        tmp1 = os.path.join(bak_dir, 'bak_'+ str(int(i)+1))
        if os.path.exists(tmp):
            os.rename(tmp, tmp1) 
            print 'mv %s to %s' % (tmp, tmp1)


if __name__ == '__main__':
    usage = "usage: %prog"
    parser = OptionParser(usage=usage)
    parser.add_option('-t', '--target', dest='target')
    parser.add_option('-s', '--dbhost', dest='dbhost', default='localhost')
    parser.add_option('-u', '--dbuser', dest='dbuser')
    parser.add_option('-p', '--dbpasswd', dest='dbpasswd')
    parser.add_option('-n', '--dbname', dest='dbname')
    #parser.add_option('-m', '--mysql', dest='cmd_mysql', default='mysql')
    parser.add_option('-y', '--mysqldump', dest='cmd_mysqldump', default='mysqldump')
    parser.add_option('-d', '--data', dest='data')

    (options, args) = parser.parse_args()
    if options.dbuser and \
            options.dbpasswd and \
            options.dbname and \
            options.target and \
            args:
        main(proj_name=args[0], opts=options)
    else:
        print ('requried option not supplied\n-h for help')
        #parser.print_help()


