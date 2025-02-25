#!/bin/awk -f
NR == 1 {
    # Sitename
    start = index($2, "/archive/")+9
    nameLength = length($2)-22 - start
    printf substr($2, start, nameLength)
    printf "-"
    # First date
    printf substr($2, length($2)-21, 10)
    printf "-"
}
END {
    # Last date
    printf substr($2, length($2)-21, 10)
}
