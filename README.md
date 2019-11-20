# pyegctl

This is a python version of utility egctl published by Vitaly Sinilin.

Original project link: [unterwulf/egctl]("https://github.com/unterwulf/egctl")

Many thanks to you!

## Installation

```
 pip install pyegctl
```

## Example usage

```python
from pyegctl.device import EGV21

pdu = EGV21('192.168.1.111', '5000', password='p4ss')

pdu.set(['on', 'on', 'left', 'toggle'])

assert pdu.status()[0] == 'on'

```

## Supported devices

Currently only V21 protocol is supported. 