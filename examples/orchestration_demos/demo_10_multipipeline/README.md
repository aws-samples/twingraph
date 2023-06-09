# Goal

Demonstrate how to run multiple pipelines, and record them all on a unified graph.

Files

---

* pipelineA.py: Implementation of a selection of tasks to be traced within a TinkerGraph database
* pipelineB.py: Implementation of a second selection of tasks to be traced within a TinkerGraph database
* run.sh: A shell script that will run the both pipelines simultaneously
---


## How to run the example

Ensure that you have the flag 'multipipeline=True' on the pipelines to avoid clearing the graph on each pipeline.

Run the orchestration pipelines together with the unified shell scripts:

```bash
./run.sh
```


