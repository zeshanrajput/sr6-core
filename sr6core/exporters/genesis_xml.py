"""
Genesis XML Serializer for SR6.
Preserves Genesis element UUIDs/OIDs to allow seamless visual shopping round-trips.
"""

import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional


def patch_genesis_xml(input_xml_path: str, char_data: Dict[str, Any], output_xml_path: str) -> bool:
    if not os.path.exists(input_xml_path):
        return False

    try:
        tree = ET.parse(input_xml_path)
        root = tree.getroot()

        # Update root attributes
        identity = char_data.get("identity", {})
        if "handle" in identity:
            root.set("handle", identity["handle"])
        if "real_name" in identity:
            real_name_el = root.find("realName")
            if real_name_el is not None:
                real_name_el.text = identity["real_name"]

        # Update contacts while preserving UUIDs/IDs
        contacts_el = root.find("contacts")
        if contacts_el is not None and "contacts" in char_data:
            existing_contacts = {c.get("name"): c for c in contacts_el.findall("contact") if c.get("name")}
            for contact_info in char_data["contacts"]:
                cname = contact_info.get("name")
                if cname in existing_contacts:
                    c_el = existing_contacts[cname]
                    if "connection" in contact_info:
                        c_el.set("rat", str(contact_info["connection"]))
                    if "loyalty" in contact_info:
                        c_el.set("loy", str(contact_info["loyalty"]))
                    if "favors" in contact_info:
                        c_el.set("favors", str(contact_info["favors"]))

        # Remove non-Genesis tags
        for tag in ["sessions", "sessionlogs"]:
            el = root.find(tag)
            if el is not None:
                root.remove(el)

        os.makedirs(os.path.dirname(output_xml_path) or ".", exist_ok=True)
        tree.write(output_xml_path, encoding="utf-8", xml_declaration=True)
        return True
    except Exception as e:
        print(f"Error patching Genesis XML: {e}")
        return False
