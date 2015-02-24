Under The Influence
===================

Under the Influence is a web application developed to help track the influence of lobbying over politics. The project is commissioned by Spinwatch and Unlock Democracy with additional funding from Greenpeace. In addition to the application improving their ability to research and campaign we hope it will also be a tool for the general public to explore who influences our representatives

Installation
------------
 * Install Neo4j
 
 * Install Mongo-DB
 
 * Install Elasticsearch
 
 * Install Mongo-Connector <br>
 [Follow these instructions for Mongo-Connector installation](https://github.com/10gen-labs/mongo-connector). <br>
 [And these instructions configuring it for Elasticsearch](https://github.com/10gen-labs/mongo-connector/wiki/Usage%20with%20ElasticSearch).<br>

 * Fetch this repo and all submodules:

   ```
   git clone --recursive https://github.com/spudmind/spud.git
   ```
 * Install the required python packages with:

   ```
   pip install -r requirements.txt
   ```
 * [Follow these instructions for building MITIE as a shared library](https://github.com/mit-nlp/MITIE#using-mitie). For me, this involved running the following:

   ```
   cd utils/mitie
   make MITIE-models
   cd mitielib
   make
   ```
