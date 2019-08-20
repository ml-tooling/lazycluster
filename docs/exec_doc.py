import importlib
import lazycluster.cluster.dask_cluster

gd = importlib.import_module('generate_docs')

generator = gd.MarkdownAPIGenerator('/lazycluster', 'https://github.com/ml-tooling/lazycluster.git')

module_body_str = generator.module2md(lazycluster.cluster.dask_cluster)

gd.to_md_file(module_body_str, 'cluster.dask_cluster')
