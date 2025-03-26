# header_script
- This script is used to add 64 byte header to the start of binary

    <details>
    <summary>Header structure:</summary> 

    |Parameter|data type|description|
    |:---|:---|:---|
    |**Expected_size**|uint64_t|binary size in bytes|
    |**Expected_CRC**|uint32_t|CRC of whole binary|
    |**Device_type**|uint16_t|type of updated device|
    |**Data_type**|uint8_t|type of binary (update = 0, configuration = 1)|
    |**Protocol_type**|uint16_t|protocol used for transmiting binary (fmtp = 0, modbus = 1)|
    |**Reserved**|47 x uint8_t|configurable buffer that can be used for future adjustments and further specifications|

    </details>

- To change header parameters go to configs/header_config.json,
- To add binary that you want to be joined with header, put it in input/firmware.bin
- Then run **python attach_header.py** and get your new binary with attached header from: output/firmware_with_header.bin

## Windows - powershell

steps to run the script: 

* python -m venv venv
* .\venv\Scripts\activate
* python attach_header.py