#!/usr/bin/env bash

#############
# Constants #
#############

PROJECT_ROOT=$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )
MANAGE=${PROJECT_ROOT}/manage.py
FIXTURES_FOLDER=${PROJECT_ROOT}/layout/fixtures

FARM_BACKUP_FIXTURE=old_farm_data
FARM_BACKUP_FILEPATH=${FIXTURES_FOLDER}/${FARM_BACKUP_FIXTURE}.json
LAYOUT_BACKUP_FIXTURE=old_layout_data
LAYOUT_BACKUP_FILEPATH=${FIXTURES_FOLDER}/${LAYOUT_BACKUP_FIXTURE}.json

TEST_NAMES=(unconfigured tray bay aisle)

#########
# Setup #
#########

# Save the old farm and layout data in fixtures
echo "Backing up data..."
python ${MANAGE} dumpdata farms --output=$FARM_BACKUP_FILEPATH
python ${MANAGE} dumpdata layout --output=$LAYOUT_BACKUP_FILEPATH

#########
# Tests #
#########

for test_name in ${TEST_NAMES[*]}; do
    FIXTURE_NAME=${test_name}_farm.json
    SETTINGS_FILE=layout.test_settings.$test_name
    echo "Preparing '$test_name' tests"
    python ${MANAGE} loaddata $FIXTURE_NAME >/dev/null
    # The --noinput option is broken in django 1.8, so this is a workaround
    yes N | python ${MANAGE} makemigrations layout >/dev/null
    python ${MANAGE} migrate --noinput >/dev/null
    python ${MANAGE} test layout --settings=$SETTINGS_FILE
done

###########
# Cleanup #
###########

# Reload the data we backed up in setup
echo "Restoring old data..."
python ${MANAGE} loaddata $FARM_BACKUP_FIXTURE >/dev/null
yes N | python ${MANAGE} makemigrations layout >/dev/null
python ${MANAGE} migrate --noinput >/dev/null
python ${MANAGE} loaddata $LAYOUT_BACKUP_FIXTURE
rm $FARM_BACKUP_FILEPATH
rm $LAYOUT_BACKUP_FILEPATH
