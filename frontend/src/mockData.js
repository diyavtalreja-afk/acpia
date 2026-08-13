export const caseMock = {
  "files": 12,
  "flags": {
    "total": 12,
    "high": 2,
    "medium": 8,
    "low": 2
  },
  "risk": {
    "score": 60,
    "label": "REVIEW",
    "flags_open": 12
  },
  "last_scan": {
    "id": 64,
    "started_at": "2026-08-11T12:02:58+00:00",
    "finished_at": "2026-08-11T12:02:59+00:00",
    "status": "done",
    "files_total": 12,
    "files_processed": 12,
    "seizure_ts": "2026-08-01T10:00:00+05:30",
    "reference_ts": "2026-08-04T09:00:00+05:30"
  }
};
export const flagsMock = {
  "flags": [
    {
      "id": 4930,
      "file_id": 65601,
      "severity": "high",
      "score": 70,
      "explanation": "Flagged photo_03.png \u2014 high risk (70/100). Triggered 2 rule(s): \u2022 Byte-identical to a known flagged file (mock DB) \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "photo_03.png",
      "path": "photo_03.png",
      "rules": [
        {
          "rule": "hash_match_exact",
          "points": 50,
          "detail": "Known entry MOCK-EXACT-01",
          "plain_label": "Byte-identical to a known flagged file (mock DB)"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4931,
      "file_id": 65602,
      "severity": "high",
      "score": 70,
      "explanation": "Flagged photo_03_copy.png \u2014 high risk (70/100). Triggered 2 rule(s): \u2022 Byte-identical to a known flagged file (mock DB) \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "photo_03_copy.png",
      "path": "photo_03_copy.png",
      "rules": [
        {
          "rule": "hash_match_exact",
          "points": 50,
          "detail": "Known entry MOCK-EXACT-01",
          "plain_label": "Byte-identical to a known flagged file (mock DB)"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4928,
      "file_id": 65599,
      "severity": "medium",
      "score": 55,
      "explanation": "Flagged photo_01.png \u2014 medium risk (55/100). Triggered 2 rule(s): \u2022 Visually similar to a known flagged image \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "photo_01.png",
      "path": "photo_01.png",
      "rules": [
        {
          "rule": "hash_match_phash",
          "points": 35,
          "detail": "Known entry MOCK-EXACT-01",
          "plain_label": "Visually similar to a known flagged image"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4929,
      "file_id": 65600,
      "severity": "medium",
      "score": 55,
      "explanation": "Flagged photo_02.png \u2014 medium risk (55/100). Triggered 2 rule(s): \u2022 Visually similar to a known flagged image \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "photo_02.png",
      "path": "photo_02.png",
      "rules": [
        {
          "rule": "hash_match_phash",
          "points": 35,
          "detail": "Known entry MOCK-EXACT-01",
          "plain_label": "Visually similar to a known flagged image"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4932,
      "file_id": 65603,
      "severity": "medium",
      "score": 55,
      "explanation": "Flagged photo_04.png \u2014 medium risk (55/100). Triggered 2 rule(s): \u2022 Visually similar to a known flagged image \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "photo_04.png",
      "path": "photo_04.png",
      "rules": [
        {
          "rule": "hash_match_phash",
          "points": 35,
          "detail": "Known entry MOCK-EXACT-01",
          "plain_label": "Visually similar to a known flagged image"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4924,
      "file_id": 65595,
      "severity": "medium",
      "score": 45,
      "explanation": "Flagged chat_1.txt \u2014 medium risk (45/100). Triggered 3 rule(s): \u2022 Changed after the device was seized \u2022 Conversation references a location during night hours \u2022 Message contains a coded-language marker (mock rule). Review the evidence and decide.",
      "name": "chat_1.txt",
      "path": "chat_1.txt",
      "rules": [
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        },
        {
          "rule": "location_night_activity",
          "points": 15,
          "detail": "Location at night",
          "plain_label": "Conversation references a location during night hours"
        },
        {
          "rule": "coded_language",
          "points": 10,
          "detail": "Coded language markers",
          "plain_label": "Message contains a coded-language marker (mock rule)"
        }
      ]
    },
    {
      "id": 4933,
      "file_id": 65604,
      "severity": "medium",
      "score": 45,
      "explanation": "Flagged synthetic_01.png \u2014 medium risk (45/100). Triggered 2 rule(s): \u2022 Likely AI-generated image (mock detector) \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "synthetic_01.png",
      "path": "synthetic_01.png",
      "rules": [
        {
          "rule": "synthetic_media",
          "points": 25,
          "detail": "Synthetic-media score 0.94",
          "plain_label": "Likely AI-generated image (mock detector)"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4934,
      "file_id": 65605,
      "severity": "medium",
      "score": 45,
      "explanation": "Flagged synthetic_02.png \u2014 medium risk (45/100). Triggered 2 rule(s): \u2022 Likely AI-generated image (mock detector) \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "synthetic_02.png",
      "path": "synthetic_02.png",
      "rules": [
        {
          "rule": "synthetic_media",
          "points": 25,
          "detail": "Synthetic-media score 0.94",
          "plain_label": "Likely AI-generated image (mock detector)"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4935,
      "file_id": 65606,
      "severity": "medium",
      "score": 45,
      "explanation": "Flagged synthetic_03.png \u2014 medium risk (45/100). Triggered 2 rule(s): \u2022 Likely AI-generated image (mock detector) \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "synthetic_03.png",
      "path": "synthetic_03.png",
      "rules": [
        {
          "rule": "synthetic_media",
          "points": 25,
          "detail": "Synthetic-media score 0.94",
          "plain_label": "Likely AI-generated image (mock detector)"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4927,
      "file_id": 65598,
      "severity": "medium",
      "score": 40,
      "explanation": "Flagged fake_zip.zip \u2014 medium risk (40/100). Triggered 2 rule(s): \u2022 File disguised with a misleading filename \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "fake_zip.zip",
      "path": "fake_zip.zip",
      "rules": [
        {
          "rule": "renamed_extension",
          "points": 20,
          "detail": "Declared .zip but content is PNG",
          "plain_label": "File disguised with a misleading filename"
        },
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4925,
      "file_id": 65596,
      "severity": "low",
      "score": 20,
      "explanation": "Flagged chat_2.txt \u2014 low risk (20/100). Triggered 1 rule(s): \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "chat_2.txt",
      "path": "chat_2.txt",
      "rules": [
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    },
    {
      "id": 4926,
      "file_id": 65597,
      "severity": "low",
      "score": 20,
      "explanation": "Flagged chat_3.txt \u2014 low risk (20/100). Triggered 1 rule(s): \u2022 Changed after the device was seized. Review the evidence and decide.",
      "name": "chat_3.txt",
      "path": "chat_3.txt",
      "rules": [
        {
          "rule": "modified_after_seizure",
          "points": 20,
          "detail": "Modified after seizure",
          "plain_label": "Changed after the device was seized"
        }
      ]
    }
  ]
};
export const graphMock = {
  "nodes": [
    {
      "id": "device",
      "type": "device",
      "label": "Seized device",
      "x": 0.0137,
      "y": 0.097,
      "props": {
        "mock": true
      }
    },
    {
      "id": "file:65595",
      "type": "file",
      "label": "chat_1.txt",
      "x": -0.1457,
      "y": 0.0371,
      "props": {
        "path": "chat_1.txt",
        "ext": ".txt",
        "size": 163,
        "modified_ts": "2026-08-11T11:25:58+00:00",
        "hidden": false,
        "is_image": false,
        "is_chat": true,
        "flagged": true,
        "flag_score": 45,
        "decision": null
      }
    },
    {
      "id": "file:65596",
      "type": "file",
      "label": "chat_2.txt",
      "x": 0.429,
      "y": 0.2905,
      "props": {
        "path": "chat_2.txt",
        "ext": ".txt",
        "size": 111,
        "modified_ts": "2026-08-11T11:25:58+00:00",
        "hidden": false,
        "is_image": false,
        "is_chat": true,
        "flagged": true,
        "flag_score": 20,
        "decision": null
      }
    },
    {
      "id": "file:65597",
      "type": "file",
      "label": "chat_3.txt",
      "x": -0.3611,
      "y": 0.0462,
      "props": {
        "path": "chat_3.txt",
        "ext": ".txt",
        "size": 95,
        "modified_ts": "2026-08-11T11:25:58+00:00",
        "hidden": false,
        "is_image": false,
        "is_chat": true,
        "flagged": true,
        "flag_score": 20,
        "decision": null
      }
    },
    {
      "id": "file:65598",
      "type": "file",
      "label": "fake_zip.zip",
      "x": -0.9451,
      "y": 0.1965,
      "props": {
        "path": "fake_zip.zip",
        "ext": ".zip",
        "size": 758,
        "modified_ts": "2026-08-11T11:25:58+00:00",
        "hidden": false,
        "is_image": false,
        "is_chat": false,
        "flagged": true,
        "flag_score": 40,
        "decision": null
      }
    },
    {
      "id": "file:65599",
      "type": "file",
      "label": "photo_01.png",
      "x": 0.0583,
      "y": 0.5786,
      "props": {
        "path": "photo_01.png",
        "ext": ".png",
        "size": 760,
        "modified_ts": "2026-08-11T11:25:56+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 55,
        "decision": null
      }
    },
    {
      "id": "file:65600",
      "type": "file",
      "label": "photo_02.png",
      "x": -0.0986,
      "y": 0.3959,
      "props": {
        "path": "photo_02.png",
        "ext": ".png",
        "size": 760,
        "modified_ts": "2026-08-11T11:25:56+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 55,
        "decision": null
      }
    },
    {
      "id": "file:65601",
      "type": "file",
      "label": "photo_03.png",
      "x": -0.0148,
      "y": 0.5965,
      "props": {
        "path": "photo_03.png",
        "ext": ".png",
        "size": 760,
        "modified_ts": "2026-08-11T11:25:56+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 70,
        "decision": null
      }
    },
    {
      "id": "file:65602",
      "type": "file",
      "label": "photo_03_copy.png",
      "x": -0.0323,
      "y": 0.4365,
      "props": {
        "path": "photo_03_copy.png",
        "ext": ".png",
        "size": 760,
        "modified_ts": "2026-08-11T11:25:56+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 70,
        "decision": null
      }
    },
    {
      "id": "file:65603",
      "type": "file",
      "label": "photo_04.png",
      "x": 0.1454,
      "y": 0.3558,
      "props": {
        "path": "photo_04.png",
        "ext": ".png",
        "size": 760,
        "modified_ts": "2026-08-11T11:25:56+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 55,
        "decision": null
      }
    },
    {
      "id": "file:65604",
      "type": "file",
      "label": "synthetic_01.png",
      "x": 0.436,
      "y": -0.1615,
      "props": {
        "path": "synthetic_01.png",
        "ext": ".png",
        "size": 10616,
        "modified_ts": "2026-08-11T11:25:57+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 45,
        "decision": null
      }
    },
    {
      "id": "file:65605",
      "type": "file",
      "label": "synthetic_02.png",
      "x": 0.2104,
      "y": -0.3188,
      "props": {
        "path": "synthetic_02.png",
        "ext": ".png",
        "size": 10616,
        "modified_ts": "2026-08-11T11:25:57+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 45,
        "decision": null
      }
    },
    {
      "id": "file:65606",
      "type": "file",
      "label": "synthetic_03.png",
      "x": 0.7192,
      "y": -0.5374,
      "props": {
        "path": "synthetic_03.png",
        "ext": ".png",
        "size": 10616,
        "modified_ts": "2026-08-11T11:25:57+00:00",
        "hidden": false,
        "is_image": true,
        "is_chat": false,
        "flagged": true,
        "flag_score": 45,
        "decision": null
      }
    },
    {
      "id": "conv:253",
      "type": "conversation",
      "label": "1",
      "x": 0.0858,
      "y": -0.4336,
      "props": {
        "participants": [
          "Alice",
          "Bob"
        ],
        "msg_count": 3
      }
    },
    {
      "id": "conv:254",
      "type": "conversation",
      "label": "2",
      "x": 0.1312,
      "y": 0.1619,
      "props": {
        "participants": [
          "Charlie",
          "Dave"
        ],
        "msg_count": 2
      }
    },
    {
      "id": "conv:255",
      "type": "conversation",
      "label": "3",
      "x": -0.2353,
      "y": 0.5565,
      "props": {
        "participants": [
          "Eve",
          "Frank"
        ],
        "msg_count": 2
      }
    },
    {
      "id": "msg:6113",
      "type": "message",
      "label": "Bob: Are we meeting at Harbour Line?",
      "x": 0.4883,
      "y": -0.3496,
      "props": {
        "ts": "2026-08-11T02:55:58+05:30",
        "sender": "Bob",
        "text": "Are we meeting at Harbour Line?",
        "night": true,
        "coded": false
      }
    },
    {
      "id": "person:Bob",
      "type": "?",
      "label": "person:Bob",
      "x": 0.1213,
      "y": 0.0346,
      "props": {}
    },
    {
      "id": "loc:Harbour Line",
      "type": "location",
      "label": "Harbour Line",
      "x": 0.7588,
      "y": -0.3282,
      "props": {
        "mock": true
      }
    },
    {
      "id": "msg:6114",
      "type": "message",
      "label": "Alice: Yes, don't forget the red package",
      "x": -0.0969,
      "y": -0.8672,
      "props": {
        "ts": "2026-08-11T03:55:58+05:30",
        "sender": "Alice",
        "text": "Yes, don't forget the red package",
        "night": true,
        "coded": true
      }
    },
    {
      "id": "person:Alice",
      "type": "?",
      "label": "person:Alice",
      "x": -0.2014,
      "y": -0.8405,
      "props": {}
    },
    {
      "id": "msg:6115",
      "type": "message",
      "label": "Charlie: Are you going to the usual spot?",
      "x": 0.5035,
      "y": -0.6422,
      "props": {
        "ts": "2026-08-11T10:55:58+05:30",
        "sender": "Charlie",
        "text": "Are you going to the usual spot?",
        "night": false,
        "coded": false
      }
    },
    {
      "id": "person:Charlie",
      "type": "?",
      "label": "person:Charlie",
      "x": 0.3394,
      "y": -0.1744,
      "props": {}
    },
    {
      "id": "msg:6116",
      "type": "message",
      "label": "Dave: Yes, see you soon.",
      "x": -0.2839,
      "y": 0.9242,
      "props": {
        "ts": "2026-08-11T11:55:58+05:30",
        "sender": "Dave",
        "text": "Yes, see you soon.",
        "night": false,
        "coded": false
      }
    },
    {
      "id": "person:Dave",
      "type": "?",
      "label": "person:Dave",
      "x": -0.5143,
      "y": 0.7996,
      "props": {}
    },
    {
      "id": "msg:6112",
      "type": "message",
      "label": "Alice: Hello there",
      "x": 0.0365,
      "y": -0.7938,
      "props": {
        "ts": "2026-08-11T14:55:58+05:30",
        "sender": "Alice",
        "text": "Hello there",
        "night": false,
        "coded": false
      }
    },
    {
      "id": "msg:6117",
      "type": "message",
      "label": "Eve: Normal message here",
      "x": 0.538,
      "y": 0.5759,
      "props": {
        "ts": "2026-08-11T15:55:58+05:30",
        "sender": "Eve",
        "text": "Normal message here",
        "night": false,
        "coded": false
      }
    },
    {
      "id": "person:Eve",
      "type": "?",
      "label": "person:Eve",
      "x": 0.2119,
      "y": 0.0194,
      "props": {}
    },
    {
      "id": "msg:6118",
      "type": "message",
      "label": "Frank: Nothing suspicious",
      "x": -0.9449,
      "y": 0.417,
      "props": {
        "ts": "2026-08-11T16:55:58+05:30",
        "sender": "Frank",
        "text": "Nothing suspicious",
        "night": false,
        "coded": false
      }
    },
    {
      "id": "person:Frank",
      "type": "?",
      "label": "person:Frank",
      "x": -0.6015,
      "y": 0.4038,
      "props": {}
    },
    {
      "id": "person:Arun K",
      "type": "person",
      "label": "Arun K",
      "x": 0.743,
      "y": 0.4917,
      "props": {
        "mock": true
      }
    },
    {
      "id": "person:Manoj P",
      "type": "person",
      "label": "Manoj P",
      "x": -0.9961,
      "y": -0.2913,
      "props": {
        "mock": true
      }
    },
    {
      "id": "person:Sneha R",
      "type": "person",
      "label": "Sneha R",
      "x": 0.2047,
      "y": -0.8411,
      "props": {
        "mock": true
      }
    },
    {
      "id": "person:Deepa M",
      "type": "person",
      "label": "Deepa M",
      "x": 0.5107,
      "y": 0.8073,
      "props": {
        "mock": true
      }
    },
    {
      "id": "person:Vishnu T",
      "type": "person",
      "label": "Vishnu T",
      "x": 0.8273,
      "y": -0.1049,
      "props": {
        "mock": true
      }
    },
    {
      "id": "person:Rahul S",
      "type": "person",
      "label": "Rahul S",
      "x": 0.4081,
      "y": -0.8147,
      "props": {
        "mock": true
      }
    },
    {
      "id": "loc:Junction 7",
      "type": "location",
      "label": "Junction 7",
      "x": -0.7373,
      "y": -0.5489,
      "props": {
        "mock": true
      }
    },
    {
      "id": "loc:Meridian Point",
      "type": "location",
      "label": "Meridian Point",
      "x": 0.7768,
      "y": 0.1922,
      "props": {
        "mock": true
      }
    },
    {
      "id": "loc:East Gate",
      "type": "location",
      "label": "East Gate",
      "x": -0.8761,
      "y": -0.4817,
      "props": {
        "mock": true
      }
    },
    {
      "id": "loc:North Creek",
      "type": "location",
      "label": "North Creek",
      "x": -0.5818,
      "y": -0.732,
      "props": {
        "mock": true
      }
    },
    {
      "id": "loc:Canal Street",
      "type": "location",
      "label": "Canal Street",
      "x": -1.0,
      "y": -0.058,
      "props": {
        "mock": true
      }
    },
    {
      "id": "known:MOCK-EXACT-01",
      "type": "known",
      "label": "MOCK-EXACT-01",
      "x": -0.0304,
      "y": 0.9054,
      "props": {
        "mock": true
      }
    }
  ],
  "edges": [
    {
      "source": "device",
      "target": "file:65595",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65596",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65597",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65598",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65599",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65600",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65601",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65602",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65603",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65604",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65605",
      "type": "contains",
      "props": {}
    },
    {
      "source": "device",
      "target": "file:65606",
      "type": "contains",
      "props": {}
    },
    {
      "source": "file:65595",
      "target": "conv:253",
      "type": "contains",
      "props": {}
    },
    {
      "source": "file:65596",
      "target": "conv:254",
      "type": "contains",
      "props": {}
    },
    {
      "source": "file:65597",
      "target": "conv:255",
      "type": "contains",
      "props": {}
    },
    {
      "source": "file:65599",
      "target": "known:MOCK-EXACT-01",
      "type": "hash_matches",
      "props": {
        "hash_type": "phash",
        "confidence": 1.0
      }
    },
    {
      "source": "file:65599",
      "target": "file:65600",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65599",
      "target": "file:65601",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65599",
      "target": "file:65602",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65599",
      "target": "file:65603",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65600",
      "target": "known:MOCK-EXACT-01",
      "type": "hash_matches",
      "props": {
        "hash_type": "phash",
        "confidence": 1.0
      }
    },
    {
      "source": "file:65600",
      "target": "file:65601",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65600",
      "target": "file:65602",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65600",
      "target": "file:65603",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65601",
      "target": "known:MOCK-EXACT-01",
      "type": "hash_matches",
      "props": {
        "hash_type": "phash",
        "confidence": 1.0
      }
    },
    {
      "source": "file:65601",
      "target": "file:65602",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65601",
      "target": "file:65603",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65602",
      "target": "known:MOCK-EXACT-01",
      "type": "hash_matches",
      "props": {
        "hash_type": "phash",
        "confidence": 1.0
      }
    },
    {
      "source": "file:65602",
      "target": "file:65603",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65603",
      "target": "known:MOCK-EXACT-01",
      "type": "hash_matches",
      "props": {
        "hash_type": "phash",
        "confidence": 1.0
      }
    },
    {
      "source": "file:65604",
      "target": "file:65605",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65604",
      "target": "file:65606",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "file:65605",
      "target": "file:65606",
      "type": "similar_to",
      "props": {
        "distance": 0
      }
    },
    {
      "source": "conv:253",
      "target": "msg:6113",
      "type": "contains",
      "props": {}
    },
    {
      "source": "conv:253",
      "target": "msg:6114",
      "type": "contains",
      "props": {}
    },
    {
      "source": "conv:253",
      "target": "msg:6112",
      "type": "contains",
      "props": {}
    },
    {
      "source": "conv:254",
      "target": "msg:6115",
      "type": "contains",
      "props": {}
    },
    {
      "source": "conv:254",
      "target": "msg:6116",
      "type": "contains",
      "props": {}
    },
    {
      "source": "conv:255",
      "target": "msg:6117",
      "type": "contains",
      "props": {}
    },
    {
      "source": "conv:255",
      "target": "msg:6118",
      "type": "contains",
      "props": {}
    },
    {
      "source": "msg:6113",
      "target": "loc:Harbour Line",
      "type": "mentions",
      "props": {}
    },
    {
      "source": "person:Bob",
      "target": "msg:6113",
      "type": "sent_by",
      "props": {}
    },
    {
      "source": "person:Alice",
      "target": "msg:6114",
      "type": "sent_by",
      "props": {}
    },
    {
      "source": "person:Alice",
      "target": "msg:6112",
      "type": "sent_by",
      "props": {}
    },
    {
      "source": "person:Charlie",
      "target": "msg:6115",
      "type": "sent_by",
      "props": {}
    },
    {
      "source": "person:Dave",
      "target": "msg:6116",
      "type": "sent_by",
      "props": {}
    },
    {
      "source": "person:Eve",
      "target": "msg:6117",
      "type": "sent_by",
      "props": {}
    },
    {
      "source": "person:Frank",
      "target": "msg:6118",
      "type": "sent_by",
      "props": {}
    }
  ],
  "focus": null,
  "node_count": 42
};