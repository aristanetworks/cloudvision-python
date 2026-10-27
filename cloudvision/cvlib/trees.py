# Copyright (c) 2026 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

from copy import deepcopy

from anytree import LevelOrderIter, LoopError, Node

from .exceptions import (
    TreeCycleException,
    TreeParentNotFoundException,
    TreeSelfLoopException,
)


def merge_into_child(parent: dict, child: dict, ignore_keys: list[str], path: list[str] = None):
    """
    Merge values from ``parent`` into ``child`` when they are missing or empty in ``child``.

    Nested dictionaries are merged recursively. Inherited values are deep-copied
    so mutable values are not shared between parent and child. The ``child``
    dictionary is modified in place. Keys in ``ignore_keys`` are not merged.

    :param parent: Dictionary containing fallback values.
    :type parent: dict
    :param child: Dictionary into which fallback values are merged.
    :type child: dict
    :param ignore_keys: Keys to exclude from the merge at every nesting level.
    :type ignore_keys: list[str]
    :param path: Path of keys traversed during a recursive merge.
    :type path: list[str] or None
    :return: The merged ``child`` dictionary.
    :rtype: dict
    """
    # If falsey, nothing to merge into b (None or empty dict)
    if not parent:
        return child
    if path is None:
        path = []
    for key in parent:
        if key in ignore_keys:
            continue

        if key in child and child[key] not in [None, "", [], {}]:
            if isinstance(parent[key], dict) and isinstance(child[key], dict):
                merge_into_child(parent[key], child[key], ignore_keys, path + [str(key)])
        else:
            if isinstance(parent[key], dict):
                child[key] = {}
                merge_into_child(parent[key], child[key], ignore_keys, path + [str(key)])
            else:
                child[key] = deepcopy(parent[key])
    return child


def merge_all(roots: list[Node], ignore_keys: list[str]) -> dict[str, dict]:
    """
    Merge each parent item's data into its descendants.

    The returned items are keyed by node name. Keys in ``ignore_keys`` are not
    merged. Mutations are performed in place, so each node's data contains the
    merged values.

    :param roots: Root nodes of the trees to merge.
    :type roots: list[anytree.Node]
    :param ignore_keys: Keys to exclude from the merge at every nesting level.
    :type ignore_keys: list[str]
    :return: Node data keyed by node name.
    :rtype: dict[str, dict]
    """
    items = {}
    for root in roots:
        # Do a breadth-first traversal from each root and merge the parent into the child
        for node in LevelOrderIter(root):
            if node.parent:
                merged = merge_into_child(node.parent.data, node.data, ignore_keys)
                items[node.name] = merged
            else:
                items[node.name] = node.data
    return items


def _report_cycle(child: Node, parent: Node, item_type: str) -> None:
    """
    Report a cycle created by linking ``child`` to ``parent``.

    :param child: Child node that closes the cycle.
    :type child: anytree.Node
    :param parent: Proposed parent node in the cycle.
    :type parent: anytree.Node
    :param item_type: Type name used to describe the items in the error.
    :type item_type: str
    :raises TreeCycleException: Always, with the complete cycle path.
    """
    # start at the parent and work towards the child
    current = parent

    # build up the path so we can show the user what the cycle is
    cycle = [child.name]
    while current is not child:
        cycle.append(current.name)
        current = current.parent

    # complete the cycle
    cycle.append(child.name)
    raise TreeCycleException(cycle, item_type)


def to_node(id: str, data: dict, item_type: str = "") -> Node:
    """
    Create a node from an identifier and its associated data.

    The identifier is used as the node name.

    :param id: Identifier to use as the node name.
    :type id: str
    :param data: Data associated with the node.
    :type data: dict
    :param item_type: Type name used to describe the item in errors.
    :type item_type: str
    :return: A node containing ``data`` and ``item_type``.
    :rtype: anytree.Node
    """
    return Node(id, data=data, item_type=item_type)


def build_trees(items: dict[str, Node], parent_key: str) -> list[Node]:
    """
    Build trees from a flat dictionary of nodes.

    Each dictionary key is an item identifier, and each value is its node.
    The value of ``parent_key`` in a node's data identifies its parent. Nodes
    without a parent are returned as roots.

    The following relationships are rejected:

    1. An item that is its own parent.
    2. An item whose parent does not exist.
    3. An item whose parent is one of its descendants.

    :param items: Nodes keyed by item identifier.
    :type items: dict[str, anytree.Node]
    :param parent_key: Key in each node's data that identifies its parent.
    :type parent_key: str
    :return: Root nodes of the resulting trees.
    :rtype: list[anytree.Node]
    :raises TreeSelfLoopException: If an item identifies itself as its parent.
    :raises TreeParentNotFoundException: If an item's parent is absent from ``items``.
    :raises TreeCycleException: If a parent-child relationship creates a cycle.
    """
    # These are the tree roots. There can be more than one.
    roots: list[Node] = []

    for item_id, node in items.items():
        parent_id = node.data.get(parent_key)

        # If the node has no parent, it is a root node
        if not parent_id:
            roots.append(node)
            continue

        # 1. Check for self loop
        if parent_id == item_id:
            raise TreeSelfLoopException(item_id, node.item_type)

        # 2. Check if parent exists
        if parent_id not in items:
            raise TreeParentNotFoundException(item_id, parent_id, node.item_type)

        # Link child to the parent, cycle detection is performed
        try:
            items[item_id].parent = items[parent_id]
        except LoopError:
            _report_cycle(items[item_id], items[parent_id], node.item_type)
    return roots
