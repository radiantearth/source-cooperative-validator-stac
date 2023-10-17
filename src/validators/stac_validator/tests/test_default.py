"""
Description: Test the default which validates core and extensions

"""

from validators.stac_validator import validate


def test_default_v070():
    stac_file = "https://radarstac.s3.amazonaws.com/stac/catalog.json"
    stac = validate.StacValidate(stac_file)
    stac.run()
    # Sort the 'schema' list within the dictionary
    sorted_message = [{'version': d['version'],
                    'path': d['path'],
                    'asset_type': d['asset_type'],
                    'validation_method': d['validation_method'],
                    'schema': sorted(d['schema']),
                    'valid_stac': d['valid_stac']} for d in stac.message]

    assert sorted_message == [
        {
            "version": "0.7.0",
            "path": "https://radarstac.s3.amazonaws.com/stac/catalog.json",
            "asset_type": "CATALOG",
            "validation_method": "default",
            "schema": ["https://cdn.staclint.com/v0.7.0/catalog.json"],
            "valid_stac": True,
        }
    ]

'''
def test_default_item_local_v080():
    stac_file = "tests/test_data/v080/items/sample-full.json"
    stac = StacValidate(stac_file)
    stac.run()
    assert stac.message == [
        {
            "version": "0.8.0",
            "path": "tests/test_data/v080/items/sample-full.json",
            "schema": [
                "https://cdn.staclint.com/v0.8.0/extension/eo.json",
                "https://cdn.staclint.com/v0.8.0/item.json",
            ],
            "asset_type": "ITEM",
            "validation_method": "default",
            "valid_stac": True,
        }
    ]


def test_default_v090():
    stac = StacValidate("tests/test_data/v090/items/good_item_v090.json")
    stac.run()
    print(stac.message)
    assert stac.message == [
        {
            "version": "0.9.0",
            "path": "tests/test_data/v090/items/good_item_v090.json",
            "schema": [
                "https://cdn.staclint.com/v0.9.0/extension/eo.json",
                "https://cdn.staclint.com/v0.9.0/extension/view.json",
                "https://cdn.staclint.com/v0.9.0/item.json",
            ],
            "asset_type": "ITEM",
            "validation_method": "default",
            "valid_stac": True,
        }
    ]


def test_default_v1beta1():
    stac_file = "tests/test_data/1beta1/sentinel2.json"
    stac = StacValidate(stac_file)
    stac.run()
    assert stac.message == [
        {
            "path": "tests/test_data/1beta1/sentinel2.json",
            "asset_type": "COLLECTION",
            "version": "1.0.0-beta.1",
            "validation_method": "default",
            "schema": ["https://cdn.staclint.com/v1.0.0-beta.1/collection.json"],
            "valid_stac": True,
        }
    ]
'''

def test_default_proj_v1b2():
    stac_file = "https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l1c/items/S2A_51SXT_20210415_0_L1C"
    stac = validate.StacValidate(stac_file)
    stac.run()
    sorted_message = [{'version': d['version'],
                    'path': d['path'],
                    'asset_type': d['asset_type'],
                    'schema': sorted(d['schema']),
                    'validation_method': d['validation_method'],
                    'valid_stac': d['valid_stac']} for d in stac.message]
    assert sorted_message == [
        {
            "version": "1.0.0-beta.2",
            "path": "https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l1c/items/S2A_51SXT_20210415_0_L1C",
            "asset_type": "ITEM",
            "schema": [
                "https://cdn.staclint.com/v1.0.0-beta.1/extension/eo.json",
                "https://cdn.staclint.com/v1.0.0-beta.1/extension/projection.json",
                "https://cdn.staclint.com/v1.0.0-beta.1/extension/view.json",
                "https://schemas.stacspec.org/v1.0.0-beta.2/item-spec/json-schema/item.json",
            ],
            "validation_method": "default",
            "valid_stac": True,
        }
    ]

'''
def test_default_simple_v1rc2():
    stac_file = "tests/test_data/1rc2/simple-item.json"
    stac = StacValidate(stac_file)
    stac.run()
    assert stac.message == [
        {
            "path": "tests/test_data/1rc2/simple-item.json",
            "asset_type": "ITEM",
            "version": "1.0.0-rc.2",
            "validation_method": "default",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.2/item-spec/json-schema/item.json",
            ],
            "valid_stac": True,
        }
    ]


def test_default_extended_v1rc2():
    stac_file = "tests/test_data/1rc2/extended-item.json"
    stac = StacValidate(stac_file)
    stac.run()
    assert stac.message == [
        {
            "version": "1.0.0-rc.2",
            "path": "tests/test_data/1rc2/extended-item.json",
            "schema": [
                "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
                "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
                "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
                "https://stac-extensions.github.io/view/v1.0.0/schema.json",
                "https://stac-extensions.github.io/remote-data/v1.0.0/schema.json",
                "https://schemas.stacspec.org/v1.0.0-rc.2/item-spec/json-schema/item.json",
            ],
            "asset_type": "ITEM",
            "validation_method": "default",
            "valid_stac": True,
        }
    ]


def test_default_catalog_v1rc2():
    stac_file = "tests/test_data/1rc2/catalog.json"
    stac = StacValidate(stac_file)
    stac.run()
    assert stac.message == [
        {
            "path": "tests/test_data/1rc2/catalog.json",
            "asset_type": "CATALOG",
            "version": "1.0.0-rc.2",
            "validation_method": "default",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.2/catalog-spec/json-schema/catalog.json"
            ],
            "valid_stac": True,
        }
    ]
'''
