# MDPGrp7RPI
PYTHON PYTHON PYTHON

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

|Nexus|--BT-->|RPI COMMSW|--WIFI-->|PC ALGO|--WIFI-->|RPI COMMSW|-->|ARDUINO|