import os


def load_sql(filename, client_id, params, inputs_dir):
    # Load a BigQuery SQL file, add client_id and columns
    
    sql_path = os.path.join(inputs_dir, filename)
    with open(sql_path) as f:
        sql = f.read().format(client_id=client_id)
    catg_cols = params["catg_cols"]
    sql_columns = ",\n".join(
        f"lower(merchandise_product_dimensions.{c}) as {c}" for c in catg_cols
    )
    sql = sql.replace("__CATEGORY_COLUMNS__", sql_columns)
    sql = sql.replace("__EXTRA_FILTERS__", params.get("sql_extra_filters", ""))
    return sql
