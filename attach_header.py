#!/usr/bin/env python3

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any, Dict, List

def compute_firmware_crc32(data_bytes: bytes) -> int:
    """CRC-32 computation (unchanged from your original)"""
    poly = 0x04C11DB7
    crc = 0xFFFFFFFF
    for b in data_bytes:
        crc ^= (b << 24)
        for _ in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
        crc &= 0xFFFFFFFF
    return ~crc & 0xFFFFFFFF

def main() -> None:
    # Get the project root directory
    project_root: Path = Path(__file__).parent

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Attach a 64-byte header to a binary file, "
                    "with parameters from JSON and automatically computed size/CRC."
    )

    # Set default paths based on project structure
    default_json: str = str(project_root / "configs" / "header_config.json")
    default_input: str = str(project_root / "input" / "firmware.bin")
    default_output: str = str(project_root / "output" / "firmware_with_header.bin")

    parser.add_argument(
        "--bin",
        default=default_input,
        help=f"Path to the input binary file (default: {default_input})"
    )
    parser.add_argument(
        "--json",
        default=default_json,
        help=f"Path to the JSON config file (default: {default_json})"
    )
    parser.add_argument(
        "--out",
        default=default_output,
        help=f"Path to the output file (default: {default_output})"
    )

    args: argparse.Namespace = parser.parse_args()

    # Ensure output directory exists
    output_path: Path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 1) Read the binary file
    try:
        with open(args.bin, "rb") as f:
            firmware_data: bytes = f.read()
    except IOError as e:
        print(f"Error reading binary file: {e}")
        sys.exit(1)

    # 2) Compute Expected_size and Expected_CRC
    expected_size: int = len(firmware_data)
    expected_crc: int = compute_firmware_crc32(firmware_data)

    # 3) Read and parse the JSON structure
    try:
        with open(args.json, "r") as f:
            header_config: Dict[str, Any] = json.load(f)
    except IOError as e:
        print(f"Error reading JSON file: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        sys.exit(1)

    # Extract fields from JSON
    device_type: int = header_config.get("Device_type",65535)
    data_type: int = header_config.get("Data_type", 255)
    protocol_type: int = header_config.get("Protocol_type", 65535)
    reserved_list: List[int] = header_config.get("Reserved", [])

    # Check if all parameters are within the predefined bounds
    if(device_type < 0 or device_type > 65535):
        print("Device_type must be between 0 - 65535")
        sys.exit(1)

    if(data_type < 0 or data_type > 255):
        print("Data_type must be between 0 - 255")
        sys.exit(1)

    if(protocol_type < 0 or protocol_type > 65535):
        print("Protocol_type must be between 0 - 65535")
        sys.exit(1)

    j = 0
    for i in reserved_list:
        if(i < 0 or i > 255):
            print(f"Reserved element number {j} must be between 0 - 255")
            sys.exit(1)
        j += 1

    # Ensure 'Reserved' has exactly 47 bytes
    if len(reserved_list) < 47:
        reserved_list += [0] * (47 - len(reserved_list))
    elif len(reserved_list) > 47:
        reserved_list = reserved_list[:47]

    # 4) Pack into a 64-byte header
    fmt_header: str = ">Q I H B H " + "B"*47
    header_data: bytes = struct.pack(
        fmt_header,
        expected_size,
        expected_crc,
        device_type,
        data_type,
        protocol_type,
        *reserved_list
    )

    # 5) Write output file
    try:
        with open(args.out, "wb") as f:
            f.write(header_data)
            f.write(firmware_data)
        print(f"Successfully wrote file: {args.out}")
    except IOError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
