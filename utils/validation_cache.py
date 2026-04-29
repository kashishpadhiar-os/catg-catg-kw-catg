import os
import re
import unicodedata

import pandas as pd

from config import CACHE_DIR


def _dedupe_cache(df):
    # To check if there's any duplication between new incoming pairs to the one's in validation cache
    # Any pair with 'MANUAL' as source takes priority over 'LLM
    df = df.copy()
    df['_sort'] = df['source'].apply(lambda x: 1 if x == 'MANUAL' else 0)
    df = df.sort_values('_sort').drop_duplicates(
        subset=['category_concat', 'similar_category'], keep='last'
    ).drop(columns=['_sort'])
    return df


def _canonical_path(s):
    # Standardize a category path with 'MANUAL' entry so everything matches and can be found correctly in the cache.
    if not isinstance(s, str):
        return s
    s = unicodedata.normalize('NFC', s)
    s = re.sub(r'[\u200B-\u200D\uFEFF]', '', s)
    s = s.lower().strip()
    s = re.sub(r'\s*>\s*', '>', s)
    s = re.sub(r'\s+', ' ', s)
    parts = [p for p in s.split('>') if p]
    return '>'.join(parts)


def _normalise_manual_rows(cache_df):
    # Apply _canonical_path function to MANUAL rows only. LLM rows are already meeting the standard format
    if cache_df.empty or 'source' not in cache_df.columns:
        return cache_df
    manual_mask = cache_df['source'] == 'MANUAL'
    if not manual_mask.any():
        return cache_df
    n_before = manual_mask.sum()
    before_cc = cache_df.loc[manual_mask, 'category_concat'].copy()
    before_sc = cache_df.loc[manual_mask, 'similar_category'].copy()
    cache_df.loc[manual_mask, 'category_concat'] = before_cc.apply(_canonical_path)
    cache_df.loc[manual_mask, 'similar_category'] = before_sc.apply(_canonical_path)
    n_changed = int(
        (cache_df.loc[manual_mask, 'category_concat'] != before_cc).sum()
        + (cache_df.loc[manual_mask, 'similar_category'] != before_sc).sum()
    )
    if n_changed:
        print(f"  Normalised {n_changed} MANUAL value(s) across {n_before} manual row(s)")
    return cache_df


def load_cache(client_id):
    # Load validation cache as per the respective client & clean up
    cache_path = os.path.join(CACHE_DIR, f"validation_cache_{client_id}.tsv")
    if os.path.exists(cache_path):
        cache_df = pd.read_csv(cache_path, sep='\t')
        if 'source' not in cache_df.columns:
            cache_df['source'] = 'LLM'
        flag_map = {'APPROVE': 'RELEVANT', 'REJECT': 'IRRELEVANT'}
        if 'llm_flag' in cache_df.columns:
            cache_df['llm_flag'] = cache_df['llm_flag'].replace(flag_map)
        cache_df = _normalise_manual_rows(cache_df)
        print(f"  Loaded cache: {len(cache_df)} pairs from {cache_path}")
        return cache_df
    print(f"  No existing cache found at {cache_path}")
    return pd.DataFrame(columns=['category_concat', 'similar_category', 'llm_flag', 'llm_reason', 'source'])


def save_cache(new_validations_df, cache_df, client_id):
    # Merges validation cache file with newly validated pairs, removes duplicates with a priority rule
    """Append new validated pairs, dedupe (MANUAL > LLM), write to disk."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, f"validation_cache_{client_id}.tsv")

    new_validations_df = new_validations_df.copy()
    if 'source' not in new_validations_df.columns:
        new_validations_df['source'] = 'LLM'

    combined = pd.concat([cache_df, new_validations_df], ignore_index=True)
    combined = _dedupe_cache(combined)

    combined.to_csv(cache_path, sep='\t', index=False)
    print(f"  Cache saved: {len(combined)} total pairs at {cache_path}")
    return combined


def add_manual_entry(client_id, category_concat, similar_category, llm_flag, llm_reason=None):
    # Insert 'MANUAL' entry for override in the cache
    cache_df = load_cache(client_id)
    category_concat = _canonical_path(category_concat)
    similar_category = _canonical_path(similar_category)
    new_entry = pd.DataFrame([{
        'category_concat': category_concat,
        'similar_category': similar_category,
        'llm_reason': llm_reason,
        'llm_flag': llm_flag,
        'source': 'MANUAL',
    }])
    save_cache(new_entry, cache_df, client_id)
    print(f"  Manual entry added: {category_concat} ↔ {similar_category} = {llm_flag}")
