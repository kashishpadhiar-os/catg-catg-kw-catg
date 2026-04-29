DEFAULT_GAE_PROJECT = "prj-onlinesales-vertexai"
BQ_PROJECT_ID = "prj-onlinesales-prod-01"

# Universal Sentence Encoder
USE_MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-multilingual/3"
USE_MODEL_GCS_PATH = "gs://os-performance-dev-bucket/tmp_similar_catg_opc/ml_models/use_multilingual_3"

# Validation cache file location
CACHE_DIR = "./validation_cache/"

# LLM model & pricing
MODEL_CASCADE = [
    "gemini-3.1-flash-lite-preview",
    "gemini-2.5-flash-lite",
]

DEFAULT_MODEL_ID = "gemini-3.1-flash-lite-preview"

MODEL_PRICING = {
    "gemini-3.1-flash-lite-preview": {"input": 0.25, "output": 1.5},
    "gemini-2.5-flash-lite": {"input": 0.1, "output": 0.4},
}

MAX_CANDIDATES_PER_BATCH = 25

# Threshold auto-tuning
MAX_THRESHOLD = 0.70
THRESHOLD_STEP = 0.05

# Category mapping parameters
CATG_PIPELINE_PARAMS = {
    "chunk_size": 1000,
    "leaf_catg_cnt": 1,
    "top_skus_cnt": 500,
    "n_trees": 512,
    "n_neighbors": 10,
    "min_score_threshold": 0.5,
    "catg_batch_limit": 1000,
    "catg_cols": [f"category_l{i}" for i in range(1, 9)],
    "embedding_order": "name_first",
}

# Category mapping - OPC parameters
OPC_PIPELINE_PARAMS = {
    "chunk_size": 1000,
    "leaf_catg_cnt": 1,
    "top_skus_cnt": 250,
    "n_trees": 256,
    "n_neighbors": 10,
    "min_score_threshold": 0.5,
    "catg_batch_limit": 1000,
    "catg_cols": [f"opc_{i}" for i in range(1, 9)],
    "embedding_order": "leaf_first",
    "sql_extra_filters": "and lower(merchandise_product_dimensions.opc_1) not like '%https%'",
}

# Define mapping to specify if a client - CATG or OPC
CLIENT_PIPELINE_TYPE = {
    "395539": "opc",
}

PIPELINE_PARAMS = {
    "catg": CATG_PIPELINE_PARAMS,
    "opc": OPC_PIPELINE_PARAMS,
}

# S3 paths
S3_CATG_MODEL_OUTPUT = (
    "s3://os-reporting-dev-bucket/search_relevancy_data/prod/"
    "similar_category_category_mapping/output/tmp_model_output/{client_id}/"
    "similar_catg_catg_mapping_{client_id}.tsv"
)

S3_CATG_VALIDATION_CACHE = (
    "s3://os-reporting-dev-buckets/search_relevancy_data/prod/"
    "similar_category_category_mapping/output/tmp_validation_cache/"
    "validation_cache_{client_id}.tsv"
)

S3_OPC_MODEL_OUTPUT = (
    "s3://os-reporting-dev-bucket/search_relevancy_data/prod/"
    "similar_opc_opc_mapping/output/tmp_model_output/{client_id}/"
    "similar_opc_opc_mapping_{client_id}.tsv"
)

S3_OPC_VALIDATION_CACHE = (
    "s3://os-reporting-dev-buckets/search_relevancy_data/prod/"
    "similar_opc_opc_mapping/output/tmp_validation_cache/"
    "validation_cache_{client_id}.tsv"
)

# Ad-serving constants
SKU_ID_CONSTANT = 666666
SOURCE_CONSTANT = "manual"

# Transformation parameters — Category variant 
CATG_TRANSFORM_PARAMS = {
    "kw_join_col": "actual_keyword",
    "kw_group_cols": ["keyword", "actual_keyword"],
    "word_cnt_max": 1,
    "blacklist_source": "file",
    "min_score_threshold": 0.65,
    "catg_cols": [f"category_l{i}" for i in range(1, 9)],
    "output_file_template": "manual_keyword_category_mapping_{client_id}.tsv",
    "s3_input_base": (
        "s3://os-reporting-dev-bucket/search_relevancy_data/prod/"
        "similar_category_category_mapping/input/{client_id}"
    ),
    "s3_key_catg_input": (
        "s3://os-reporting-dev-bucket/search_relevancy_data/prod/"
        "similar_category_category_mapping/input/{client_id}/"
        "keyword_to_category_mapping_{client_id}.tsv"
    ),
    "s3_output": (
        "s3://os-reporting-dev-buckets/search_relevancy_data/prod/"
        "manual_keyword_category_mapping/{client_id}/"
        "manual_keyword_category_mapping_{client_id}.tsv"
    ),
    "s3_model_output": S3_CATG_MODEL_OUTPUT,
}

# Transformation parameters — OPC variant
OPC_TRANSFORM_PARAMS = {
    "kw_join_col": "keyword",
    "kw_group_cols": ["keyword"],
    "word_cnt_max": 1,
    "blacklist_source": "athena",
    "min_score_threshold": 0.85,
    "catg_cols": [f"opc_{i}" for i in range(1, 9)],
    "output_file_template": "manual_keyword_opc_category_mapping_{client_id}.tsv",
    "s3_input_base": (
        "s3://os-reporting-dev-bucket/search_relevancy_data/prod/"
        "similar_category_category_mapping/input/{client_id}"
    ),
    "s3_key_catg_input": (
        "s3://os-performance-dev-bucket/keyword_opc_workflows/similar_opc_opc_mapping/input/"
        "{client_id}/keyword_to_opc_mapping_{client_id}.tsv"
    ),
    "s3_output": (
        "s3://os-performance-dev-bucket/prod/tmp_keyword_opc_manual_mappings/"
        "{client_id}/manual_keyword_opc_category_mapping_{client_id}.tsv"
    ),
    "s3_model_output": S3_OPC_MODEL_OUTPUT,
}

TRANSFORM_PARAMS = {
    "catg": CATG_TRANSFORM_PARAMS,
    "opc": OPC_TRANSFORM_PARAMS,
}

# Shared transformation constants
FLAG_WEIGHT = {"RELEVANT": 0.75, "LOOSELY_RELEVANT": 0.25}
ELIGIBLE_WEIGHT = {1: 0.75, 0: 0.25}