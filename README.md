## Panorama scripts for Open edX

This code is part of the Aulasneo Panorama project. It is intended to be
installed on an Open edX™ LMS instance. Its objective is to extract data from
Open edX™ data sources and to make it available for the Panorama resources for processing.

## Installation

Log in to the Open edX™ instance. If it is running from several severs, install it on the LMS.
It must have access to the configuration files, MySQL db, /edx/var/log/tracking directory
and the LMS manage commands usually located in /edx/app/edxapp/edx-platform/lms/djangoapps/courseware/management/commands/

As it must persist the session lifecycle, it should be installed in a system's user home (usually /home/ubuntu)
or other locations like /opt

Clone from Github repository to install.

```bash
git clone https://github.com/aulasneo/panorama-openedx-scripts.git
```
Add a line like this to the crontab in order to run the script once an hour:
```
0 * * * * sudo -u edxapp /path/to/panorama_upload_data
```

**NOTE**

Be aware that this will upload a potentially huge amount of data to your AWS account.
This can cause extra costs for data transfer and storage.

If you are not experienced, please contact us for support.

## Usage

`panorama_upload_data` is the shell script to be run periodically to extract the data.
It can be run manually, and certainly should be added to the crontab.

It works together with Aulasneo's Panorama© analytics system, so it makes no sense
using these scripts without having a Panorama© service available.

## Code components

- `panorama_upload_data`: main shell script
- `dump_structure.py`: 


## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.html)