# Copyright (c) 2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the COPYING file.

import pytest
import json

from cloudvision.cvlib import (
    get_tag_value_from_resolver,
    validate_resolver
)


validateResolverCases = [
    # name
    # resolvers list
    # expected inputs
    # expected tag value
    [
        "test resolver lists with all valid resolvers",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 2
                        }
                    },
                    "tags": {
                        "query": "device:mleaf2"
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, {'memberLeafsInfo': {'nodeId': 2}}],
        ["mleaf1", "mleaf2"],
    ],
    [
        "test resolver lists with a blank tags query resolver",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 2
                        }
                    },
                    "tags": {
                        "query": ""
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, None],
        ["mleaf1", None],
    ],
    [
        "test resolver lists with a missing tags query resolver",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 2
                        }
                    },
                    "tags": {
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, None],
        ["mleaf1", None],
    ],
    [
        "test resolver lists with a missing tags resolver",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 2
                        }
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, None],
        ["mleaf1", None],
    ],
    [
        "test resolver lists with a empty inputs resolver",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                {
                    "inputs": {
                    },
                    "tags": {
                        "query": "device:mleaf2"
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, None],
        ["mleaf1", None],
    ],
    [
        "test resolver lists with a missing inputs resolver",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                {
                    "tags": {
                        "query": "device:mleaf2"
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, None],
        ["mleaf1", None],
    ],
    [
        "test resolver lists with empty resolver",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                {},
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 2
                        }
                    },
                    "tags": {
                        "query": "device:mleaf2"
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, None, {'memberLeafsInfo': {'nodeId': 2}}],
        ["mleaf1", None, "mleaf2"],
    ],
    [
        "test resolver lists with null resolver",
        """
            [
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 1
                        }
                    },
                    "tags": {
                        "query": "device:mleaf1"
                    }
                },
                null,
                {
                    "inputs": {
                        "memberLeafsInfo": {
                            "nodeId": 2
                        }
                    },
                    "tags": {
                        "query": "device:mleaf2"
                    }
                }
            ]
        """,
        [{'memberLeafsInfo': {'nodeId': 1}}, None, {'memberLeafsInfo': {'nodeId': 2}}],
        ["mleaf1", None, "mleaf2"],
    ],
]


@pytest.mark.parametrize('name, resolvers, exp_inputs, exp_tags', validateResolverCases)
def test_validate_resolvers(name, resolvers, exp_inputs, exp_tags):
    resolvers = json.loads(resolvers)
    inputs_list = []
    tag_list = []
    for resolver in resolvers:
        inputs, tag = validate_resolver(resolver)
        inputs_list.append(inputs)
        tag_list.append(tag)
    assert list(inputs_list) == list(exp_inputs)
    assert list(tag_list) == list(exp_tags)
