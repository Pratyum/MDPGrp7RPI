# MDPGrp7RPI
PYTHON PYTHON PYTHON

## Usage
`cd d5/`

`python MT-v4.py` or `python MT-v5.py`

You might encounter an "Address in use" error if you kill the program and run it again immediately after.
Please wait a minute or so before executing it again.


## Communication Flow

```
|----PC---|			 |-------RPI--------|
|         |			 | COMMSW		    |
|  ALGO   |			 |    (USBSERIAL)-->|---USB--->|ARDUINO|
| (TCP)<->|<--WIFI-->|<->(TCP)-----^	|
|---------|			 | 	   	|			|
					 |(BLUETOOTH)		|
					 |------|-----------|
					 		|
					 		BT
					 		|
					 	 |NEXUS|
```

## Control Flow from Nexus

`|Nexus|--BT-->|RPI COMMSW|--WIFI-->|PC ALGO|--WIFI-->|RPI COMMSW|--USB-->|ARDUINO|`

## Control Flow from Algo

`|PC ALGO|--WIFI/TCPIP-->|RPI COMMSW|--USB-->|ARDUINO|`