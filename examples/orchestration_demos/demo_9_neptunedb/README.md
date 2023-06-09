# Goal

Demonstrate how to use Amazon Neptune as a graph tracer.

Files

---

* deployment.py: Implementation using Neptune as a backend to record the graph
---

## Prerequisites  

1.  Provision and setup a Neptune Database on the AWS Management Console (serverless or with a chosen instance type).


## How to run the example


Run the orchestration pipeline
```bash
python deployment.py 
```

Neptune DB can be visualized through the SageMaker NeptuneDB Workbench. When using the magics (%%gremlin) you can key in the following to visualize.

```python
%%gremlin -p v,ine,outv,oute,inv,oute,inv
    g.V().inE().outV().outE().inV().outE().inV().path() 
```

