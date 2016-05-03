Usage
=====

Updating URL lists
------------------

Some lists require you install some extra modules.

You can do so with:

```
# It's recommended you do this in a virtualenv
pip install requirements.txt
```

Then you can update the URL lists with:

```
# Update Italian gambling website list
./bin/update-official it/aams

# Update Italian BOFH list
./bin/update-official it/bofh

# Update Tor bridges list
./bin/update-services tor/bridges

# Update Tor directory authority list
./bin/update-services tor/dir_auths
```

Adding new URLs
---------------

To find the mappings of two letter country codes and country names see [this
file](https://github.com/citizenlab/test-lists/blob/master/lists/00-LEGEND-category_codes.csv):

```
./bin/add http://example.com/
```

You will guided through an interactive step by step process to add the URL.

What Is It?
===========

Contained are URL testing lists intended to help in testing URL censorship divided
by country codes.   In addition to these local lists the global list is
comprised of a wide range of internationally relevant and popular websites
including sites with content that is perceived to be provocative or
objectionable. Most of the websites on the global list are in English. In
contrast the local lists are designed individually for each country by regional
experts.  They have content representing a wide range of content categories at
the local and regional levels, and content in local languages. In countries
where Internet censorship has been reported, the local lists also include many
of the sites that are alleged to have been blocked.

Categories are divided among four broad themes:

* Political (This category is focused primarily on Web sites that express views
in opposition to those of the current government. Content more broadly related
to human rights, freedom of expression, minority rights, and religious
movements is also considered here.) 

* Social (This group covers material related
to sexuality, gambling, and illegal drugs and alcohol, as well as other topics
that may be socially sensitive or perceived as offensive).  

* Conflict/Security
(Content related to armed conflicts, border disputes, separatist movements, and
militant groups is included in this category).  

* Internet Tools (Web sites that
provide e-mail, Internet hosting, search, translation, Voice-over Internet
Protocol (VoIP) telephone service, and circumvention methods are grouped in
this category.)

More information about testing methodology can be found [here](https://opennet.net/oni-faq)

The only testing list that applies regionally (more than one country) is the
CIS testing list which is intended for testing former Commonwealth of
Independent States nations.

Lists are available in both CSV and JSON.

Please note that these lists are not the entirety of testing lists but rather just
the newest list for every unique country code.

License
========

All data is provided under Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International and available in full
[here](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode) and summarized
[here](https://creativecommons.org/licenses/by-nc-sa/4.0/)


