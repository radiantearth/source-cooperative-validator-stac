NEW_VERSIONS = [
    "1.0.0-beta.2",
    "1.0.0-rc.1",
    "1.0.0-rc.2",
    "1.0.0-rc.3",
    "1.0.0-rc.4",
    "1.0.0",
]

def get_stac_type(stac_content: dict) -> str:
    try:
        content_types = ["Item", "Catalog", "Collection"]
        if "type" in stac_content and stac_content["type"] == "Feature":
            return "Item"
        elif "type" in stac_content and stac_content["type"] in content_types:
            return stac_content["type"]
        elif "extent" in stac_content or "license" in stac_content:
            return "Collection"
        else:
            return "Catalog"
    except TypeError as e:
        return str(e)

def set_stac_schema_addr(version: str, stac_type: str) -> str:
    if version in NEW_VERSIONS:
        return f"https://schemas.stacspec.org/v{version}/{stac_type}-spec/json-schema/{stac_type}.json"
    else:
        return f"https://cdn.staclint.com/v{version}/{stac_type}.json"