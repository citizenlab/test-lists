# Services

This data format

**version** 0.1

### name

The name of the service whose address is being listed.

When nested nodes should be separated by a `/` . For example if listing tor
bridges, the name shall be `tor/bridges`.

### category_code

A code taken from the list of categories described in
`lists/00-LEGEND-category_codes.csv`.

### date_added

This is the date in which the item was added to this repository.

### date_published

This is the date in which such URL was made available publicly. By this we mean
the point in time when there was an internet service listing such address whose
access is not restricted by the owner of the resource.

For example this can be when the Tor bridge IP address is pushed to the public
git repository or when the nameserver of a popular chat app starts listing a
new IP.

This date may also coincide with the value of date_added or it may be used in a
way that is context specific, but such difference should be documented in the
data format specification of the specific service.

### data_format_version

This is the data format version this address is using.

### source

This is the source of the address information, can either be the author of the
git commit or it may be the organisation running the website from where it was
taken.

### notes

Extra information on this address.
