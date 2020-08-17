# Copyright (c) 2020 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import logging
name = "cloudvision.Connector"


def process_notifs(stream, paths={}, keys={}, nominalKeys=None):
    """
    process_notifs consume the batch coming from stream and return them
    as a hierarchy of dataset, path, and keys. Allowing for faster access
    of a given time serie.
    """
    res = {}

    for batch in stream:
        dname = batch["dataset"]["name"]
        for notif in batch["notifications"]:
            time = notif["timestamp"]
            path = "/".join(notif["path_elements"])
            if paths and path not in paths:
                continue
            for key, value in notif["updates"].items():
                if keys and key not in keys:
                    continue
                value = __get_val(value, nominalKeys)
                res = __update_dict(res, dname, path, key, nominalKeys, value, time)
    return res


def __get_val(nominal, nomKeys):
    res = nominal
    if nomKeys is None:
        return res
    for k in nomKeys:
        if k not in res:
            logging.error(
                """
                Key  %s not found in json %s
                Full nominal %s
                Nominal key path %s
                """ % (k, res, nominal, nomKeys))
            return None
        res = res[k]
    return res


def __update_dict(resDict, dataset, path, key, nominalKeys, val, ts):
    entry = resDict.setdefault(dataset,
                               {}).setdefault(path,
                                              {}).setdefault(key, {})
    if nominalKeys:
        entry = entry.setdefault("/".join(nominalKeys), {})
    entry.setdefault("values", []).append(val)
    entry.setdefault("timestamps", []).append(ts)
    return resDict


def sort_dict(resDict):
    """
    sort_dict orders every timeseries in a hierarchy of dataset by its timestamps.
    """

    def sort_timeserie(timeserie):
        timeserie["values"], timeserie["timestamps"] = zip(*sorted(zip(
            timeserie["values"],
            timeserie["timestamps"]), key=lambda x: (x[1].seconds, x[1].nanos)))

    stack = [resDict]
    while stack:
        timeserie = stack.pop()
        if "values" in timeserie and "timestamps" in timeserie:
            sort_timeserie(timeserie)
        else:
            stack.extend(timeserie.values())
    return resDict
