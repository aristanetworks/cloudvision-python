# Copyright (c) 2026 Arista Networks, Inc.  All rights reserved.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

"""Definition caches are optional, shared, and independent of assignments."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from functools import partial
from typing import Any, List
from unittest.mock import Mock

import pytest
from grpc import RpcError
from google.protobuf.timestamp_pb2 import Timestamp

from arista.tag.v2.services import (
    TagServiceStub,
    TagConfigServiceStub,
    TagStreamResponse,
    TagConfigStreamResponse,
    TagConfigSetSomeResponse,
)
from arista.tag.v2.tag_pb2 import (
    CREATOR_TYPE_USER,
    ELEMENT_TYPE_DEVICE,
    ELEMENT_TYPE_INTERFACE,
)
from cloudvision.cvlib.tags import Tags
from cloudvision.cvlib.constants import MAINLINE_WS_ID, TIMEOUT_REQUEST
from cloudvision.cvlib.exceptions import TagOperationException


@pytest.fixture(params=["Device", "Interface"])
def cache(request):
    kind = request.param
    ctx = Mock()
    ctx.getWorkspaceId.return_value = "workspace1"
    tags = Tags(ctx)
    etype = ELEMENT_TYPE_DEVICE if kind == "Device" else ELEMENT_TYPE_INTERFACE
    return tags, kind, etype


def definitionResponse(responseType, label, value, remove=False):
    response = responseType()
    response.value.key.label.value = label
    response.value.key.value.value = value
    if responseType is TagConfigStreamResponse:
        response.value.remove.value = remove
    return response


tagDefinitionLoadingCases: List[List[Any]] = [
    # name
    # mainline definitions
    # workspace updates
    # fetch stage to simulate an RPC failure ("mainline", "workspace", or None)
    # expected_definitions
    [
        "merge workspace changes",
        [("Role", "Leaf"), ("Role", "Spine"), ("Leaf-Domain", "1")],
        [
            ("Role", "Leaf", True),
            ("Leaf-Domain", "1", True),
            ("NodeId", "1", True),
            ("Role", "Edge-Router", False),
            ("Role", "Edge-Router", False),
        ],
        None,
        {"Role": {"Spine", "Edge-Router"}},
    ],
    [
        "empty definitions",
        [],
        [],
        None,
        {},
    ],
    [
        "mainline fetch failure",
        [],
        [],
        "mainline",
        {},
    ],
    [
        "mainline fetch failure with workspace additions",
        [],
        [("Role", "Leaf", False)],
        "mainline",
        {"Role": {"Leaf"}},
    ],
    [
        "workspace fetch failure with mainline non-empty",
        [("Role", "Leaf")],
        [],
        "workspace",
        {"Role": {"Leaf"}},
    ],
]


@pytest.mark.parametrize("name, mainlineTags, workspaceUpdates, failureStage, expected_definitions",
                         tagDefinitionLoadingCases, ids=[c[0] for c in tagDefinitionLoadingCases])
def test_definitionLoading(cache, monkeypatch, name, mainlineTags, workspaceUpdates,
                           failureStage, expected_definitions):
    tags, kind, etype = cache
    synced = Timestamp(seconds=123, nanos=456)
    syncGetter = Mock(return_value=synced)
    monkeypatch.setattr("cloudvision.cvlib.tags.getWorkspaceLastSynced", syncGetter)
    mainline, workspace = Mock(), Mock()
    tags.ctx.getApiClient.side_effect = {
        TagServiceStub: mainline, TagConfigServiceStub: workspace,
    }.__getitem__
    mainline.GetAll.return_value = [
        definitionResponse(TagStreamResponse, *tag) for tag in mainlineTags
    ]
    workspace.GetAll.return_value = [
        definitionResponse(TagConfigStreamResponse, *update) for update in workspaceUpdates
    ]
    if failureStage:
        def failedStream():
            responseType = (TagStreamResponse if failureStage == "mainline"
                            else TagConfigStreamResponse)
            yield definitionResponse(responseType, "Role", "Edge-Router")
            raise RpcError()

        failedClient = mainline if failureStage == "mainline" else workspace
        failedClient.GetAll.return_value = failedStream()
        with pytest.raises(RpcError):
            getattr(tags, f"_getAll{kind}TagDefinitions")()
        assert getattr(tags, f"{kind.lower()}TagDefinitions") is None
        if failureStage == "mainline":
            workspace.GetAll.assert_not_called()
        failedClient.GetAll.return_value = []
        mainline.GetAll.reset_mock()
        workspace.GetAll.reset_mock()
        syncGetter.reset_mock()

    result = getattr(tags, f"_getAll{kind}TagDefinitions")()
    assert result == expected_definitions
    assert getattr(tags, f"_getAll{kind}TagDefinitions")() is result
    syncGetter.assert_called_once_with(tags.ctx.getApiClient, "workspace1")
    mainRequest = mainline.GetAll.call_args.args[0]
    mainFilter = mainRequest.partial_eq_filter[0]
    assert mainRequest.time.end == synced
    assert mainFilter.key.workspace_id.value == MAINLINE_WS_ID
    assert mainFilter.key.element_type == etype
    assert mainFilter.creator_type == CREATOR_TYPE_USER
    assert not mainFilter.HasField("assigned")
    configFilter = workspace.GetAll.call_args.args[0].partial_eq_filter[0]
    assert configFilter.key.workspace_id.value == "workspace1"
    assert configFilter.key.element_type == etype
    mainline.GetAll.assert_called_once_with(mainRequest, timeout=TIMEOUT_REQUEST)
    assert workspace.GetAll.call_count == 1


tagDefinitionExistsCases: List[List[Any]] = [
    # name
    # definitions input (None means the definition cache is not loaded)
    # assignments input (assignment caches keyed by Device or Interface test kind)
    # exists_checks input (list of (label, value) tags to check)
    # expected_exists_results (booleans in the same order as exists_checks)
    # expected_assignment_lookups (calls to the assignment-cache getter)
    [
        "unloaded definition cache falls back to assignment cache",
        None,
        {
            "Device": {"device": {"Role": ["Leaf"]}},
            "Interface": {"device": {"Ethernet1": {"Role": ["Leaf"]}}},
        },
        [("Role", "Leaf"), ("Role", "Spine"), ("Leaf-Domain", "1")],
        [True, False, False],
        3,
    ],
    [
        "loaded empty cache is authoritative",
        {},
        {
            "Device": {"device": {"Role": ["Leaf"]}},
            "Interface": {"device": {"Ethernet1": {"Role": ["Leaf"]}}},
        },
        [("Role", "Leaf"), ("Role", "Spine"), ("Leaf-Domain", "1")],
        [False, False, False],
        0,
    ],
    [
        "loaded definitions include unassigned tags",
        {"Role": {"Spine"}},
        {
            "Device": {"device": {"Role": ["Leaf"]}},
            "Interface": {"device": {"Ethernet1": {"Role": ["Leaf"]}}},
        },
        [("Role", "Leaf"), ("Role", "Spine"), ("Leaf-Domain", "1")],
        [False, True, False],
        0,
    ],
]


@pytest.mark.parametrize("name, definitions, assignments, exists_checks, "
                         "expected_exists_results, expected_assignment_lookups",
                         tagDefinitionExistsCases, ids=[c[0] for c in tagDefinitionExistsCases])
def test_definitionExistenceAndFallback(cache, name, definitions, assignments, exists_checks,
                                        expected_exists_results,
                                        expected_assignment_lookups):
    tags, kind, _ = cache
    assignmentGetter = Mock(return_value=assignments[kind])
    setattr(tags, f"_getAll{kind}Tags", assignmentGetter)
    getattr(tags, f"_set{kind}TagDefinitions")(definitions)
    exists = getattr(tags, f"_{kind.lower()}TagExists")
    assert [exists(label, value) for label, value in exists_checks] == expected_exists_results
    assert assignmentGetter.call_count == expected_assignment_lookups
    tags.ctx.getApiClient.assert_not_called()


tagDefinitionCreationCases: List[List[Any]] = [
    # name
    # definitions caches
    # assignments caches
    # tag creates
    # simulated failure (None, "rpc", "item", or "stream")
    # failure tag ((label, value) to fail, or None)
    # configs per request (maximum definitions in each bulk API request)
    # expected definitions caches
    # expected api calls
    # expected errors (exception type, or None)
    [
        'existing definition skips creation',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Leaf')],
        None,
        None,
        1,
        {'Role': {'Leaf'}},
        [],
        None,
    ],
    [
        'single creation updates shared cache',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Spine')],
        None,
        None,
        1,
        {'Role': {'Leaf', 'Spine'}},
        [('Role', 'Spine')],
        None,
    ],
    [
        'single creation failure',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Spine')],
        'rpc',
        ('Role', 'Spine'),
        1,
        {'Role': {'Leaf'}},
        [('Role', 'Spine')],
        RpcError,
    ],
    [
        'single creation leaves cache unloaded',
        None,
        {'Device': {}, 'Interface': {}},
        [('Role', 'Spine')],
        None,
        None,
        1,
        None,
        [('Role', 'Spine')],
        None,
    ],
    [
        'bulk creation leaves cache unloaded',
        None,
        {'Device': {}, 'Interface': {}},
        [('Role', 'Core'), ('Role', 'RR')],
        None,
        None,
        10,
        None,
        [('Role', 'Core'), ('Role', 'RR')],
        None,
    ],
    [
        'bulk success',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Leaf'), ('Role', 'Core'), ('Role', 'RR')],
        None,
        None,
        10,
        {'Role': {'RR', 'Leaf', 'Core'}},
        [('Role', 'Core'), ('Role', 'RR')],
        None,
    ],
    [
        'chunked success',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Leaf'), ('Role', 'Core'), ('Role', 'RR')],
        None,
        None,
        1,
        {'Role': {'RR', 'Leaf', 'Core'}},
        [('Role', 'Core'), ('Role', 'RR')],
        None,
    ],
    [
        'bulk item error is not raised or cached',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Leaf'), ('Role', 'Core'), ('Role', 'RR')],
        'item',
        ('Role', 'RR'),
        10,
        {'Role': {'Leaf', 'Core'}},
        [('Role', 'Core'), ('Role', 'RR')],
        None,
    ],
    [
        'chunked item error is not raised or cached',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Leaf'), ('Role', 'Core'), ('Role', 'RR')],
        'item',
        ('Role', 'RR'),
        1,
        {'Role': {'Leaf', 'Core'}},
        [('Role', 'Core'), ('Role', 'RR')],
        None,
    ],
    [
        'interrupted batch is not cached',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Leaf'), ('Role', 'Core'), ('Role', 'RR')],
        'stream',
        ('Role', 'RR'),
        10,
        {'Role': {'Leaf'}},
        [('Role', 'Core'), ('Role', 'RR')],
        TagOperationException,
    ],
    [
        'completed chunk survives stream failure',
        {'Role': {'Leaf'}},
        {'Device': {}, 'Interface': {}},
        [('Role', 'Leaf'), ('Role', 'Core'), ('Role', 'RR')],
        'stream',
        ('Role', 'RR'),
        1,
        {'Role': {'Leaf', 'Core'}},
        [('Role', 'Core'), ('Role', 'RR')],
        TagOperationException,
    ],
]


@pytest.mark.parametrize("name, definitions, assignments, tag_creates, simulated_failure, "
                         "failure_tag, configs_per_request, expected_definitions, "
                         "expected_api_tags, "
                         "expected_error",
                         tagDefinitionCreationCases, ids=[c[0] for c in tagDefinitionCreationCases])
def test_definitionCreation(cache, name, definitions, assignments, tag_creates, simulated_failure,
                            failure_tag, configs_per_request, expected_definitions,
                            expected_api_tags,
                            expected_error):
    def setOne(request, timeout, simulated_failure, failure_tag, api_tags):
        key = request.value.key
        api_tags.append((key.label.value, key.value.value))
        if simulated_failure == "rpc" and (key.label.value, key.value.value) == failure_tag:
            raise RpcError()

    def setSome(request, timeout, simulated_failure, failure_tag, api_tags, requests):
        requests.append(request)
        api_tags.extend((config.key.label.value, config.key.value.value)
                        for config in request.values)
        for config in request.values:
            if (config.key.label.value, config.key.value.value) == failure_tag:
                if simulated_failure == "stream":
                    raise RpcError()
                if simulated_failure == "item":
                    yield TagConfigSetSomeResponse(key=config.key, error="failed")

    def create(tag_cache, etype, tag_creates, configs_per_request):
        if len(tag_creates) == 1:
            label, value = tag_creates[0]
            tag_cache._createTag(etype, label, value)
        else:
            tag_cache._createTags(etype, list(tag_creates), configsPerReq=configs_per_request)

    tags, kind, etype = cache
    definitions = deepcopy(definitions)
    getattr(tags, f"_set{kind}TagDefinitions")(definitions)
    other = Tags(Mock())
    getattr(other, f"_set{kind}TagDefinitions")(definitions)
    setattr(tags, f"_getAll{kind}Tags", Mock(return_value=assignments[kind]))
    client = tags.ctx.getApiClient.return_value
    api_tags = []
    requests = []
    client.Set.side_effect = partial(setOne, simulated_failure=simulated_failure,
                                     failure_tag=failure_tag, api_tags=api_tags)
    client.SetSome.side_effect = partial(setSome, simulated_failure=simulated_failure,
                                         failure_tag=failure_tag, api_tags=api_tags,
                                         requests=requests)

    if expected_error:
        with pytest.raises(expected_error):
            create(tags, etype, tag_creates, configs_per_request)
    else:
        create(tags, etype, tag_creates, configs_per_request)

    assert api_tags == expected_api_tags
    if not expected_api_tags:
        tags.ctx.getApiClient.assert_not_called()
    if len(tag_creates) > 1:
        assert len(requests) == ((len(expected_api_tags) + configs_per_request - 1)
                                 // configs_per_request)

    actual = getattr(tags, f"{kind.lower()}TagDefinitions")
    assert actual is definitions
    assert getattr(other, f"{kind.lower()}TagDefinitions") is definitions
    assert actual == expected_definitions
    if expected_definitions is not None:
        exists = getattr(other, f"_{kind.lower()}TagExists")
        for label, value in tag_creates:
            assert exists(label, value) == (value in expected_definitions.get(label, ()))


def test_unassignmentPreservesDefinition(cache):
    tags, kind, _ = cache
    definitions = {"Role": {"Spine"}}
    getattr(tags, f"_set{kind}TagDefinitions")(definitions)
    if kind == "Device":
        tags.relevantTagAssigns = {"device": {"Role": ["Spine"]}}
        tags._unassignDevTagInCache("device", "Role", "Spine")
        assert tags.relevantTagAssigns == {}
    else:
        tags.relevantIntfTagAssigns = {"device": {"Ethernet1": {"Role": ["Spine"]}}}
        tags._unassignIntfTagInCache("device", "Ethernet1", "Role", "Spine")
        assert tags.relevantIntfTagAssigns == {}
    assert definitions == {"Role": {"Spine"}}


concurrentTagDefinitionCases: List[List[Any]] = [
    # name
    # element type
    # tag values
    # expected definitions
    [
        "device distinct values",
        ELEMENT_TYPE_DEVICE,
        [str(index) for index in range(1, 501)],
        {"Leaf-Domain": {str(index) for index in range(1, 501)}},
    ],
    [
        "device overlapping values",
        ELEMENT_TYPE_DEVICE,
        [str(index % 50 + 1) for index in range(500)],
        {"Leaf-Domain": {str(index) for index in range(1, 51)}},
    ],
    [
        "interface distinct values",
        ELEMENT_TYPE_INTERFACE,
        [str(index) for index in range(1, 501)],
        {"Leaf-Domain": {str(index) for index in range(1, 501)}},
    ],
    [
        "interface overlapping values",
        ELEMENT_TYPE_INTERFACE,
        [str(index % 50 + 1) for index in range(500)],
        {"Leaf-Domain": {str(index) for index in range(1, 51)}},
    ],
]


@pytest.mark.parametrize("name, etype, tag_values, expected_definitions",
                         concurrentTagDefinitionCases,
                         ids=[case[0] for case in concurrentTagDefinitionCases])
def test_concurrentSharedLabelAdditions(name, etype, tag_values, expected_definitions):
    kind = "Device" if etype == ELEMENT_TYPE_DEVICE else "Interface"
    shared = {}
    contexts = [Tags(Mock()) for _ in range(8)]
    for context in contexts:
        context.ctx.getWorkspaceId.return_value = "workspace1"
        getattr(context, f"_set{kind}TagDefinitions")(shared)

    def add(index):
        contexts[index % len(contexts)]._createTag(etype, "Leaf-Domain", tag_values[index])

    # Schedule one task per tag value; each task attempts to create one definition.
    # Eight worker threads pick up tasks dynamically, so their task counts may differ.
    # Contexts are selected round-robin, and all contexts share the definition cache.
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(add, range(len(tag_values))))
    assert shared == expected_definitions
