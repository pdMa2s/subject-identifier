# subject-identifier

University of Aveiro

Departamento de Electrónica, Telecomunicações e Informática

MEI

This work was developed for course of Algorithmic Information Theory (2017/2018).

The goal of this application is to automatically identify the subject portrait in a face image 
by measuring the similarities between images, it does by using an approximation of the 
Kolmogorov complexity, the Normalized Compression Distance (NCD) and the Normalized ConditionalCompression Distance (NCCD).

How to run: 

```bash
$ python CompressionTests.py -h
```

Check the usage USAGE prompt and follow the instructions

Example:
```bash
$ python CompressionTests.py orl_faces bzip2 -nr 3
```
