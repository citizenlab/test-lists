## Test Lists v1 data format

The goal of this section is to outline the current dataformat for the testing
lists.

Ideally we would enrich this data format spec with also some additional notes
on the existing pain points and what are the current limitations.

### v1 data format

The testing lists are broken down into CSV files, which are named as:
* `global.csv` for testing lists that apply to all countries
* `[country_code].csv` for country specific lists, where `country_code` is the
  lowercase
  [ISO3166](https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes) alpha
  2 country code. The only exception is the `cis` category code that is
  for Commonwealth of Independent States nations.

Each CSV file contains the following columns:

* `url` - Full URL of the resource, which must match the following regular expression:
```
re.compile(
r'^(?:http)s?://' # http:// or https://
r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
r'(?::\d+)?' # optional port
r'(?:/?|[/?]\S+)$', re.IGNORECASE)
```
* `category_code` - Category code (see current category codes)
* `category_description` - Description of the category
* `date_added` - [ISO 8601](https://en.wikipedia.org/wiki/ISO_8601) timestamp of when it was added to the list in the format `YYYY-MM-DD`
* `source` - opaque string representing the name of the person that added it to the list
* `notes` - opaque string with notes about this string

### v1 category codes

* Alcohol & Drugs,ALDR
* Religion,REL
* Pornography,PORN
* Provocative Attire,PROV
* Political Criticism,POLR
* Human Rights Issues,HUMR
* Environment,ENV
* Terrorism and Militants,MILX
* Hate Speech,HATE
* News Media,NEWS
* Sex Education,XED
* Public Health,PUBH
* Gambling,GMB
* Anonymization and circumvention tools,ANON
* Online Dating,DATE
* Social Networking,GRP
* LGBT,LGBT
* File-sharing,FILE
* Hacking Tools,HACK
* Communication Tools,COMT
* Media sharing,MMED
* Hosting and Blogging Platforms,HOST
* Search Engines,SRCH
* Gaming,GAME
* Culture,CULTR
* Economics,ECON
* Government,GOVT
* E-commerce,COMM
* Control content,CTRL
* Intergovernmental Organizations,IGO
* Miscellaneous content,MISC

## v1.5 data format

The goal of the v1.5 data format is to come up with an incremental set of
changes to the lists formats such that it's possible to relatively easily
backport changes from upstream while we work on fully migrating over to the new
format.

Ideally it would include only the addition of new columns, without any
drammatic changes to minimize the likelyhood of conflicts when it's merged from
upstream.

* `url` - Full URL of the resource
* `category_code` - Category code (see current category codes)
* `category_description` - Description of the category
* `date_added` - ISO timestamp of when it was added
* `source` - string representing the name of the person that added it
* `notes` - a JSON string representing metadata for the URL (see URL Meta below)

### URL Meta

URL meta is a JSON encoded metadata column that expresses metadata related to
the a URL that is relevant to analysts permorning data analysis.

It should be extensible without needing to add new columns (adding or changing
columns has the potential of breaking parsers of CSV).

This field is optional and parsers should not expect it to be present or it
containing any of the specific keys defined below.

Defined keys
* `notes`: value coming from the existing notes column
* `context_*`: values representing context that's specific to the URL

