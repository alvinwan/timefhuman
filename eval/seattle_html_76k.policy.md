# Seattle Gold Policy

`seattle_html_76k` is treated as a gold extraction corpus for real date/time-like content, including metadata dates.

Included:

- maintenance-comment dates such as `08-07-2013`, `7-10-2013`, and `6-3-2014`
- article timestamps such as `Jan 6 2016 at 10:13AM`
- prose time ranges such as `7-11pm`
- URL dates such as `2013-01-23`

Excluded:

- asset or library version numbers such as `1.3.4` and `1.7.1`
- shorter partial matches when a fuller timestamp is present, such as standalone `Wed`
- generic prose words such as `night` when they appear inside compounds like `one-night-only`
- image or layout dimensions such as `648 H` and `960 H`
