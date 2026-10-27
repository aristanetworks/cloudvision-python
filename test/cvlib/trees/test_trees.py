# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest

from cloudvision.cvlib.exceptions import (
    TreeCycleException,
    TreeParentNotFoundException,
    TreeSelfLoopException,
)
from cloudvision.cvlib.trees import build_trees, merge_into_child, merge_all, to_node

check_merge = [
    # name
    # parent data
    # child data
    # ignored keys
    # expected merged data
    [
        "missing and empty values inherited from parent",
        {
            "missing": "parent",
            "none": "parent",
            "empty_string": "parent",
            "empty_list": ["parent"],
            "empty_dict": {"parent": True},
        },
        {
            "none": None,
            "empty_string": "",
            "empty_list": [],
            "empty_dict": {},
        },
        [],
        {
            "missing": "parent",
            "none": "parent",
            "empty_string": "parent",
            "empty_list": ["parent"],
            "empty_dict": {"parent": True},
        },
    ],
    [
        "child values take precedence",
        {"string": "parent", "list": ["parent"], "nested": {"value": "parent"}},
        {"string": "child", "list": ["child"], "nested": {"value": "child"}},
        [],
        {"string": "child", "list": ["child"], "nested": {"value": "child"}},
    ],
    [
        "nested dictionaries are merged recursively",
        {"nested": {"inherited": "parent", "preserved": "parent"}},
        {"nested": {"preserved": "child"}},
        [],
        {"nested": {"inherited": "parent", "preserved": "child"}},
    ],
    [
        "ignored keys are not inherited at any depth",
        {"ignored": "parent", "nested": {"ignored": "parent", "value": "parent"}},
        {"nested": {"child": True}},
        ["ignored"],
        {"nested": {"child": True, "value": "parent"}},
    ],
    [
        "empty parent leaves child unchanged",
        {},
        {"value": "child"},
        [],
        {"value": "child"},
    ],
]


@pytest.mark.parametrize(
    "name, parent_data, child_data, ignore_keys, expected_data",
    check_merge,
)
def test_merge_int_child(name, parent_data, child_data, ignore_keys, expected_data):
    result = merge_into_child(parent_data, child_data, ignore_keys)

    assert result is child_data
    assert child_data == expected_data


@pytest.mark.parametrize(
    "child_data",
    [
        {},
        {"nested": {}},
        {"nested": None},
    ],
    ids=["missing", "empty-dictionary", "none"],
)
def test_merge_into_child_excludes_ignored_keys_from_inherited_dict(child_data):
    parent_data = {
        "nested": {
            "ignored": "parent",
            "value": "parent",
        },
    }

    result = merge_into_child(parent_data, child_data, ["ignored"])

    assert result == {"nested": {"value": "parent"}}


def test_to_node():
    data = {"parent": "root", "value": "child"}

    node = to_node("child", data, "port profile")

    assert node.name == "child"
    assert node.data is data
    assert node.item_type == "port profile"


check_merge_items = [
    # name
    # item data
    # ignored keys
    # expected merged items
    [
        "parent values are merged into descendants",
        {
            "root": {
                "parent": None,
                "region": "west",
                "settings": {"mtu": 1500},
            },
            "child": {
                "parent": "root",
                "region": "east",
                "settings": {"speed": "100G"},
            },
            "grandchild": {
                "parent": "child",
                "settings": {},
                "ignored": "grandchild",
            },
            "second-root": {"region": "north"},
        },
        ["parent", "ignored"],
        {
            "root": {
                "parent": None,
                "region": "west",
                "settings": {"mtu": 1500},
            },
            "child": {
                "parent": "root",
                "region": "east",
                "settings": {"mtu": 1500, "speed": "100G"},
            },
            "grandchild": {
                "parent": "child",
                "region": "east",
                "settings": {"mtu": 1500, "speed": "100G"},
                "ignored": "grandchild",
            },
            "second-root": {"region": "north"},
        },
    ],
]


@pytest.mark.parametrize(
    "name, item_data, ignore_keys, expected_items",
    check_merge_items,
)
def test_merge_all(name, item_data, ignore_keys, expected_items):
    items = {
        item_id: to_node(item_id, data)
        for item_id, data in item_data.items()
    }
    roots = []
    for item_id, node in items.items():
        parent_id = node.data.get("parent")
        if parent_id:
            node.parent = items[parent_id]
        else:
            roots.append(node)

    result = merge_all(roots, ignore_keys)

    assert result == expected_items
    assert all(data is items[item_id].data for item_id, data in result.items())


@pytest.mark.parametrize(
    "first_child_settings, mutate",
    [
        (
            {},
            # Set mtu to 9000
            lambda settings: settings.__setitem__("mtu", 9000),
        ),
        (
            {"speed": "10G"},
            # Append "child" to tags
            lambda settings: settings["tags"].append("child"),
        ),
    ],
    ids=["inherited-dictionary", "inherited-list"],
)
def test_merge_all_copies_inherited_mutable_values(first_child_settings, mutate):
    items = {
        "root": to_node(
            "root",
            {"settings": {"mtu": 1500, "tags": ["parent"]}},
        ),
        "first-child": to_node(
            "first-child",
            {"settings": first_child_settings},
        ),
        "second-child": to_node(
            "second-child",
            {"settings": {"speed": "100G"}},
        ),
    }
    items["first-child"].parent = items["root"]
    items["second-child"].parent = items["root"]

    result = merge_all([items["root"]], [])

    # Verify that the inherited values are copied, not shared
    assert result["first-child"]["settings"] is not result["root"]["settings"]
    assert (
        result["first-child"]["settings"]["tags"]
        is not result["root"]["settings"]["tags"]
    )

    mutate(result["first-child"]["settings"])
    # Verify that the original values are not mutated
    assert result["root"]["settings"] == {"mtu": 1500, "tags": ["parent"]}
    assert result["second-child"]["settings"] == {
        "mtu": 1500,
        "speed": "100G",
        "tags": ["parent"],
    }


check_build_trees = [
    # name
    # item data
    # expected roots
    # expected parent relationships
    # expected descendants
    [
        "nodes are linked into trees",
        {
            "grandchild": {"parent": "child"},
            "root": {},
            "child": {"parent": "root"},
            "second-root": {"parent": None},
        },
        ["root", "second-root"],
        {"grandchild": "child", "root": None, "child": "root", "second-root": None},
        {"root": ["child", "grandchild"], "second-root": []},
    ],
]


@pytest.mark.parametrize(
    "name, item_data, expected_roots, expected_parents, expected_descendants",
    check_build_trees,
)
def test_build_trees(
    name,
    item_data,
    expected_roots,
    expected_parents,
    expected_descendants,
):
    items = {
        item_id: to_node(item_id, data, "port profile")
        for item_id, data in item_data.items()
    }

    roots = build_trees(items, "parent")

    assert [node.name for node in roots] == expected_roots
    for item_id, parent_id in expected_parents.items():
        expected_parent = items[parent_id] if parent_id else None
        assert items[item_id].parent is expected_parent
    for root_id, descendant_ids in expected_descendants.items():
        assert [node.name for node in items[root_id].descendants] == descendant_ids


check_build_trees_errors = [
    # name
    # item parent relationships
    # expected error
    [
        # child -> child
        "node is its own parent",
        {"child": "child"},
        TreeSelfLoopException("child", "profile"),
    ],
    [
        # child -> <missing parent>
        "parent does not exist",
        {"child": "missing"},
        TreeParentNotFoundException(
            "child",
            "missing",
            "profile",
        ),
    ],
    [
        # first -> second -> first
        "two-node cycle",
        {"first": "second", "second": "first"},
        TreeCycleException(
            ["second", "first", "second"],
            "profile",
        ),
    ],
    [
        # first -> second -> third -> first
        "three-node cycle",
        {"first": "second", "second": "third", "third": "first"},
        TreeCycleException(
            ["third", "first", "second", "third"],
            "profile",
        ),
    ],
]


@pytest.mark.parametrize(
    "name, relationships, expected_error",
    check_build_trees_errors,
)
def test_build_trees_errors(name, relationships, expected_error):
    items = {
        item_id: to_node(
            item_id,
            {"parent": parent_id},
            "profile",
        )
        for item_id, parent_id in relationships.items()
    }

    with pytest.raises(type(expected_error), match=str(expected_error)):
        build_trees(items, "parent")
