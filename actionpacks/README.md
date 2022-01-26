# CloudVision Custom Python3 Script Action Packs

## **Note**: Please see <https://github.com/aristanetworks/cloudvision-python-actions> for up-to-date actions

## **Note**: This is only available from CloudVision 2021.3.0 onwards

## Overview

Here are a number of example Python3 scripts in action pack form to serve as reference to those designing their own user scripts.  
These action packs are also able to be uploaded to a CloudVision cluster, where they can be used as needed, or duplicated and customised.  
Those action packs listed in `bundled.yaml` are _bundled by default_ to CloudVision.

## How to Upload Action Packs to a CloudVision cluster

**Note**: This is method of uploading scripts is not yet available for CVaaS customers.

### Pre-requisites

* `tar`

### Steps

* `tar` up the action pack while you are in the `actionpacks` directory (or equivalent directory). The name of the tar is not important, but it is good practice to use the same name as the as the directory you are tarring, and include the version string.
* Use scp to copy the tar file over to any of the cvp nodes in the system.
* On the cvp node, upload the action pack via the the `actionpack_cli` tool

**Note**: This will upload the action pack as the `aerisadmin` user, which means that only the `aerisadmin` user will be able to modify or delete them (copies can still be made and modified/deleted by any user authorised to create actions).

To _avoid_ making an aeris admin gated script, it is advised to create a new action, and to copy the script and arguments wanted from the example in question.

### Example

**Note**: This example is using the `event-monitor` action pack, which is bundled by default

* `tar` up the action pack:

``` Shell
> tar cvf event-monitor-action-pack_1.0.0.tar event-monitor-action-pack
a event-monitor-action-pack
a event-monitor-action-pack/config.yaml
a event-monitor-action-pack/event-monitor
a event-monitor-action-pack/event-monitor/config.yaml
a event-monitor-action-pack/event-monitor/script.py
```

* `scp` action pack over to the cvp node

* `ssh` onto the node and run `/cvpi/tools/actionpack_cli event-monitor-action-pack_1.0.0.tar`
