#!/bin/bash

# Reset jcom-test and copy everything from jcom-pp to jcom-test.

set -e

# Delete all files from test, and replace with files from pre-production
j_test=/home/wjs/janeway
j_pp=/home/wjs/janeway-pp
rm -rf $j_test/src/files/*
rsync --archive --delete $j_pp/src/files/ $j_test/src/files/

# Let's store postgresql pwds (temporarily) in pgpass
pgpass=$HOME/.pgpass
can_delete_pgpass=yes
if [[ -e $pgpass ]]
then
    echo "Warning: appending pwd to $pgpass"
    can_delete_pgpass=no
else
    touch $pgpass
    chmod 0600 $pgpass
fi

# Dump test db (just in case...)
j_test_settings=$j_test/src/core/settings.py
j_test_dump=/tmp/j_test.sql
j_test_db_name=$(sed -n -E 's/ +"NAME": "(.+)",/\1/p' $j_test_settings)
j_test_db_user=$(sed -n -E 's/ +"USER": "(.+)",/\1/p' $j_test_settings)
j_test_db_password=$(sed -n -E 's/ +"PASSWORD": "(.+)",/\1/p' $j_test_settings)
j_test_db_host=$(sed -n -E 's/ +"HOST": "(.+)",/\1/p' $j_test_settings)
echo "$j_test_db_host:5432:$j_test_db_name:$j_test_db_user:$j_test_db_password" >> $pgpass
pg_dump -U $j_test_db_user -h $j_test_db_host $j_test_db_name --file=$j_test_dump --clean --create

# Dump pre-production db
j_pp_settings=$j_pp/src/core/settings.py
j_pp_dump=/tmp/j_pp.sql
j_pp_db_name=$(sed -n -E 's/ +"NAME": "(.+)",/\1/p' $j_pp_settings)
j_pp_db_user=$(sed -n -E 's/ +"USER": "(.+)",/\1/p' $j_pp_settings)
j_pp_db_password=$(sed -n -E 's/ +"PASSWORD": "(.+)",/\1/p' $j_pp_settings)
j_pp_db_host=$(sed -n -E 's/ +"HOST": "(.+)",/\1/p' $j_pp_settings)
echo "$j_pp_db_host:5432:$j_pp_db_name:$j_pp_db_user:$j_pp_db_password" >> $pgpass
pg_dump -U $j_pp_db_user -h $j_pp_db_host $j_pp_db_name --file=$j_pp_dump --clean --create

# Restore pre-production schema/data into test DB
psql --echo-errors --quiet -U $j_pp_db_user -h $j_pp_db_host $j_pp_db_name < $j_pp_dump
