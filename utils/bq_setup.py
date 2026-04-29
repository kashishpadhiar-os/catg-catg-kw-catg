import time
import copy
from typing import Optional, Union, List, Dict, Tuple

import numpy as np
import pandas as pd
from google.cloud import bigquery

from config import BQ_PROJECT_ID

SINGLE_VALUE_COLLECTION_TYPES = (list, tuple, set, frozenset, pd.Series, np.ndarray)
_BQ_COST_PER_TB = 5


def _bq_to_query_parameters(simple_query_params):
    from google.cloud.bigquery.dbapi._helpers import to_query_parameters

    def _transform(val):
        if isinstance(val, SINGLE_VALUE_COLLECTION_TYPES):
            if not isinstance(val, (list, tuple)):
                val = list(sorted(val))
            if any(isinstance(v, np.float64) for v in val):
                val = list(map(float, val))
            elif any(isinstance(v, np.int64) for v in val):
                val = list(map(int, val))
        return val

    return to_query_parameters(
        {k: _transform(v) for k, v in simple_query_params.items()}, parameter_types={}
    )


def bq_query(
    query: str,
    simple_query_params: Optional[Dict[str, Union[str, int]]] = None,
    *,
    query_params: Optional[List] = None,
    max_cost: float = 1.0,
    use_query_cache: bool = True,
) -> pd.DataFrame:
    start_time = time.time()
    client = bigquery.Client(project=BQ_PROJECT_ID)

    query_params = copy.deepcopy(query_params or [])
    if simple_query_params:
        query_params += _bq_to_query_parameters(simple_query_params)

    job_config = bigquery.QueryJobConfig()
    job_config.query_parameters = query_params
    job_config.use_query_cache = use_query_cache

    if max_cost and max_cost > 0:
        job_config.maximum_bytes_billed = int((max_cost / _BQ_COST_PER_TB) * 1000**4)

    print(f"  Starting BQ query...")
    job_result = client.query(query, job_config=job_config)
    result_df = job_result.to_dataframe(progress_bar_type="tqdm")

    cost_estimate = job_result.total_bytes_billed / (1000**4) * _BQ_COST_PER_TB
    run_time = round(time.time() - start_time)
    print(f"  BQ done: {len(result_df)} rows | cost ~${cost_estimate:.4f} | {run_time}s | cache_hit={job_result.cache_hit}")

    return result_df
