#!/bin/bash
# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

# egrep that comes with our Linux distro doesn't like \d, so use [0-9]
notice='Copyright \(c\) 20[0-9][0-9] Arista Networks, Inc.'
apacheNotice='Use of this source code is governed by the Apache License 2.0'
apacheNoticeSource='that can be found in the COPYING file.'
confidential='Confidential and Proprietary'
generatedCodePaths='(^arista|^fmp).*'
copyrightCheck='.*(check_copyright.sh)'

files=`git diff-tree --no-commit-id --name-only --diff-filter=ACMR -r HEAD | \
	egrep '\.(go|proto|py|sh)$' | \
	grep -v '_pb2\.py$' | \
	grep -v '_pb2_grpc\.py$' |\
	grep -v 'docsrc/'`
status=0

for file in $files; do
	if egrep -q "$confidential" $file ; then
		# Need to omit the check_copyright script from this check as it will always fail
		if [[ "$file" =~ $copyrightCheck ]] ; then
			continue
		fi
		echo "$file: use of confidential material per copyright notice"
		status=1
	fi
	if ! egrep -q "$notice" $file; then
		echo "$file: missing or incorrect copyright notice for Arista"
		status=1
	fi
	if [[ "$file" =~ $generatedCodePaths ]]; then
		continue
	fi
	if ! egrep -q "$apacheNotice" $file ; then
		echo "$file: missing or incorrect Apache Licence 2.0 notice"
		status=1
	fi
	if ! egrep -q "$apacheNoticeSource" $file ; then
		echo "$file: missing or incorrect Apache Licence 2.0 notice COPYING directive"
		status=1
	fi
done

exit $status
