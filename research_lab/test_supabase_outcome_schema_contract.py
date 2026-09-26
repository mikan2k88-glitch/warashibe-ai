from research_lab.supabase_outcome_schema_contract import assess


def main():
    columns = [
        {"column_name": "id", "data_type": "bigint", "column_default": None},
        {"column_name": "opportunity_key", "data_type": "text", "column_default": None},
        {"column_name": "sold", "data_type": "boolean", "column_default": None},
        {"column_name": "days_to_outcome", "data_type": "integer", "column_default": None},
    ]
    result = assess(columns)
    assert result["write_ready"] is False
    assert result["issues"] == ["id_has_no_default"]
    columns[0]["column_default"] = "nextval('warashibe_sale_outcomes_id_seq'::regclass)"
    assert assess(columns) == {"write_ready": True, "issues": []}
    print("Supabase outcome schema preflight: PASS")


if __name__ == "__main__":
    main()
