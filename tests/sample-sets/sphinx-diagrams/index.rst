sphinx-diagrams
===============

.. diagrams::

    from diagrams import Cluster
    from diagrams.k8s.compute import Deployment
    from sphinx_diagrams import SphinxDiagram

    with SphinxDiagram(title="GKE"):
        with Cluster("GCP Project"):
            Deployment("Primary Cluster")

----

.. diagrams::

    from diagrams import Diagram
    from diagrams.aws.compute import EC2
    from diagrams.aws.database import RDS
    from diagrams.aws.network import ELB
    from sphinx_diagrams import SphinxDiagram

    with SphinxDiagram(title="GKE"):
        ELB("lb") >> [EC2("worker1"),
                      EC2("worker2"),
                      EC2("worker3"),
                      EC2("worker4"),
                      EC2("worker5")] >> RDS("events")

----

.. diagrams::

    from diagrams import Cluster, Diagram
    from diagrams.aws.compute import ECS, EKS, Lambda
    from diagrams.aws.database import Redshift
    from diagrams.aws.integration import SQS
    from diagrams.aws.storage import S3
    from sphinx_diagrams import SphinxDiagram

    with SphinxDiagram(title="GKE"):
        with Cluster("Event Flows"):
            with Cluster("Event Workers"):
                workers = [ECS("worker1"),
                           ECS("worker2"),
                           ECS("worker3")]

            queue = SQS("event queue")

            with Cluster("Processing"):
                handlers = [Lambda("proc1"),
                            Lambda("proc2"),
                            Lambda("proc3")]

        store = S3("events store")
        dw = Redshift("analytics")

        workers >> queue >> handlers
        handlers >> store
        handlers >> dw
