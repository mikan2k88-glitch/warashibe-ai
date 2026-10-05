"""Read-only presentation from saved shadow records; no invented live evidence."""
from research_lab.promotion_gate import evaluate_promotion
from research_lab.evidence_integrity import source_url


def candidate_summary(repository, *, as_of):
    rows = repository.load()
    row = max(rows, key=lambda r: (r.get('observed_at', ''), r['shadow_candidate_id'])) if rows else None
    gate = {'target_total_acquisition_cost_jpy_max': 2200, 'target_net_profit_jpy_min': 300}
    result = {
        'state': 'not_observed', 'headline': '保存済み候補はありません',
        'message': '候補を保存し、後日の観測と証拠を追加してください。',
        'item_name': '未観測', 'decision': 'HOLD — 証拠未確認', 'go_to_p3': False,
        'source_url': '', 'sale_comp_url': '', 'next_search_gate': gate,
        'purchase_price_jpy': None, 'expected_sale_price_jpy': None,
        'expected_net_profit_jpy': None, 'expected_margin_rate': None,
        'estimated_days_to_sell': None, 'capital_velocity_jpy_per_day': None,
        'economics': {'remote_purchase_total_cost_jpy': None, 'sale_net_after_fee_and_shipping_jpy': None},
        'observed_at': None, 'evidence_refs': [], 'hypothetical': True,
    }
    if row is None:
        return result
    decision = evaluate_promotion(row, as_of=as_of)
    sale = next((e for e in row.get('evidence', []) if e.get('kind') == 'sold_price'), {})
    result.update({
        'state': 'shadow_observed', 'headline': '保存済みShadow候補（仮想評価）',
        'message': '判定理由: ' + (', '.join(decision['reasons']) or 'Promotion Gate通過・Human Review待ち'),
        'item_name': row.get('product_name') or row.get('candidate_id'),
        'shadow_candidate_id': row['shadow_candidate_id'], 'candidate_id': row.get('candidate_id'),
        'decision': 'Human Review準備済み' if decision['human_review_ready'] else 'HOLD',
        'go_to_p3': decision['human_review_ready'],
        'source_url': row['source_url'] if source_url(row.get('source_url')) else '',
        'sale_comp_url': sale.get('source_url') if source_url(sale.get('source_url')) else '',
        'purchase_price_jpy': row.get('acquisition_price'),
        'expected_sale_price_jpy': row.get('expected_sale_price'),
        'expected_net_profit_jpy': row.get('expected_net_profit'),
        'expected_margin_rate': row.get('expected_roi'),
        'estimated_days_to_sell': row.get('estimated_sell_days'),
        'observed_at': row.get('latest_observation', {}).get('observed_at', row.get('observed_at')),
        'evidence_refs': row.get('evidence_refs', []), 'promotion': decision,
        'economics': {'remote_purchase_total_cost_jpy': row.get('total_acquisition_cost'),
                      'sale_net_after_fee_and_shipping_jpy': row.get('expected_sale_price', 0) - row.get('expected_selling_fee', 0) - row.get('expected_outbound_shipping', 0)},
    })
    return result


def runner_evidence(*, as_of):
    """An explicitly configured local runner snapshot proves only P1 execution."""
    import json
    import os
    from pathlib import Path
    from datetime import timedelta
    from research_lab.product_dd_input_gate import _utc_time
    path = os.environ.get('WARASHIBE_RUNNER_SNAPSHOT')
    expected = os.environ.get('WARASHIBE_EXPECTED_HEAD_SHA')
    result = {'status': 'not_verified', 'observed_at': None, 'head_sha': None, 'source': None}
    if not path or not expected:
        return result
    try:
        row = json.loads(Path(path).read_text(encoding='utf-8'))
        at, now = _utc_time(row.get('generated_at')), _utc_time(as_of)
        checks = row.get('checks')
        if (at is None or now is None or at > now or now - at > timedelta(days=1)
                or row.get('head_sha') != expected or row.get('status') != 'passed'
                or row.get('profile') != 'build' or row.get('selected_priority') is None
                or row.get('human_gate_preserved') is not True
                or row.get('external_execution_authorized') is not False
                or not isinstance(checks, list) or not checks
                or any(not isinstance(c, dict) or c.get('returncode') != 0 for c in checks)):
            return result
        return {'status': 'observed_success', 'observed_at': row['generated_at'],
                'head_sha': expected, 'source': 'configured_runner_snapshot'}
    except (OSError, ValueError, TypeError, AttributeError):
        return result


def escape_html(value):
    """Escape saved data on HTML only; JSON remains machine-readable."""
    from html import escape
    if isinstance(value, str):
        return escape(value, quote=True)
    if isinstance(value, dict):
        return {k: escape_html(v) for k, v in value.items()}
    if isinstance(value, list):
        return [escape_html(v) for v in value]
    return value
