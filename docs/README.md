<!-- markdownlint-disable -->

# API Overview

## Modules

- [`lazycluster.cluster`](./lazycluster.cluster.md#module-lazyclustercluster)
- [`lazycluster.cluster.dask_cluster`](./lazycluster.cluster.dask_cluster.md#module-lazyclusterclusterdask_cluster): Module for conveniently managing a [DASK](http://distributed.dask.org) cluster.
- [`lazycluster.cluster.exceptions`](./lazycluster.cluster.exceptions.md#module-lazyclusterclusterexceptions): Exception module for cluster classes.
- [`lazycluster.cluster.hyperopt_cluster`](./lazycluster.cluster.hyperopt_cluster.md#module-lazyclusterclusterhyperopt_cluster): Module for conveniently managing a [Hyperopt](https://github.com/hyperopt/hyperopt) cluster.
- [`lazycluster.cluster.runtime_cluster`](./lazycluster.cluster.runtime_cluster.md#module-lazyclusterclusterruntime_cluster): Module comprising the abstract RuntimeCluster class with its related `launcher strategy` classes.
- [`lazycluster.exceptions`](./lazycluster.exceptions.md#module-lazyclusterexceptions): Exception module.
- [`lazycluster.runtime_mgmt`](./lazycluster.runtime_mgmt.md#module-lazyclusterruntime_mgmt): Runtime management module. This module contains convenient classes for working with `Runtimes` and `RuntimeTasks`.
- [`lazycluster.runtimes`](./lazycluster.runtimes.md#module-lazyclusterruntimes): Runtimes module.
- [`lazycluster.scripts`](./lazycluster.scripts.md#module-lazyclusterscripts)
- [`lazycluster.scripts.cli_handler`](./lazycluster.scripts.cli_handler.md#module-lazyclusterscriptscli_handler)
- [`lazycluster.settings`](./lazycluster.settings.md#module-lazyclustersettings): Contains setting parameters for the library.
- [`lazycluster.utils`](./lazycluster.utils.md#module-lazyclusterutils)

## Classes

- [`dask_cluster.DaskCluster`](./lazycluster.cluster.dask_cluster.md#class-daskcluster): Convenient class for launching a Dask cluster in a `RuntimeGroup`.
- [`dask_cluster.LocalMasterLauncher`](./lazycluster.cluster.dask_cluster.md#class-localmasterlauncher): Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited methods and attributes.
- [`dask_cluster.RoundRobinLauncher`](./lazycluster.cluster.dask_cluster.md#class-roundrobinlauncher): WorkerLauncher implementation for launching DASK workers in a round robin manner. See its documentation to get a list of the inherited methods and attributes.
- [`exceptions.MasterStartError`](./lazycluster.cluster.exceptions.md#class-masterstarterror): Error indicating that the cluster master instance could not be started successfully.
- [`hyperopt_cluster.HyperoptCluster`](./lazycluster.cluster.hyperopt_cluster.md#class-hyperoptcluster): Convenient class for launching a Hyperopt cluster in a `RuntimeGroup`.
- [`hyperopt_cluster.LocalMongoLauncher`](./lazycluster.cluster.hyperopt_cluster.md#class-localmongolauncher): Concrete implementation of the `MasterLauncher` interface. See its documentation to get a list of the inherited methods and attributes.
- [`hyperopt_cluster.MongoLauncher`](./lazycluster.cluster.hyperopt_cluster.md#class-mongolauncher): Abstract implementation of the `MasterLauncher` interface used to implement a concrete launch strategy for mongodb instance used in hyperopt.
- [`hyperopt_cluster.RoundRobinLauncher`](./lazycluster.cluster.hyperopt_cluster.md#class-roundrobinlauncher): Concrete WorkerLauncher implementation for launching hyperopt workers in a round robin manner.
- [`runtime_cluster.MasterLauncher`](./lazycluster.cluster.runtime_cluster.md#class-masterlauncher): Abstract class for implementing the strategy for launching the master instance of the cluster.
- [`runtime_cluster.MasterWorkerCluster`](./lazycluster.cluster.runtime_cluster.md#class-masterworkercluster): Class for clusters following a master-worker architecture.
- [`runtime_cluster.RuntimeCluster`](./lazycluster.cluster.runtime_cluster.md#class-runtimecluster): Abstract cluster class.
- [`runtime_cluster.WorkerLauncher`](./lazycluster.cluster.runtime_cluster.md#class-workerlauncher): Abstract class for implementing the strategy for launching worker instances within a RuntimeGroup.
- [`exceptions.InvalidRuntimeError`](./lazycluster.exceptions.md#class-invalidruntimeerror): Error indicating that a `Runtime` can not be instantiated properly.
- [`exceptions.LazyclusterError`](./lazycluster.exceptions.md#class-lazyclustererror): Basic exception class for `lazycluster` library errors.
- [`exceptions.NoPortsLeftError`](./lazycluster.exceptions.md#class-noportslefterror): Error indicating that there are no more ports left from the given port list.
- [`exceptions.NoRuntimesDetectedError`](./lazycluster.exceptions.md#class-noruntimesdetectederror): Error indicating that no `Runtime` could be detcted automatically by a `RuntimeManager` for example.
- [`exceptions.PathCreationError`](./lazycluster.exceptions.md#class-pathcreationerror): Error indicating that a given path could not be created.
- [`exceptions.PortInUseError`](./lazycluster.exceptions.md#class-portinuseerror): Error indicating that a port is already in use in a `RuntimeGroup` or on the local machine.
- [`exceptions.TaskExecutionError`](./lazycluster.exceptions.md#class-taskexecutionerror): This error relates to exceptions occured during RuntimeTask execution.
- [`runtime_mgmt.RuntimeGroup`](./lazycluster.runtime_mgmt.md#class-runtimegroup): A `RuntimeGroup` is the representation of logically related `Runtimes`.
- [`runtime_mgmt.RuntimeManager`](./lazycluster.runtime_mgmt.md#class-runtimemanager): The `RuntimeManager` can be used for a simplified resource management.
- [`runtimes.Runtime`](./lazycluster.runtimes.md#class-runtime): A `Runtime` is the logical representation of a remote host.
- [`runtimes.RuntimeTask`](./lazycluster.runtimes.md#class-runtimetask): This class provides the functionality for executing a sequence of elementary operations over ssh.
- [`utils.Environment`](./lazycluster.utils.md#class-environment): This class contains environment variables.
- [`utils.ExecutionFileLogUtil`](./lazycluster.utils.md#class-executionfilelogutil): Generic class used to write log files.
- [`utils.Timestamp`](./lazycluster.utils.md#class-timestamp): Custom Timestamp class with convenient methods.

## Functions

- No functions


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
