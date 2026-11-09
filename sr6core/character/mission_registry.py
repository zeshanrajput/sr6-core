"""
SRM Mission Registry, Ebook Extractor, and Database Ingestion Engine.
Manages:
- Canonical list of legal SRM, CMP, PM, and SMH missions across 2081 and 2083 arcs.
- Dynamic ebook discovery across docx, pdf, and nested zip files.
- Automated text extraction (title, synopsis, scenes, full text).
- SQLite storage in ref_missions and full-text search indexing in missions_fts.
"""

import os
import re
import io
import json
import sqlite3
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import yaml

# Canonical database path fallback
DEFAULT_DB_PATH = os.environ.get(
    "SR6_RULES_DB_PATH",
    os.path.join(os.path.expanduser("~"), ".sr6", "rules_index.db")
)

DEFAULT_EBOOKS_DIR = os.environ.get(
    "SR6_EBOOKS_DIR",
    os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "SR6", "ebooks")
)

# Complete canonical list of legal Shadowrun Missions for 6th Edition (SRMG v2.4 Appendix B)
CANONICAL_MISSIONS: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------
    # Seattle 2081 Arc - Introductory & CMPs
    # -------------------------------------------------------------
    "Build-A-Runner": {
        "id": "Build-A-Runner",
        "code": "Build-A-Runner",
        "title": "Build-A-Runner Workshop",
        "season": "GEN",
        "arc": "Introductory",
        "type": "Special",
        "region": "GEN",
    },
    "CMP.2081.FT": {
        "id": "CMP.2081.FT",
        "code": "CMP 2081-FT",
        "title": "Top Chef - Seattle / The First Taste",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "CMP",
        "region": "SEA",
    },
    "CMP.2081.05": {
        "id": "CMP.2081.05",
        "code": "CMP 2081-05",
        "title": "Late Night Radio",
        "season": "2081",
        "arc": "Neo-Tokyo Twilight",
        "type": "CMP",
        "region": "TYO",
    },
    "CMP.2081.06": {
        "id": "CMP.2081.06",
        "code": "CMP 2081-06",
        "title": "Forbidden Beta Test",
        "season": "2081",
        "arc": "Neo-Tokyo Twilight",
        "type": "CMP",
        "region": "TYO",
    },
    "CMP.2081.07": {
        "id": "CMP.2081.07",
        "code": "CMP 2081-07",
        "title": "Countdown to Zero Hour",
        "season": "2081",
        "arc": "Neo-Tokyo Twilight",
        "type": "CMP",
        "region": "TYO",
    },
    "CMP.2081.08": {
        "id": "CMP.2081.08",
        "code": "CMP 2081-08",
        "title": "Tears of Amaterasu",
        "season": "2081",
        "arc": "Neo-Tokyo Twilight",
        "type": "CMP",
        "region": "TYO",
    },
    "CMP.2081.09": {
        "id": "CMP.2081.09",
        "code": "CMP 2081-09",
        "title": "Bring Me Prince Charming",
        "season": "2081",
        "arc": "Blood Diamonds",
        "type": "CMP",
        "region": "AMS",
    },
    "CMP.2081.10": {
        "id": "CMP.2081.10",
        "code": "CMP 2081-10",
        "title": "A Diamond in The Rough",
        "season": "2081",
        "arc": "Blood Diamonds",
        "type": "CMP",
        "region": "AMS",
    },
    "CMP.2081.11": {
        "id": "CMP.2081.11",
        "code": "CMP 2081-11",
        "title": "Paved with Good Intentions",
        "season": "2081",
        "arc": "Blood Diamonds",
        "type": "CMP",
        "region": "AMS",
    },
    "CMP.2081.12": {
        "id": "CMP.2081.12",
        "code": "CMP 2081-12",
        "title": "Uneasy Lies The Head",
        "season": "2081",
        "arc": "Blood Diamonds",
        "type": "CMP",
        "region": "AMS",
    },
    "CMP.2081.13": {
        "id": "CMP.2081.13",
        "code": "CMP 2081-13",
        "title": "Bright Lights, Big City",
        "season": "2081",
        "arc": "Big Easy Blues",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2081.14": {
        "id": "CMP.2081.14",
        "code": "CMP 2081-14",
        "title": "Hellhound on My Trail",
        "season": "2081",
        "arc": "Big Easy Blues",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2081.15": {
        "id": "CMP.2081.15",
        "code": "CMP 2081-15",
        "title": "Stone Crazy",
        "season": "2081",
        "arc": "Big Easy Blues",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2081.16": {
        "id": "CMP.2081.16",
        "code": "CMP 2081-16",
        "title": "Seventh Son",
        "season": "2081",
        "arc": "Big Easy Blues",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2081.17": {
        "id": "CMP.2081.17",
        "code": "CMP 2081-17",
        "title": "You'll Never Leave Berea Alive",
        "season": "2081",
        "arc": "Kentucky Fried Shadows 2",
        "type": "CMP",
        "region": "KY",
    },
    "CMP.2081.18": {
        "id": "CMP.2081.18",
        "code": "CMP 2081-18",
        "title": "Blue Kentucky Girl",
        "season": "2081",
        "arc": "Kentucky Fried Shadows 2",
        "type": "CMP",
        "region": "KY",
    },
    "CMP.2081.19": {
        "id": "CMP.2081.19",
        "code": "CMP 2081-19",
        "title": "Blue Moon of Kentucky",
        "season": "2081",
        "arc": "Kentucky Fried Shadows 2",
        "type": "CMP",
        "region": "KY",
    },
    "CMP.2081.20": {
        "id": "CMP.2081.20",
        "code": "CMP 2081-20",
        "title": "In the Cold Kentucky Rain",
        "season": "2081",
        "arc": "Kentucky Fried Shadows 2",
        "type": "CMP",
        "region": "KY",
    },

    # -------------------------------------------------------------
    # Seattle 2081 Arc - Core 24 SRMs
    # -------------------------------------------------------------
    "SRM.2081.01": {
        "id": "SRM.2081.01",
        "code": "SRM 2081-01",
        "title": "Death of a Fixer",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.02": {
        "id": "SRM.2081.02",
        "code": "SRM 2081-02",
        "title": "Urgent Care",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.03": {
        "id": "SRM.2081.03",
        "code": "SRM 2081-03",
        "title": "Johnson and Johnson",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.04": {
        "id": "SRM.2081.04",
        "code": "SRM 2081-04",
        "title": "Trailblazers",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.05": {
        "id": "SRM.2081.05",
        "code": "SRM 2081-05",
        "title": "This is Renton",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.06": {
        "id": "SRM.2081.06",
        "code": "SRM 2081-06",
        "title": "Cutting Strings",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.07": {
        "id": "SRM.2081.07",
        "code": "SRM 2081-07",
        "title": "Bootleg Bliss",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.08": {
        "id": "SRM.2081.08",
        "code": "SRM 2081-08",
        "title": "Child's Play",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.09": {
        "id": "SRM.2081.09",
        "code": "SRM 2081-09",
        "title": "Eviction Notice",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.10": {
        "id": "SRM.2081.10",
        "code": "SRM 2081-10",
        "title": "Keep Your Eye on the Lady",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.11": {
        "id": "SRM.2081.11",
        "code": "SRM 2081-11",
        "title": "Power Over Life",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.12": {
        "id": "SRM.2081.12",
        "code": "SRM 2081-12",
        "title": "The Red Pill",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.13": {
        "id": "SRM.2081.13",
        "code": "SRM 2081-13",
        "title": "A Cookie from Uncle Lung",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.14": {
        "id": "SRM.2081.14",
        "code": "SRM 2081-14",
        "title": "The Advantages of History",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.15": {
        "id": "SRM.2081.15",
        "code": "SRM 2081-15",
        "title": "A Bunch of Corporate Drek",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.16": {
        "id": "SRM.2081.16",
        "code": "SRM 2081-16",
        "title": "It Ends, It Begins",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.17": {
        "id": "SRM.2081.17",
        "code": "SRM 2081-17",
        "title": "Framed in Blood",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.18": {
        "id": "SRM.2081.18",
        "code": "SRM 2081-18",
        "title": "Friendships Never Grow Rust",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.19": {
        "id": "SRM.2081.19",
        "code": "SRM 2081-19",
        "title": "False Flag, Pink Mohawk",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.20": {
        "id": "SRM.2081.20",
        "code": "SRM 2081-20",
        "title": "Fairweather Light",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.21": {
        "id": "SRM.2081.21",
        "code": "SRM 2081-21",
        "title": "Grudge Match Gladiators",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.22": {
        "id": "SRM.2081.22",
        "code": "SRM 2081-22",
        "title": "Bloodrocution",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.23": {
        "id": "SRM.2081.23",
        "code": "SRM 2081-23",
        "title": "Severed Roots",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "SRM.2081.24": {
        "id": "SRM.2081.24",
        "code": "SRM 2081-24",
        "title": "Punk Rock v Dad Rock",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SRM",
        "region": "SEA",
    },
    "PM.2081.01": {
        "id": "PM.2081.01",
        "code": "PM 2081-01",
        "title": "Mayhem and Misdirection",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "PM",
        "region": "SEA",
    },
    "PM.2081.02": {
        "id": "PM.2081.02",
        "code": "PM 2081-02",
        "title": "Nuclear Option",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "PM",
        "region": "SEA",
    },
    "PM.2081.03": {
        "id": "PM.2081.03",
        "code": "PM 2081-03",
        "title": "Entwined Auras",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "PM",
        "region": "SEA",
    },
    "SMH.2081.01": {
        "id": "SMH.2081.01",
        "code": "SMH 2081-01",
        "title": "Drek the Halls",
        "season": "2081",
        "arc": "Seattle 2081",
        "type": "SMH",
        "region": "SEA",
    },

    # -------------------------------------------------------------
    # New Orleans 2083 Arc - CMPs & Specials
    # -------------------------------------------------------------
    "CMP.2083.FT": {
        "id": "CMP.2083.FT",
        "code": "CMP 2083-FT",
        "title": "The First Taste - New Orleans",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.01": {
        "id": "CMP.2083.01",
        "code": "CMP 2083-01",
        "title": "Nonplushed",
        "season": "2083",
        "arc": "Bad Blood",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.02": {
        "id": "CMP.2083.02",
        "code": "CMP 2083-02",
        "title": "Royal Road",
        "season": "2083",
        "arc": "Bad Blood",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.03": {
        "id": "CMP.2083.03",
        "code": "CMP 2083-03",
        "title": "Hell & High Water",
        "season": "2083",
        "arc": "Bad Blood",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.04": {
        "id": "CMP.2083.04",
        "code": "CMP 2083-04",
        "title": "Hog Wild",
        "season": "2083",
        "arc": "Bad Blood",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.05": {
        "id": "CMP.2083.05",
        "code": "CMP 2083-05",
        "title": "Precious Cargo",
        "season": "2083",
        "arc": "The Price of Flesh",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.06": {
        "id": "CMP.2083.06",
        "code": "CMP 2083-06",
        "title": "Fragile Contraband",
        "season": "2083",
        "arc": "The Price of Flesh",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.07": {
        "id": "CMP.2083.07",
        "code": "CMP 2083-07",
        "title": "Misplaced Loyalty",
        "season": "2083",
        "arc": "The Price of Flesh",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.08": {
        "id": "CMP.2083.08",
        "code": "CMP 2083-08",
        "title": "Darkest Jungle",
        "season": "2083",
        "arc": "The Price of Flesh",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.09": {
        "id": "CMP.2083.09",
        "code": "CMP 2083-09",
        "title": "World Star",
        "season": "2083",
        "arc": "K-Pocalypse",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.10": {
        "id": "CMP.2083.10",
        "code": "CMP 2083-10",
        "title": "All Kill",
        "season": "2083",
        "arc": "K-Pocalypse",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.11": {
        "id": "CMP.2083.11",
        "code": "CMP 2083-11",
        "title": "Dynamite Life",
        "season": "2083",
        "arc": "K-Pocalypse",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.12": {
        "id": "CMP.2083.12",
        "code": "CMP 2083-12",
        "title": "Black Ocean",
        "season": "2083",
        "arc": "K-Pocalypse",
        "type": "CMP",
        "region": "NOLA",
    },
    "CMP.2083.14": {
        "id": "CMP.2083.14",
        "code": "CMP 2083-14",
        "title": "A Day at the Beach",
        "season": "2083",
        "arc": "Denver War",
        "type": "CMP",
        "region": "DW",
    },
    "CMP.2083.15": {
        "id": "CMP.2083.15",
        "code": "CMP 2083-15",
        "title": "By Land, Sea, and Hair",
        "season": "2083",
        "arc": "Denver War",
        "type": "CMP",
        "region": "DW",
    },
    "CMP.2083.16": {
        "id": "CMP.2083.16",
        "code": "CMP 2083-16",
        "title": "War Never Changes",
        "season": "2083",
        "arc": "Denver War",
        "type": "CMP",
        "region": "DW",
    },

    # -------------------------------------------------------------
    # New Orleans 2083 Arc - Core SRMs
    # -------------------------------------------------------------
    "SRM.2083.01": {
        "id": "SRM.2083.01",
        "code": "SRM 2083-01",
        "title": "Gaining Ground",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.02": {
        "id": "SRM.2083.02",
        "code": "SRM 2083-02",
        "title": "Fashionable Cyberpunk Planeteers",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.03": {
        "id": "SRM.2083.03",
        "code": "SRM 2083-03",
        "title": "Unofficial Dunkelzahn Fan Club",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.04": {
        "id": "SRM.2083.04",
        "code": "SRM 2083-04",
        "title": "Gantillon's Last Run",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.05": {
        "id": "SRM.2083.05",
        "code": "SRM 2083-05",
        "title": "Intentions Laid Threadbare",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.06": {
        "id": "SRM.2083.06",
        "code": "SRM 2083-06",
        "title": "Zero Two Murder",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.07": {
        "id": "SRM.2083.07",
        "code": "SRM 2083-07",
        "title": "The Devil's Danse",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.08": {
        "id": "SRM.2083.08",
        "code": "SRM 2083-08",
        "title": "Dragon's Gambit",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.09": {
        "id": "SRM.2083.09",
        "code": "SRM 2083-09",
        "title": "Houseguests Can Be Murder",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.10": {
        "id": "SRM.2083.10",
        "code": "SRM 2083-10",
        "title": "Wasted Talent",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.11": {
        "id": "SRM.2083.11",
        "code": "SRM 2083-11",
        "title": "Blackwater Delta",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.12": {
        "id": "SRM.2083.12",
        "code": "SRM 2083-12",
        "title": "When You're Smiling",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.13": {
        "id": "SRM.2083.13",
        "code": "SRM 2083-13",
        "title": "Enter the Funhouse",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.14": {
        "id": "SRM.2083.14",
        "code": "SRM 2083-14",
        "title": "Deepest Roots",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.15": {
        "id": "SRM.2083.15",
        "code": "SRM 2083-15",
        "title": "Dalliance with Decadence",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.16": {
        "id": "SRM.2083.16",
        "code": "SRM 2083-16",
        "title": "Crossfire Hurricane",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.17": {
        "id": "SRM.2083.17",
        "code": "SRM 2083-17",
        "title": "Haute Blooded",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.18": {
        "id": "SRM.2083.18",
        "code": "SRM 2083-18",
        "title": "Some Kind of Voodoo?",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.19": {
        "id": "SRM.2083.19",
        "code": "SRM 2083-19",
        "title": "The Hallow Feast",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "SRM.2083.20": {
        "id": "SRM.2083.20",
        "code": "SRM 2083-20",
        "title": "The Fallacy of Plans",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SRM",
        "region": "NOLA",
    },
    "PM.2083.01": {
        "id": "PM.2083.01",
        "code": "PM 2083-01",
        "title": "Come Sail Away",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "PM",
        "region": "NOLA",
    },
    "PM.2083.02": {
        "id": "PM.2083.02",
        "code": "PM 2083-02",
        "title": "The Best Show in the World",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "PM",
        "region": "NOLA",
    },
    "SMH.2083.01": {
        "id": "SMH.2083.01",
        "code": "SMH 2083-01",
        "title": "The CONquest",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SMH",
        "region": "NOLA",
    },
    "SMH.2083.02": {
        "id": "SMH.2083.02",
        "code": "SMH 2083-02",
        "title": "Egg Hunt at the Jackalope Ranch",
        "season": "2083",
        "arc": "New Orleans 2083",
        "type": "SMH",
        "region": "NOLA",
    },
}


def normalize_mission_code(code_or_title: str) -> str:
    """
    Normalizes any mission identifier into canonical ID format:
    e.g.:
      'SRM 2081-01' -> 'SRM.2081.01'
      'SRM 2081-14' -> 'SRM.2081.14'
      '2081-14'     -> 'SRM.2081.14'
      'CMP 2020-05' -> 'CMP.2081.05'
      'CMP 2081-05' -> 'CMP.2081.05'
      'Death of a Fixer' -> 'SRM.2081.01'
    """
    s = code_or_title.strip()
    
    # Direct match in canonical dictionary
    if s in CANONICAL_MISSIONS:
        return s
    for k, v in CANONICAL_MISSIONS.items():
        if k.lower() == s.lower():
            return k

    # Special named events
    if re.search(r"build[- ]?a[- ]?runner", s, re.IGNORECASE):
        return "Build-A-Runner"
    if re.search(r"first[- ]?taste", s, re.IGNORECASE):
        if "2083" in s or "nola" in s.lower():
            return "CMP.2083.FT"
        return "CMP.2081.FT"

    # Normalize punctuation: 'SRM 2081-01', 'srm.2081.01', 'SRM-2081-01'
    cleaned = re.sub(r"[\s\-_]+", ".", s).upper()
    
    # Handle '2081.14' shorthand -> 'SRM.2081.14'
    m_short = re.match(r"^(2081|2083)\.([0-9]{2})$", cleaned)
    if m_short:
        cleaned = f"SRM.{m_short.group(1)}.{m_short.group(2)}"

    # Handle Neo-Tokyo legacy numbering 'CMP.2020.05' -> 'CMP.2081.05'
    cleaned = re.sub(r"^CMP\.2020\.", "CMP.2081.", cleaned)

    parts = [p for p in cleaned.split(".") if p]
    if len(parts) >= 3 and parts[0] in ["SRM", "CMP", "SMH", "PM"]:
        norm_key = f"{parts[0]}.{parts[1]}.{parts[2]}"
        if norm_key in CANONICAL_MISSIONS:
            return norm_key

    # Try title matching
    s_lower = s.lower()
    for k, v in CANONICAL_MISSIONS.items():
        title_lower = v.get("title", "").lower()
        if title_lower == s_lower or s_lower in title_lower:
            return k

    return s


def init_missions_table(conn: sqlite3.Connection):
    """Creates the ref_missions metadata and missions_fts virtual tables in SQLite."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ref_missions (
            id TEXT PRIMARY KEY,
            code TEXT,
            title TEXT,
            season TEXT,
            arc TEXT,
            type TEXT,
            region TEXT,
            file_path TEXT,
            synopsis TEXT,
            scenes_json TEXT,
            char_count INTEGER DEFAULT 0,
            raw_text TEXT
        )
    """)
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS missions_fts USING fts5(
            id,
            code,
            title,
            arc,
            season,
            synopsis,
            content
        )
    """)
    conn.commit()


def extract_docx_text(file_bytes_or_path: Any) -> Dict[str, Any]:
    """Extracts title, synopsis, scenes, and full text from a docx file (path or bytes)."""
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    paras = []
    
    with zipfile.ZipFile(file_bytes_or_path) as z:
        tree = ET.fromstring(z.read("word/document.xml"))
        for p in tree.iter(f"{{{ns}}}p"):
            texts = [node.text for node in p.iter(f"{{{ns}}}t") if node.text]
            if texts:
                paras.append("".join(texts).strip())

    full_text = "\n\n".join(paras)
    title = paras[0] if paras else ""

    synopsis = ""
    syn_idx = -1
    for idx, p in enumerate(paras[:50]):
        if re.search(r"synopsis", p, re.IGNORECASE):
            syn_idx = idx
            break
    if syn_idx != -1 and syn_idx + 1 < len(paras):
        syn_paras = []
        for p in paras[syn_idx+1:syn_idx+8]:
            if re.search(r"scene\s+[0-9]|credits|cast of shadows|background", p, re.IGNORECASE):
                break
            syn_paras.append(p)
        synopsis = "\n\n".join(syn_paras)

    scenes = []
    for p in paras:
        m = re.match(r"^(Scene\s+[0-9]+[A-Za-z]?\s*[:\-].*)", p, re.IGNORECASE)
        if m:
            scenes.append(m.group(1))

    return {
        "title": title,
        "synopsis": synopsis,
        "scenes": scenes,
        "raw_text": full_text,
        "char_count": len(full_text)
    }


def extract_pdf_text(file_path: str) -> Dict[str, Any]:
    """Extracts text from a PDF file using PyMuPDF (fitz)."""
    try:
        import pymupdf as fitz
    except ImportError:
        import fitz

    doc = fitz.open(file_path)
    paras = []
    for page in doc:
        text = page.get_text("text")
        if text.strip():
            paras.append(text.strip())

    full_text = "\n\n".join(paras)
    first_lines = paras[0].split("\n") if paras else []
    title = first_lines[0].strip() if first_lines else ""

    synopsis = ""
    syn_idx = -1
    for idx, p in enumerate(paras[:10]):
        if re.search(r"synopsis", p, re.IGNORECASE):
            syn_idx = idx
            break
    if syn_idx != -1 and syn_idx + 1 < len(paras):
        synopsis = paras[syn_idx + 1][:800]

    return {
        "title": title,
        "synopsis": synopsis,
        "scenes": [],
        "raw_text": full_text,
        "char_count": len(full_text)
    }


def scan_ebooks_files(ebooks_dir: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    Scans the ebooks directory for docx, pdf, and zip files and maps them to canonical mission keys.
    """
    root = Path(ebooks_dir or DEFAULT_EBOOKS_DIR)
    if not root.exists():
        return {}

    code_pattern = re.compile(r"(SRM|CMP|SMH|PM)[\s\._\-]?([0-9]{4})[\s\._\-]?([0-9]{2}|FT)", re.IGNORECASE)
    file_map: Dict[str, Dict[str, Any]] = {}

    # 1. Walk regular files
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        fname = p.name
        is_handout = any(k in fname.lower() for k in ["handout", "map", "overview", "primer", "faq", "bestiary", "journal"])
        if is_handout:
            continue

        if fname.lower().endswith(".docx") or fname.lower().endswith(".pdf"):
            m = code_pattern.search(fname)
            if m:
                mtype = m.group(1).upper()
                season = m.group(2)
                num = m.group(3).upper()
                raw_code = f"{mtype}.{season}.{num}"
                norm_code = normalize_mission_code(raw_code)
                if norm_code in CANONICAL_MISSIONS:
                    # Prefer docx over pdf for richer structure
                    if norm_code not in file_map or (fname.endswith(".docx") and not file_map[norm_code]["path"].endswith(".docx")):
                        file_map[norm_code] = {
                            "path": str(p),
                            "format": "docx" if fname.endswith(".docx") else "pdf",
                            "in_zip": False
                        }

    # 2. Walk zip files for nested docx missions
    for zp in root.rglob("*.zip"):
        try:
            with zipfile.ZipFile(zp) as outer:
                for name in outer.namelist():
                    if name.endswith(".docx") and not name.startswith("__MACOSX"):
                        m = code_pattern.search(name)
                        if m:
                            mtype = m.group(1).upper()
                            season = m.group(2)
                            num = m.group(3).upper()
                            norm_code = normalize_mission_code(f"{mtype}.{season}.{num}")
                            if norm_code in CANONICAL_MISSIONS and norm_code not in file_map:
                                file_map[norm_code] = {
                                    "path": str(zp),
                                    "zip_subpath": name,
                                    "format": "docx_in_zip",
                                    "in_zip": True
                                }
        except Exception:
            pass

    return file_map


def ingest_all_missions(db_path: Optional[str] = None, ebooks_dir: Optional[str] = None, force: bool = False) -> Dict[str, int]:
    """
    Extracts text from all available ebook mission files and stores them in ref_missions and missions_fts.
    """
    db_file = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(db_file)), exist_ok=True)
    conn = sqlite3.connect(db_file)
    init_missions_table(conn)

    cursor = conn.cursor()
    files_map = scan_ebooks_files(ebooks_dir)

    # Check which missions are already ingested
    cursor.execute("SELECT id FROM ref_missions")
    existing_ids = {row[0] for row in cursor.fetchall()}

    ingested = 0
    updated = 0

    for m_id, meta in CANONICAL_MISSIONS.items():
        if m_id in existing_ids and not force:
            continue

        file_info = files_map.get(m_id)
        synopsis = ""
        scenes_json = "[]"
        raw_text = ""
        char_count = 0
        file_path = file_info["path"] if file_info else ""

        if file_info:
            try:
                fmt = file_info["format"]
                if fmt == "docx":
                    res = extract_docx_text(file_info["path"])
                elif fmt == "docx_in_zip":
                    with zipfile.ZipFile(file_info["path"]) as outer:
                        b = io.BytesIO(outer.read(file_info["zip_subpath"]))
                        res = extract_docx_text(b)
                elif fmt == "pdf":
                    res = extract_pdf_text(file_info["path"])
                else:
                    res = {}

                synopsis = res.get("synopsis", "")
                scenes_json = json.dumps(res.get("scenes", []))
                raw_text = res.get("raw_text", "")
                char_count = res.get("char_count", 0)
            except Exception as e:
                # Keep metadata even if text extraction encounters odd formatting
                pass

        cursor.execute("""
            INSERT OR REPLACE INTO ref_missions (
                id, code, title, season, arc, type, region, file_path, synopsis, scenes_json, char_count, raw_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m_id,
            meta.get("code", m_id),
            meta.get("title", m_id),
            meta.get("season", "GEN"),
            meta.get("arc", "Shadowrun Missions"),
            meta.get("type", "SRM"),
            meta.get("region", "GEN"),
            file_path,
            synopsis,
            scenes_json,
            char_count,
            raw_text
        ))

        # Index in FTS5
        cursor.execute("DELETE FROM missions_fts WHERE id = ?", (m_id,))
        cursor.execute("""
            INSERT INTO missions_fts (id, code, title, arc, season, synopsis, content)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            m_id,
            meta.get("code", m_id),
            meta.get("title", m_id),
            meta.get("arc", ""),
            meta.get("season", ""),
            synopsis,
            raw_text
        ))

        if m_id in existing_ids:
            updated += 1
        else:
            ingested += 1

    conn.commit()
    conn.close()
    return {"ingested": ingested, "updated": updated, "total_canonical": len(CANONICAL_MISSIONS)}


def get_mission_record(code_or_title: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieves full mission record from SQLite ref_missions, falling back to CANONICAL_MISSIONS memory dict.
    """
    norm_id = normalize_mission_code(code_or_title)
    
    db_file = db_path or DEFAULT_DB_PATH
    if os.path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ref_missions WHERE id = ? OR code = ?", (norm_id, code_or_title.strip()))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["scenes"] = json.loads(d.get("scenes_json") or "[]")
                conn.close()
                return d
            conn.close()
        except Exception:
            pass

    if norm_id in CANONICAL_MISSIONS:
        rec = dict(CANONICAL_MISSIONS[norm_id])
        rec["synopsis"] = ""
        rec["scenes"] = []
        rec["file_path"] = ""
        return rec

    return None


def search_missions(query: str, db_path: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Executes FTS5 full-text search across mission text and synopses in SQLite.
    """
    db_file = db_path or DEFAULT_DB_PATH
    if not os.path.exists(db_file):
        return []

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Escape query for FTS5
    safe_q = re.sub(r'["\*\^]', '', query).strip()
    if not safe_q:
        return []

    try:
        cursor.execute("""
            SELECT id, code, title, arc, season, snippet(missions_fts, 5, '<b>', '</b>', '...', 20) as snippet
            FROM missions_fts
            WHERE missions_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (f"{safe_q}*", limit))
        results = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return results
    except Exception:
        conn.close()
        return []
