import re

ctx.alog("Removing all currently unused EOSs from /mnt/flash")

# Get current boot image
# runDeviceCommands takes a list of commands to run on the device, and receives a list of responses
# Each command response has an 'error' and 'response' entry, where the error will be any error with
# running the command, e.g. insufficient permissions, and the response will be the output of the
# successful command. The error will be the empty string in the case of a successfully run command
cmdOut = ctx.runDeviceCmds(["enable", "show boot"])
# show boot command output is at index 1 of the returned list as it is the second command to run.
# We want the output of the command, so we extract the response field
showbootResp = cmdOut[1]["response"]
# Show boot response is a dict. The eos boot image is under 'softwareImage'
eosBootImageFull = showbootResp["softwareImage"]
# The eos boot image is in the form of 'flash:/EOS.swi'. Only the image name is of interest,
# so split on the / to get 'EOS.swi'
eosBootImage = eosBootImageFull.split("/")[1]

# This command returns a large response message
cmdOut = ctx.runDeviceCmds(["enable", "dir flash:EOS*"])
# Extract the first response message from the 'dir flash:EOS*' command, there will be only one
eosListTxt = cmdOut[1]["response"]["messages"][0]
# This is a long string, so we need to extract all instances of EOS<X>.swi into a list
eosList = re.findall(r'EOS.*\.swi', eosListTxt)

# If there are no unused images, exit after logging
if len(eosList) == 1:
    ctx.alog("No unused EOS images to remove")
else:
    # For each of these swi's not use for boot, delete them
    for eos in eosList:
        if eos != eosBootImage:
            ctx.alog("Removing unused eos image {}".format(eos))
            cmd = "delete flash:" + eos
            cmdOut = ctx.runDeviceCmds(["enable", cmd])

    ctx.alog("All unused EOS images from /mnt/flash removed")
